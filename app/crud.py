from datetime import timedelta

from sqlalchemy.orm import Session

from app import models, schemas
from app.state_machine import Status, validate_transition, default_follow_up_days


def create_application(db: Session, data: schemas.ApplicationCreate) -> models.Application:
    app_obj = models.Application(
        company=data.company,
        role_title=data.role_title,
        date_applied=data.date_applied,
        notes=data.notes,
        status=Status.APPLIED,
    )
    days = default_follow_up_days(Status.APPLIED)
    if days is not None:
        app_obj.follow_up_date = data.date_applied + timedelta(days=days)

    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return app_obj


def get_application(db: Session, application_id: int) -> models.Application | None:
    return db.get(models.Application, application_id)


def list_applications(db: Session, status: Status | None = None) -> list[models.Application]:
    query = db.query(models.Application)
    if status is not None:
        query = query.filter(models.Application.status == status)
    return query.order_by(models.Application.date_applied.desc()).all()


def update_application(
    db: Session, app_obj: models.Application, data: schemas.ApplicationUpdate
) -> models.Application:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(app_obj, field, value)
    db.commit()
    db.refresh(app_obj)
    return app_obj


def update_status(
    db: Session, app_obj: models.Application, new_status: Status
) -> models.Application:
    # Raises InvalidTransitionError on illegal moves; caller turns that
    # into an HTTP 409 in the router.
    validate_transition(app_obj.status, new_status)

    app_obj.status = new_status
    days = default_follow_up_days(new_status)
    if days is not None:
        app_obj.follow_up_date = app_obj.date_applied + timedelta(days=days)
    else:
        app_obj.follow_up_date = None

    db.commit()
    db.refresh(app_obj)
    return app_obj


def delete_application(db: Session, app_obj: models.Application) -> None:
    db.delete(app_obj)
    db.commit()
