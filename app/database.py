import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL is read from the environment so the same code runs against
# SQLite locally/in CI and PostgreSQL in production (12-factor config).
# Example production value: postgresql://user:pass@host:5432/jobtracker
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./jobtracker.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
