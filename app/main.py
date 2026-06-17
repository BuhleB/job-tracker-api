from fastapi import FastAPI

from app.database import Base, engine
from app.routers import applications

# Creates tables on startup if they don't exist yet. Fine for SQLite/dev;
# in a real production setup with Postgres you'd swap this for Alembic
# migrations, but that's a deliberate scope cut for this project.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Application Tracker API",
    description="Tracks job applications through a defined status workflow.",
    version="1.0.0",
)

app.include_router(applications.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
