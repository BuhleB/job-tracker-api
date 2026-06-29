# Job Application Tracker API

A REST API I built to track job applications through a structured status
workflow: `applied → interviewing → offer → accepted`, with `rejected` and
`withdrawn` available as exits at any active stage.

Live API: https://job-tracker-api-1sca.onrender.com/docs
Live Dashboard: https://jobtacker.netlify.app/

![CI](https://github.com/BuhleB/job-tracker-api/actions/workflows/ci.yml/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)

## Why I built this

I built this to have a dedicated tool for tracking my own job search,
and to demonstrate testing patterns I apply professionally — not just
CRUD with tests bolted on.

The core business rule is that an application can't skip stages (you
can't jump from "applied" to "offer" without going through
"interviewing"), and terminal statuses like "rejected" or "accepted"
can't be changed. Follow-up dates are calculated automatically based
on the current status.

I isolated that logic into its own module (`app/state_machine.py`) with
no database or FastAPI dependencies so it can be unit tested in isolation.

## Tech stack

- **API**: FastAPI + Pydantic v2
- **ORM / DB**: SQLAlchemy 2.0, SQLite (dev/demo), configurable to PostgreSQL
  via `DATABASE_URL` env var with no code changes
- **Testing**: pytest, pytest-cov, FastAPI's `TestClient`
- **CI/CD**: GitHub Actions — runs the full suite, enforces a coverage floor,
  then builds the Docker image on every push
- **Containerization**: Docker

## Test strategy

| Layer | File | What it covers | Runs against |
|---|---|---|---|
| Unit | `tests/test_state_machine.py` | Status transition rules, follow-up date logic | Pure functions, no dependencies |
| Integration | `tests/test_crud.py` | CRUD + business logic against a real DB session | In-memory SQLite |
| API | `tests/test_api.py` | Full HTTP cycle, status codes, error responses | In-memory SQLite via `TestClient` |

32 tests, 93% line coverage. The CI pipeline fails the build if coverage
drops below 80%, so the gate is enforced automatically on every push.

The structure follows a test pyramid: the majority of tests are fast,
isolated unit tests, with a smaller set of integration tests, and a thin
layer of API-level tests confirming everything works together end to end.

## Running locally

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
# Interactive docs at http://localhost:8000/docs
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

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/applications/` | Create an application (status defaults to `applied`) |
| `GET` | `/applications/` | List all applications; filter with `?status=` |
| `GET` | `/applications/{id}` | Get a single application |
| `PUT` | `/applications/{id}` | Update company, role, notes, or follow-up date |
| `PATCH` | `/applications/{id}/status` | Advance status (validated against workflow rules) |
| `DELETE` | `/applications/{id}` | Delete an application |
| `GET` | `/health` | Health check |

## Coming next

- React dashboard for visualising applications by status
- JWT authentication via FastAPI's `OAuth2PasswordBearer`
- Alembic migrations for schema version control
