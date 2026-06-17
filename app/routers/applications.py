from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.state_machine import InvalidTransitionError, Status

router = APIRouter(prefix="/applications", tags=["applications"])


def _get_or_404(db: Session, application_id: int):
    app_obj = crud.get_application(db, application_id)
    if app_obj is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return app_obj


@router.post("/", response_model=schemas.ApplicationOut, status_code=201)
def create_application(payload: schemas.ApplicationCreate, db: Session = Depends(get_db)):
    return crud.create_application(db, payload)


@router.get("/", response_model=list[schemas.ApplicationOut])
def list_applications(status: Status | None = None, db: Session = Depends(get_db)):
    return crud.list_applications(db, status)


@router.get("/{application_id}", response_model=schemas.ApplicationOut)
def get_application(application_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, application_id)


@router.put("/{application_id}", response_model=schemas.ApplicationOut)
def update_application(
    application_id: int, payload: schemas.ApplicationUpdate, db: Session = Depends(get_db)
):
    app_obj = _get_or_404(db, application_id)
    return crud.update_application(db, app_obj, payload)


@router.patch("/{application_id}/status", response_model=schemas.ApplicationOut)
def update_status(
    application_id: int, payload: schemas.StatusUpdate, db: Session = Depends(get_db)
):
    app_obj = _get_or_404(db, application_id)
    try:
        return crud.update_status(db, app_obj, payload.status)
    except InvalidTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.delete("/{application_id}", status_code=204)
def delete_application(application_id: int, db: Session = Depends(get_db)):
    app_obj = _get_or_404(db, application_id)
    crud.delete_application(db, app_obj)
