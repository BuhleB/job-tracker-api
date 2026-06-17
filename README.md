# Job Application Tracker API

A REST API for tracking job applications through a defined status workflow
(`applied → interviewing → offer → accepted`, with `rejected`/`withdrawn`
as exits at any active stage). Built to demonstrate not just a working
service, but the testing discipline and delivery pipeline around it.

![CI](https://github.com/BuhleB/job-tracker-api/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)

## Why this project exists

Most portfolio APIs are CRUD with no real logic to test. This one has an
actual business rule worth verifying: an application can't jump straight
from "applied" to "offer," terminal statuses can't be changed, and
follow-up dates are calculated automatically based on status. That rule
lives in its own module (`app/state_machine.py`) specifically so it can be
unit tested without touching a database or the API layer.

## Tech stack

- **API**: FastAPI + Pydantic v2
- **ORM / DB**: SQLAlchemy 2.0, SQLite for dev/test, PostgreSQL in production
  (swap via the `DATABASE_URL` env var — no code changes needed)
- **Testing**: pytest, pytest-cov, FastAPI's `TestClient`
- **CI/CD**: GitHub Actions (test → coverage gate → Docker build)
- **Containerization**: Docker

## Test strategy

| Layer | File | What it covers | Runs against |
|---|---|---|---|
| Unit | `tests/test_state_machine.py` | Status transition rules, follow-up date logic | Nothing — pure functions |
| Integration | `tests/test_crud.py` | CRUD + business logic against a real DB session | In-memory SQLite |
| API / E2E | `tests/test_api.py` | Full HTTP request/response cycle, status codes, error handling | In-memory SQLite via `TestClient` |

32 tests, 93% line coverage. CI fails the build if coverage drops below 80%.

This mirrors a standard test pyramid: fast, isolated unit tests at the
base, fewer integration tests in the middle, and a thin layer of
API-level tests confirming the pieces work together end to end.

## Running it locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
# API docs at http://localhost:8000/docs
```

## Running the tests

```bash
pytest --cov=app --cov-report=term-missing
```

## Running with Docker

```bash
docker build -t job-tracker-api .
docker run -p 8000:8000 job-tracker-api
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/applications/` | Create an application (defaults to `applied`) |
| GET | `/applications/` | List applications, optional `?status=` filter |
| GET | `/applications/{id}` | Get one application |
| PUT | `/applications/{id}` | Update company/role/notes/follow-up date |
| PATCH | `/applications/{id}/status` | Move to a new status (validated) |
| DELETE | `/applications/{id}` | Delete an application |
| GET | `/health` | Health check |

## What I'd add next

- Alembic migrations instead of `create_all` on startup
- Authentication (the API is currently single-user/open)
- A `follow_up_date < today` query for an "overdue follow-ups" view
