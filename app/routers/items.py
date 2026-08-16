from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/items", tags=["items"])


def _log_movement(db: Session, item_id: str, from_loc: str | None, to_loc: str | None,
                   type_: str, status: str, note: str | None = None):
    movement = models.Movement(
        item_id=item_id, from_location=from_loc, to_location=to_loc,
        type=type_, status=status, note=note or "",
    )
    db.add(movement)


@router.get("", response_model=list[schemas.ItemOut])
def list_items(
    q: str | None = None,
    project_id: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Item)
    if project_id:
        query = query.filter(models.Item.project_id == project_id)
    if status:
        query = query.filter(models.Item.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            models.Item.name.ilike(like),
            models.Item.category.ilike(like),
            models.Item.location_code.ilike(like),
            models.Item.container_id.ilike(like),
            models.Item.status.ilike(like),
        ))
    return query.order_by(models.Item.created_at.desc()).all()


@router.post("", response_model=schemas.ItemOut, status_code=201)
def register_item(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    project = db.get(models.Project, payload.project_id)
    if not project:
        raise HTTPException(404, "Storage project not found")

    location_code = "-".join(filter(None, [
        payload.warehouse, payload.zone, payload.aisle, payload.rack, payload.level, payload.position
    ])) or "Unassigned"

    data = payload.model_dump(exclude={
        "collected_from", "warehouse", "zone", "aisle", "rack", "level", "position"
    })
    item = models.Item(**data, location_code=location_code, status="Received")
    db.add(item)
    db.flush()  # get item.id before commit

    _log_movement(
        db, item.id, payload.collected_from or "Collection point", location_code,
        "Intake", "Received", "Item registered."
    )
    item.status = "Stored"
    _log_movement(
        db, item.id, location_code, location_code,
        "Shelved", "Stored", "Assigned to storage location."
    )

    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=schemas.ItemOut)
def get_item(item_id: str, db: Session = Depends(get_db)):
    item = db.get(models.Item, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item


@router.patch("/{item_id}", response_model=schemas.ItemOut)
def update_item(item_id: str, payload: schemas.ItemUpdate, db: Session = Depends(get_db)):
    item = db.get(models.Item, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.post("/{item_id}/status", response_model=schemas.ItemOut)
def change_status(item_id: str, payload: schemas.ItemStatusChange, db: Session = Depends(get_db)):
    item = db.get(models.Item, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    if payload.status not in schemas.ITEM_STATUSES:
        raise HTTPException(400, f"Unknown status. Must be one of: {schemas.ITEM_STATUSES}")

    item.status = payload.status
    _log_movement(
        db, item.id, item.location_code, item.location_code,
        "Status update", payload.status, payload.note or f"Status changed to {payload.status}."
    )
    db.commit()
    db.refresh(item)
    return item


@router.post("/{item_id}/relocate", response_model=schemas.ItemOut)
def relocate_item(item_id: str, payload: schemas.ItemRelocate, db: Session = Depends(get_db)):
    item = db.get(models.Item, item_id)
    if not item:
        raise HTTPException(404, "Item not found")

    old_location = item.location_code
    item.location_code = payload.location_code
    _log_movement(
        db, item.id, old_location, payload.location_code,
        "Relocation", item.status, payload.note or "Item relocated."
    )
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: str, db: Session = Depends(get_db)):
    item = db.get(models.Item, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    db.delete(item)
    db.commit()
