from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.location import get_location
from app.crud.user import get_user
from app.exceptions.db import DatabaseException
from app.exceptions.event import MissingEventException, WrongRoleException
from app.models.enums import UserRole
from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate


def get_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
):
    query = db.query(Event).filter(Event.deleted_at.is_(None))

    return query.offset(skip).limit(limit).all()


def get_event(*, db: Session, event_id: int):
    db_event = (
        db.query(Event).filter(Event.id == event_id, Event.deleted_at.is_(None)).first()
    )
    if not db_event:
        raise MissingEventException()
    return db_event


def get_events_by_location(*, db: Session, location_id: int):
    return db.query(Event).filter(
        Event.location_id == location_id, Event.deleted_at.is_(None)
    )


def get_event_by_organizer(*, db: Session, organizer_id: int):
    return db.query(Event).filter(
        Event.organizer_id == organizer_id, Event.deleted_at.is_(None)
    )


def create_event(*, db: Session, event: EventCreate):
    db_user = get_user(db=db, user_id=event.organizer_id)

    if (
        db_user.role != UserRole.ORGANIZER.value
        and db_user.role != UserRole.ADMIN.value
    ):
        raise WrongRoleException(user=str(db_user.username))

    _ = get_location(db=db, location_id=event.location_id)

    db_event = Event(
        title=event.title,
        event_date=event.event_date,
        start_time=event.start_time,
        description=event.description,
        location_id=event.location_id,
        organizer_id=event.organizer_id,
        ticket_capacity=event.ticket_capacity,
    )
    try:
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event
    except IntegrityError as e:
        db.rollback()
        raise DatabaseException(str(e))


def update_event(*, db: Session, event: EventUpdate, event_id: int):
    db_event = get_event(db=db, event_id=event_id)

    update_data = event.model_dump(exclude_unset=True)

    if "location_id" in update_data:
        _ = get_location(db=db, location_id=update_data["location_id"])
    if "organizer_id" in update_data:
        db_user = get_user(db=db, user_id=update_data["organizer_id"])
        if (
            db_user.role != UserRole.ORGANIZER.value
            and db_user.role != UserRole.ADMIN.value
        ):
            raise WrongRoleException(user=db_user.username)

    for key, value in update_data.items():
        setattr(db_event, key, value)

    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(*, db: Session, event_id: int):
    db_event = get_event(db=db, event_id=event_id)

    try:
        db_event.deleted_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(db_event)

        return db_event
    except IntegrityError as e:
        db.rollback()
        raise DatabaseException(str(e))
