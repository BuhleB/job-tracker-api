from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import applications

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Job Application Tracker API",
    description="Tracks job applications through a defined status workflow.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(applications.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}