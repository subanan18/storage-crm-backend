from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[schemas.ProjectOut])
def list_projects(company_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Project)
    if company_id:
        q = q.filter(models.Project.company_id == company_id)
    return q.order_by(models.Project.created_at.desc()).all()


@router.post("", response_model=schemas.ProjectOut, status_code=201)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    if not db.get(models.Company, payload.company_id):
        raise HTTPException(404, "Company not found")
    project = models.Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    return project


@router.patch("/{project_id}", response_model=schemas.ProjectOut)
def update_project(project_id: str, payload: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    db.delete(project)
    db.commit()
