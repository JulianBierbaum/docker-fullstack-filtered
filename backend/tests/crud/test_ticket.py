
import pytest
from sqlalchemy.orm import Session
from app.crud.ticket import (
    create_ticket,
    cancel_ticket,
    get_ticket,
    get_tickets,
    get_tickets_by_event,
    update_ticket,
    get_available_ticket_count_by_event,
    get_available_tickets_by_event
)
from app.exceptions.ticket import MissingTicketException
from app.schemas.ticket import TicketCreate, TicketUpdate


def test_get_ticket_success(db: Session, test_ticket):
    result = get_ticket(db=db, ticket_id=test_ticket.id)
    assert result is not None
    assert result.id == test_ticket.id
    assert result.seat_num == "A1"


def test_get_ticket_not_found(db: Session):
    with pytest.raises(MissingTicketException):
        get_ticket(db=db, ticket_id=999)


def test_get_tickets(db: Session, test_ticket):
    result = get_tickets(db=db)
    assert len(result) == 1
    assert result[0].id == test_ticket.id


def test_get_tickets_by_event(db: Session, test_ticket, test_event):
    result = get_tickets_by_event(db=db, event_id=test_event.id)
    assert len(result) == 1
    assert result[0].id == test_ticket.id

def test_get_available_tickets_by_event(db: Session, test_ticket, test_event):
    result = get_available_tickets_by_event(db=db, event_id=test_event.id)
    assert len(result) == 0
    cancel_ticket(db=db, ticket_id=test_ticket.id)
    result = get_available_tickets_by_event(db=db, event_id=test_event.id)
    assert len(result) == 1


def test_get_available_ticket_count_by_event(db: Session, test_ticket, test_event):
    result = get_available_ticket_count_by_event(db=db, event_id=test_event.id)
    assert result == 49
    cancel_ticket(db=db, ticket_id=test_ticket.id)
    result = get_available_ticket_count_by_event(db=db, event_id=test_event.id)
    assert result == 50


def test_create_ticket_success(db: Session, test_event):
    ticket_data = TicketCreate(event_id=test_event.id, seat_num="B2", price=100)
    result = create_ticket(db=db, ticket=ticket_data)
    assert result is not None
    assert result.seat_num == "B2"


def test_update_ticket_success(db: Session, test_ticket):
    update_data = TicketUpdate(price=75)
    result = update_ticket(db=db, ticket=update_data, ticket_id=test_ticket.id)
    assert result is not None
    assert result.price == 75


def test_update_ticket_not_found(db: Session):
    update_data = TicketUpdate(price=75)
    with pytest.raises(MissingTicketException):
        update_ticket(db=db, ticket=update_data, ticket_id=999)


def test_cancel_ticket_success(db: Session, test_ticket):
    result = cancel_ticket(db=db, ticket_id=test_ticket.id)
    assert result is not None
    assert result.cancelled_at is not None


def test_cancel_ticket_not_found(db: Session):
    with pytest.raises(MissingTicketException):
        cancel_ticket(db=db, ticket_id=999)
