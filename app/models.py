import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, Table
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


retrieval_items = Table(
    "retrieval_items",
    Base.metadata,
    Column("retrieval_id", String, ForeignKey("retrievals.id", ondelete="CASCADE"), primary_key=True),
    Column("item_id", String, ForeignKey("items.id", ondelete="CASCADE"), primary_key=True),
)


class Company(Base):
    __tablename__ = "companies"

    id = Column(String, primary_key=True, default=lambda: gen_id("CO"))
    name = Column(String, nullable=False)
    company_number = Column(String, nullable=True)
    contact_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    billing_address = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="company", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: gen_id("PRJ"))
    company_id = Column(String, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    collection_date = Column(String, nullable=True)
    expected_duration = Column(String, nullable=True)
    status = Column(String, default="Active")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="projects")
    items = relationship("Item", back_populates="project", cascade="all, delete-orphan")
    retrievals = relationship("Retrieval", back_populates="project", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True, default=lambda: gen_id("ITM"))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    container_id = Column(String, nullable=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    condition = Column(String, default="Good")
    condition_notes = Column(Text, nullable=True)
    estimated_value = Column(Float, nullable=True)
    fragile = Column(Boolean, default=False)
    handling = Column(String, nullable=True)
    location_code = Column(String, default="Unassigned")
    status = Column(String, default="Expected")
    photo_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="items")
    movements = relationship("Movement", back_populates="item", cascade="all, delete-orphan")
    retrievals = relationship("Retrieval", secondary=retrieval_items, back_populates="items")


class Movement(Base):
    __tablename__ = "movements"

    id = Column(String, primary_key=True, default=lambda: gen_id("MV"))
    item_id = Column(String, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    from_location = Column(String, nullable=True)
    to_location = Column(String, nullable=True)
    type = Column(String, nullable=True)
    status = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    item = relationship("Item", back_populates="movements")


class Retrieval(Base):
    __tablename__ = "retrievals"

    id = Column(String, primary_key=True, default=lambda: gen_id("RET"))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="Requested")
    requested_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    delivery_note = Column(Text, nullable=True)
    proof_name = Column(String, nullable=True)

    project = relationship("Project", back_populates="retrievals")
    items = relationship("Item", secondary=retrieval_items, back_populates="retrievals")
