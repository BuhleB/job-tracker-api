from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.state_machine import Status


class ApplicationCreate(BaseModel):
    company: str
    role_title: str
    date_applied: date
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    company: str | None = None
    role_title: str | None = None
    notes: str | None = None
    follow_up_date: date | None = None


class StatusUpdate(BaseModel):
    status: Status


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company: str
    role_title: str
    status: Status
    date_applied: date
    follow_up_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
