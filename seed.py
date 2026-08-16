"""
Populate the database with the same sample data the frontend prototype
ships with (ABC Fashion Ltd / Croydon Shop Relocation), so the API and
frontend line up when you first connect them.

Run with:  python seed.py
"""
from app.database import SessionLocal, Base, engine
from app import models

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    if db.query(models.Company).count() > 0:
        print("Database already has data — skipping seed.")
    else:
        company = models.Company(
            name="ABC Fashion Ltd",
            company_number="07421356",
            contact_name="Priya Anand",
            email="priya@abcfashion.co.uk",
            phone="020 7946 0091",
            billing_address="14 Regent Street, London, W1B 5AA",
            industry="Retail",
            notes="Multi-site retailer, three shops across London.",
        )
        db.add(company)
        db.flush()

        project = models.Project(
            company_id=company.id,
            name="Croydon Shop Relocation",
            reason="Store refurbishment",
            collection_date="2026-08-15",
            expected_duration="3 months",
            status="Active",
            notes="Original site: Croydon High Street.",
        )
        db.add(project)
        db.flush()

        item1 = models.Item(
            project_id=project.id,
            container_id="BOX-000127",
            name="Samsung display monitor QM55B",
            category="Electronics",
            quantity=2,
            condition="Good",
            condition_notes="Small scratch on rear.",
            estimated_value=600,
            fragile=True,
            handling="Keep upright",
            location_code="WH-LON-01-C-05-R12-L03-P02",
            status="Stored",
        )
        item2 = models.Item(
            project_id=project.id,
            container_id="PAL-000058",
            name="Black reception desk",
            category="Furniture",
            quantity=1,
            condition="Good",
            estimated_value=350,
            fragile=False,
            location_code="WH-LON-01-C-05-R11-L01-P01",
            status="Stored",
        )
        db.add_all([item1, item2])
        db.flush()

        db.add_all([
            models.Movement(
                item_id=item1.id, from_location="Croydon High Street",
                to_location=item1.location_code, type="Intake", status="Stored",
                note="Received and shelved.",
            ),
            models.Movement(
                item_id=item2.id, from_location="Croydon High Street",
                to_location=item2.location_code, type="Intake", status="Stored",
                note="Received and shelved.",
            ),
        ])

        db.commit()
        print("Seed data created: 1 company, 1 project, 2 items.")
finally:
    db.close()
