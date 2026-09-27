# Deployment checklist

Use this checklist before deploying the FastAPI backend.

## Configuration

- [ ] Set a production `DATABASE_URL`.
- [ ] Configure `CORS_ORIGINS` with the exact frontend origin.
- [ ] Keep secrets outside source control.
- [ ] Use a production-safe database user with only required permissions.

## Database

- [ ] Run `alembic upgrade head`.
- [ ] Confirm the application can open a database connection.
- [ ] Back up existing production data before schema changes.
- [ ] Avoid running sample `seed.py` data against production.

## API

- [ ] Start with `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- [ ] Verify `/docs` or disable public docs if required by the hosting environment.
- [ ] Check `/dashboard/stats`.
- [ ] Test company, project, item and retrieval workflows end-to-end.

## Observability

- [ ] Capture application logs.
- [ ] Monitor HTTP 5xx responses.
- [ ] Add a lightweight health endpoint for the hosting platform.
- [ ] Record deployment version/commit SHA.

## Frontend connection

Set the frontend's `VITE_API_URL` to the deployed backend base URL and confirm browser CORS requests succeed.

## Post-deployment smoke test

1. Create a test company.
2. Create a project for that company.
3. Register an item.
4. Change its location/status.
5. Confirm a movement record is created.
6. Create a retrieval request.
7. Advance the retrieval workflow.
8. Remove test data if the environment is production.
