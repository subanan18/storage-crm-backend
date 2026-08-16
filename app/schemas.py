from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict

ITEM_STATUSES = [
    "Expected", "Collected", "In transit to warehouse", "Received",
    "Inspection required", "Stored", "Reserved for delivery", "Picked",
    "In transit to customer", "Delivered", "Returned to storage",
    "Missing", "Damaged", "Disposed",
]

RETRIEVAL_STAGES = ["Requested", "Picking", "Picked", "Out for delivery", "Delivered"]


# ---------- Company ----------

class CompanyBase(BaseModel):
    name: str
    company_number: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    billing_address: Optional[str] = None
    industry: Optional[str] = None
    notes: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    company_number: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    billing_address: Optional[str] = None
    industry: Optional[str] = None
    notes: Optional[str] = None


class CompanyOut(CompanyBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


# ---------- Project ----------

class ProjectBase(BaseModel):
    company_id: str
    name: str
    reason: Optional[str] = None
    collection_date: Optional[str] = None
    expected_duration: Optional[str] = None
    status: Optional[str] = "Active"
    notes: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    reason: Optional[str] = None
    collection_date: Optional[str] = None
    expected_duration: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ProjectOut(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


# ---------- Item ----------

class ItemBase(BaseModel):
    project_id: str
    container_id: Optional[str] = None
    name: str
    category: Optional[str] = None
    quantity: int = 1
    condition: Optional[str] = "Good"
    condition_notes: Optional[str] = None
    estimated_value: Optional[float] = None
    fragile: bool = False
    handling: Optional[str] = None
    photo_url: Optional[str] = None


class ItemCreate(ItemBase):
    collected_from: Optional[str] = None
    warehouse: Optional[str] = None
    zone: Optional[str] = None
    aisle: Optional[str] = None
    rack: Optional[str] = None
    level: Optional[str] = None
    position: Optional[str] = None


class ItemUpdate(BaseModel):
    container_id: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    condition: Optional[str] = None
    condition_notes: Optional[str] = None
    estimated_value: Optional[float] = None
    fragile: Optional[bool] = None
    handling: Optional[str] = None
    photo_url: Optional[str] = None


class ItemStatusChange(BaseModel):
    status: str
    note: Optional[str] = None


class ItemRelocate(BaseModel):
    location_code: str
    note: Optional[str] = None


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    container_id: Optional[str] = None
    name: str
    category: Optional[str] = None
    quantity: int
    condition: Optional[str] = None
    condition_notes: Optional[str] = None
    estimated_value: Optional[float] = None
    fragile: bool
    handling: Optional[str] = None
    location_code: str
    status: str
    photo_url: Optional[str] = None
    created_at: datetime


# ---------- Movement ----------

class MovementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    item_id: str
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    note: Optional[str] = None
    timestamp: datetime


# ---------- Retrieval ----------

class RetrievalCreate(BaseModel):
    project_id: str
    item_ids: List[str]


class RetrievalAdvance(BaseModel):
    proof_name: Optional[str] = None
    delivery_note: Optional[str] = None


class RetrievalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    status: str
    requested_at: datetime
    delivered_at: Optional[datetime] = None
    delivery_note: Optional[str] = None
    proof_name: Optional[str] = None
    item_ids: List[str] = []

    @classmethod
    def from_orm_with_items(cls, retrieval):
        obj = cls.model_validate(retrieval)
        obj.item_ids = [item.id for item in retrieval.items]
        return obj


# ---------- Dashboard ----------

class DashboardStats(BaseModel):
    companies: int
    active_projects: int
    stored: int
    in_transit: int
    flagged: int
    pending_retrievals: int
    status_breakdown: dict
