from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions.location import (
    DuplicateLocationNameException,
    MissingLocationException,
)
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate


def get_location(*, db: Session, location_id: int):
    db_location = (
        db.query(Location)
        .filter(Location.id == location_id, Location.deleted_at.is_(None))
        .first()
    )
    if not db_location:
        raise MissingLocationException()
    return db_location


def get_location_by_name(*, db: Session, location_name: str):
    return (
        db.query(Location)
        .filter(Location.name == location_name, Location.deleted_at.is_(None))
        .first()
    )


def get_locations(db: Session):
    return db.query(Location).filter(Location.deleted_at.is_(None)).all()


def create_location(*, db: Session, location: LocationCreate):
    if get_location_by_name(db=db, location_name=location.name):
        raise DuplicateLocationNameException(name=location.name)

    db_location = Location(
        name=location.name,
        address=location.address,
        capacity=location.capacity,
    )
    try:
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
        return db_location
    except IntegrityError as e:
        db.rollback()
        raise e


def update_location(*, db: Session, location: LocationUpdate, location_id: int):
    db_location = get_location(db=db, location_id=location_id)

    if not db_location:
        raise MissingLocationException()

    try:
        update_data = location.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_location, key, value)

        db.commit()
        db.refresh(db_location)
        return db_location
    except IntegrityError as e:
        db.rollback()
        raise e


def delete_location(*, db: Session, location_id: int):
    db_location = get_location(db=db, location_id=location_id)
    if not db_location:
        raise MissingLocationException()

    try:
        db_location.deleted_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(db_location)

        return db_location
    except IntegrityError as e:
        db.rollback()
        raise e
