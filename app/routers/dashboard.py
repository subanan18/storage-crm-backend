from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

FLAGGED_STATUSES = {"Missing", "Damaged"}
IN_TRANSIT_STATUSES = {
    "In transit to customer", "In transit to warehouse", "Picked", "Reserved for delivery"
}


@router.get("/stats", response_model=schemas.DashboardStats)
def get_stats(db: Session = Depends(get_db)):
    items = db.query(models.Item).all()
    status_breakdown: dict[str, int] = {}
    for item in items:
        status_breakdown[item.status] = status_breakdown.get(item.status, 0) + 1

    return schemas.DashboardStats(
        companies=db.query(models.Company).count(),
        active_projects=db.query(models.Project).filter(models.Project.status == "Active").count(),
        stored=sum(1 for i in items if i.status == "Stored"),
        in_transit=sum(1 for i in items if i.status in IN_TRANSIT_STATUSES),
        flagged=sum(1 for i in items if i.status in FLAGGED_STATUSES),
        pending_retrievals=db.query(models.Retrieval).filter(models.Retrieval.status != "Delivered").count(),
        status_breakdown=status_breakdown,
    )
