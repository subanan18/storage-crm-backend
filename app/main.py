from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import companies, projects, items, movements, retrievals, dashboard, realtime

# Creates tables if they don't exist yet. For real schema changes going
# forward, use Alembic migrations instead (see alembic/ directory).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Depot — Storage & Asset Tracking API",
    description=(
        "Backend for the AI-powered managed storage and asset-tracking platform: "
        "companies, storage projects, items/containers, movement audit log, "
        "retrieval/delivery workflow, and realtime WebSocket updates."
    ),
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router)
app.include_router(projects.router)
app.include_router(items.router)
app.include_router(movements.router)
app.include_router(retrievals.router)
app.include_router(dashboard.router)
app.include_router(realtime.router)


@app.get("/", tags=["health"])
def health_check():
    return {
        "status": "ok",
        "service": "depot-crm-api",
        "realtime": "/realtime/ws/{channel}",
    }
