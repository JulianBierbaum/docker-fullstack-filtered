
from datetime import date, time
import pytest
from sqlalchemy.orm import Session
from app.crud.event import (
    create_event,
    delete_event,
    get_event,
    get_events,
    get_events_by_location,
    get_event_by_organizer,
    update_event,
)
from app.exceptions.event import MissingEventException, WrongRoleException
from app.exceptions.location import MissingLocationException
from app.schemas.event import EventCreate, EventUpdate


def test_get_event_success(db: Session, test_event):
    result = get_event(db=db, event_id=test_event.id)
    assert result is not None
    assert result.id == test_event.id
    assert result.title == "Test Event"


def test_get_event_not_found(db: Session):
    result = get_event(db=db, event_id=999)
    assert result is None


def test_get_events(db: Session, test_event):
    result = get_events(db=db)
    assert len(result) == 1
    assert result[0].id == test_event.id


def test_get_events_by_location(db: Session, test_event, test_location):
    result = get_events_by_location(db=db, location_id=test_location.id)
    assert len(list(result)) == 1
    assert result[0].id == test_event.id


def test_get_event_by_organizer(db: Session, test_event, test_organizer):
    result = get_event_by_organizer(db=db, organizer_id=test_organizer.id)
    assert len(list(result)) == 1
    assert result[0].id == test_event.id


def test_create_event_success(db: Session, test_location, test_organizer):
    event_data = EventCreate(
        title="New Event",
        event_date=date(2026, 1, 1),
        start_time=time(20, 0),
        description="Another event",
        location_id=test_location.id,
        organizer_id=test_organizer.id,
        ticket_capacity=100,
    )
    result = create_event(db=db, event=event_data)
    assert result is not None
    assert result.title == "New Event"


def test_create_event_wrong_role(db: Session, test_location, test_visitor):
    event_data = EventCreate(
        title="New Event",
        event_date=date(2026, 1, 1),
        start_time=time(20, 0),
        description="Another event",
        location_id=test_location.id,
        organizer_id=test_visitor.id,
        ticket_capacity=100,
    )
    with pytest.raises(WrongRoleException):
        create_event(db=db, event=event_data)


def test_create_event_missing_location(db: Session, test_organizer):
    event_data = EventCreate(
        title="New Event",
        event_date=date(2026, 1, 1),
        start_time=time(20, 0),
        description="Another event",
        location_id=999,
        organizer_id=test_organizer.id,
        ticket_capacity=100,
    )
    with pytest.raises(MissingLocationException):
        create_event(db=db, event=event_data)


def test_update_event_success(db: Session, test_event):
    update_data = EventUpdate(title="Updated Event Title")
    result = update_event(db=db, event=update_data, event_id=test_event.id)
    assert result is not None
    assert result.title == "Updated Event Title"


def test_update_event_not_found(db: Session):
    update_data = EventUpdate(title="Nonexistent")
    with pytest.raises(MissingEventException):
        update_event(db=db, event=update_data, event_id=999)


def test_delete_event_success(db: Session, test_event):
    result = delete_event(db=db, event_id=test_event.id)
    assert result is not None
    assert result.deleted_at is not None
    assert get_event(db=db, event_id=test_event.id) is None


def test_delete_event_not_found(db: Session):
    with pytest.raises(MissingEventException):
        delete_event(db=db, event_id=999)
