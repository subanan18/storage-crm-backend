from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.routers.items import _log_movement

router = APIRouter(prefix="/retrievals", tags=["retrievals"])

# Status each item takes on as the retrieval advances to this stage
ITEM_STATUS_FOR_STAGE = {
    "Picking": "Reserved for delivery",
    "Picked": "Picked",
    "Out for delivery": "In transit to customer",
    "Delivered": "Delivered",
}


def _serialize(retrieval: models.Retrieval) -> schemas.RetrievalOut:
    return schemas.RetrievalOut.from_orm_with_items(retrieval)


@router.get("", response_model=list[schemas.RetrievalOut])
def list_retrievals(project_id: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Retrieval)
    if project_id:
        query = query.filter(models.Retrieval.project_id == project_id)
    retrievals = query.order_by(models.Retrieval.requested_at.desc()).all()
    return [_serialize(r) for r in retrievals]


@router.post("", response_model=schemas.RetrievalOut, status_code=201)
def create_retrieval(payload: schemas.RetrievalCreate, db: Session = Depends(get_db)):
    project = db.get(models.Project, payload.project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    items = db.query(models.Item).filter(models.Item.id.in_(payload.item_ids)).all()
    if len(items) != len(payload.item_ids):
        raise HTTPException(404, "One or more items not found")
    for item in items:
        if item.status != "Stored":
            raise HTTPException(400, f"Item '{item.name}' is not currently Stored and cannot be reserved.")

    retrieval = models.Retrieval(project_id=payload.project_id, status="Requested", items=items)
    db.add(retrieval)
    db.flush()

    for item in items:
        item.status = "Reserved for delivery"
        _log_movement(db, item.id, item.location_code, "Reserved", "Reserved for delivery",
                      "Retrieval request created.")

    db.commit()
    db.refresh(retrieval)
    return _serialize(retrieval)


@router.get("/{retrieval_id}", response_model=schemas.RetrievalOut)
def get_retrieval(retrieval_id: str, db: Session = Depends(get_db)):
    retrieval = db.get(models.Retrieval, retrieval_id)
    if not retrieval:
        raise HTTPException(404, "Retrieval not found")
    return _serialize(retrieval)


@router.post("/{retrieval_id}/advance", response_model=schemas.RetrievalOut)
def advance_retrieval(retrieval_id: str, payload: schemas.RetrievalAdvance, db: Session = Depends(get_db)):
    retrieval = db.get(models.Retrieval, retrieval_id)
    if not retrieval:
        raise HTTPException(404, "Retrieval not found")

    order = schemas.RETRIEVAL_STAGES
    current_idx = order.index(retrieval.status)
    if current_idx == len(order) - 1:
        raise HTTPException(400, "Retrieval is already Delivered")

    next_stage = order[current_idx + 1]
    retrieval.status = next_stage

    if next_stage == "Delivered":
        retrieval.delivered_at = datetime.utcnow()
        retrieval.proof_name = payload.proof_name or retrieval.proof_name
        retrieval.delivery_note = payload.delivery_note or retrieval.delivery_note

    new_item_status = ITEM_STATUS_FOR_STAGE.get(next_stage)
    for item in retrieval.items:
        if new_item_status:
            item.status = new_item_status
        destination = "Customer" if next_stage == "Delivered" else item.location_code
        _log_movement(db, item.id, item.location_code, destination, "Retrieval",
                      new_item_status or next_stage, f"Retrieval advanced to {next_stage}.")

    db.commit()
    db.refresh(retrieval)
    return _serialize(retrieval)


@router.delete("/{retrieval_id}", status_code=204)
def delete_retrieval(retrieval_id: str, db: Session = Depends(get_db)):
    retrieval = db.get(models.Retrieval, retrieval_id)
    if not retrieval:
        raise HTTPException(404, "Retrieval not found")
    db.delete(retrieval)
    db.commit()
