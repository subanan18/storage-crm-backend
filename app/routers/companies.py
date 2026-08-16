from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[schemas.CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return db.query(models.Company).order_by(models.Company.created_at.desc()).all()


@router.post("", response_model=schemas.CompanyOut, status_code=201)
def create_company(payload: schemas.CompanyCreate, db: Session = Depends(get_db)):
    company = models.Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}", response_model=schemas.CompanyOut)
def get_company(company_id: str, db: Session = Depends(get_db)):
    company = db.get(models.Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    return company


@router.patch("/{company_id}", response_model=schemas.CompanyOut)
def update_company(company_id: str, payload: schemas.CompanyUpdate, db: Session = Depends(get_db)):
    company = db.get(models.Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: str, db: Session = Depends(get_db)):
    company = db.get(models.Company, company_id)
    if not company:
        raise HTTPException(404, "Company not found")
    db.delete(company)
    db.commit()
