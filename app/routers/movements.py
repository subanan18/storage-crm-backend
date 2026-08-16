from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/movements", tags=["movements"])


@router.get("", response_model=list[schemas.MovementOut])
def list_movements(item_id: str | None = None, limit: int = 200, db: Session = Depends(get_db)):
    query = db.query(models.Movement)
    if item_id:
        query = query.filter(models.Movement.item_id == item_id)
    return query.order_by(models.Movement.timestamp.desc()).limit(limit).all()
