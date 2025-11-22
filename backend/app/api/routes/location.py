from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from app.crud import location as crud
from app.schemas import location as schemas
from app.api.deps import SessionDep, roles_required
from app.models.enums import UserRole
from app.exceptions.location import (
    DuplicateLocationNameException,
    MissingLocationException,
)
from app.exceptions.db import DatabaseException


router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/", response_model=List[schemas.Location])
def get_locations(db: SessionDep):
    return crud.get_locations(db=db)


@router.post("/", dependencies=[Depends(roles_required([UserRole.ADMIN]))], response_model=schemas.Location)
def create_location(db: SessionDep, location: schemas.LocationCreate):
    try:
        return crud.create_location(db=db, location=location)
    except DuplicateLocationNameException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{location_id}", response_model=schemas.Location)
def get_location(db: SessionDep, location_id: int):
    try:
        return crud.get_location(db=db, location_id=location_id)
    except MissingLocationException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.put("/{location_id}", dependencies=[Depends(roles_required([UserRole.ADMIN]))], response_model=schemas.Location)
def update_location(
    db: SessionDep, location_id: int, location: schemas.LocationUpdate
):
    try:
        return crud.update_location(
            db=db, location_id=location_id, location=location
        )
    except MissingLocationException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{location_id}", dependencies=[Depends(roles_required([UserRole.ADMIN]))], response_model=schemas.Location)
def delete_location(db: SessionDep, location_id: int):
    try:
        return crud.delete_location(db=db, location_id=location_id)
    except MissingLocationException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
