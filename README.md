# Depot — storage & asset-tracking API

FastAPI + PostgreSQL backend for the managed storage / asset-tracking CRM
(companies → storage projects → items/containers, with a full movement
audit log and a pick-and-deliver retrieval workflow). This is the backend
half of the `storage-crm.jsx` frontend prototype — same data model, same
statuses, same location-code scheme.

## Stack

- FastAPI (REST API, auto docs)
- SQLAlchemy 2.0 (ORM)
- PostgreSQL
- Alembic (migrations)
- Docker Compose (for local Postgres + API)

## Quick start — Docker (recommended)

Requires Docker and Docker Compose.

```bash
docker compose up --build
```

This starts Postgres on `localhost:5432` and the API on `localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

To load the same sample data the frontend ships with:

```bash
docker compose exec api python seed.py
```

## Quick start — local Python

Requires Python 3.12+ and a running PostgreSQL instance.

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit DATABASE_URL to point at your Postgres

python seed.py                  # optional — loads sample data
uvicorn app.main:app --reload
```

The API will create its tables automatically on first startup. For schema
changes after that, use Alembic:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

## Project structure

```
app/
  main.py         FastAPI app, CORS, router wiring
  config.py       Settings loaded from .env
  database.py     SQLAlchemy engine/session
  models.py       ORM tables: Company, Project, Item, Movement, Retrieval
  schemas.py      Pydantic request/response models
  routers/
    companies.py  CRUD for business customers
    projects.py   CRUD for storage projects
    items.py      Item registration, status changes, relocation, search
    movements.py  Read-only audit log
    retrievals.py Create + advance pick/deliver requests
    dashboard.py  Aggregate stats for the dashboard view
alembic/          Migration environment and versions
seed.py           Loads sample data matching the frontend demo
docker-compose.yml
Dockerfile
```

## Data model

```
Company 1───* Project 1───* Item 1───* Movement
                  │             │
                  └──────* Retrieval *──────┘
                         (many-to-many via retrieval_items)
```

- **Item statuses**: Expected, Collected, In transit to warehouse, Received,
  Inspection required, Stored, Reserved for delivery, Picked,
  In transit to customer, Delivered, Returned to storage, Missing, Damaged,
  Disposed.
- **Retrieval stages**: Requested → Picking → Picked → Out for delivery → Delivered.
- **Location codes** follow `WAREHOUSE-ZONE-AISLE-RACK-LEVEL-POSITION`,
  e.g. `WH-LON-01-C-05-R12-L03-P02`. Built automatically from the
  registration form's location fields.
- Registering an item and changing its status or location always writes a
  row to `movements` — nothing overwrites a location silently, matching
  the audit-log requirement in the original spec.

## API reference

Full interactive reference (with request/response schemas) is at `/docs`
once the server is running. Summary:

| Method | Path | Purpose |
|---|---|---|
| GET/POST | `/companies` | List / create companies |
| GET/PATCH/DELETE | `/companies/{id}` | Read, update, delete a company |
| GET/POST | `/projects?company_id=` | List / create storage projects |
| GET/PATCH/DELETE | `/projects/{id}` | Read, update, delete a project |
| GET/POST | `/items?q=&project_id=&status=` | Search items / register a new item |
| GET/PATCH/DELETE | `/items/{id}` | Read, update, delete an item |
| POST | `/items/{id}/status` | Change item status (logs a movement) |
| POST | `/items/{id}/relocate` | Move an item to a new location (logs a movement) |
| GET | `/movements?item_id=` | Full audit log, optionally filtered |
| GET/POST | `/retrievals?project_id=` | List / create retrieval requests |
| GET | `/retrievals/{id}` | Read a single retrieval |
| POST | `/retrievals/{id}/advance` | Advance to the next pick/deliver stage |
| DELETE | `/retrievals/{id}` | Cancel/delete a retrieval |
| GET | `/dashboard/stats` | Aggregate counts + status breakdown |

## Connecting the frontend

Point the frontend at this API's base URL (`http://localhost:8000` by
default) and replace its `window.storage` calls with `fetch` calls against
these endpoints. CORS is already configured via the `CORS_ORIGINS` env var
— add your frontend's origin there.

## Not included (see original product spec for later phases)

Authentication/roles, file/image upload storage (S3 etc.), AI features
(vision, semantic search, duplicate detection), and QR/barcode scanning
hardware integration. The schema and routes are structured so these can be
added without reshaping what's already here.
