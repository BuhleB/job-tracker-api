from datetime import date, datetime, timezone

from sqlalchemy import String, Date, DateTime, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.state_machine import Status


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company: Mapped[str] = mapped_column(String(120), nullable=False)
    role_title: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[Status] = mapped_column(
        SAEnum(Status), nullable=False, default=Status.APPLIED
    )
    date_applied: Mapped[date] = mapped_column(Date, nullable=False)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )
