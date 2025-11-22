from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from app.crud import event as crud
from app.schemas import event as schemas
from app.api.deps import SessionDep, roles_required
from app.models.enums import UserRole
from app.exceptions.event import MissingEventException, WrongRoleException
from app.exceptions.db import DatabaseException


router = APIRouter(prefix="/events", tags=["events"])


@router.get("/", response_model=List[schemas.Event])
def get_events(db: SessionDep):
    return crud.get_events(db=db)


@router.post("/", dependencies=[Depends(roles_required([UserRole.ORGANIZER, UserRole.ADMIN]))], response_model=schemas.Event)
def create_event(db: SessionDep, event: schemas.EventCreate):
    try:
        return crud.create_event(db=db, event=event)
    except WrongRoleException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{event_id}", response_model=schemas.Event)
def get_event(db: SessionDep, event_id: int):
    try:
        return crud.get_event(db=db, event_id=event_id)
    except MissingEventException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.put("/{event_id}", dependencies=[Depends(roles_required([UserRole.ADMIN]))], response_model=schemas.Event)
def update_event(db: SessionDep, event_id: int, event: schemas.EventUpdate):
    try:
        return crud.update_event(db=db, event_id=event_id, event=event)
    except MissingEventException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except WrongRoleException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{event_id}", dependencies=[Depends(roles_required([UserRole.ADMIN]))], response_model=schemas.Event)
def delete_event(db: SessionDep, event_id: int):
    try:
        return crud.delete_event(db=db, event_id=event_id)
    except MissingEventException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/location/{location_id}", response_model=List[schemas.Event])
def get_events_by_location(db: SessionDep, location_id: int):
    return crud.get_events_by_location(db=db, location_id=location_id)


@router.get("/organizer/{organizer_id}", response_model=List[schemas.Event])
def get_events_by_organizer(db: SessionDep, organizer_id: int):
    return crud.get_event_by_organizer(db=db, organizer_id=organizer_id)
