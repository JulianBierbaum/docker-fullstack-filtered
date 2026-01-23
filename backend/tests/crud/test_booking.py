import pytest
from sqlalchemy.orm import Session

from app.crud.booking import (
    create_booking,
    delete_booking,
    get_all_bookings,
    get_booking,
    get_bookings_by_event,
    get_bookings_by_ticket,
    get_bookings_by_user,
    update_booking,
)
from app.crud.ticket import create_ticket
from app.exceptions.booking import MissingBookingException
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingUpdate
from app.schemas.ticket import TicketCreate


def test_get_booking_success(db: Session, test_booking):
    result = get_booking(db=db, booking_number=test_booking.booking_number)
    assert result is not None
    assert result.booking_number == test_booking.booking_number


def test_get_booking_not_found(db: Session):
    with pytest.raises(MissingBookingException):
        get_booking(db=db, booking_number=999)


def test_get_all_bookings(db: Session, test_booking):
    result = get_all_bookings(db=db)
    assert len(result) == 1
    assert result[0].booking_number == test_booking.booking_number


def test_get_bookings_by_user(db: Session, test_booking, test_visitor):
    result = get_bookings_by_user(db=db, user_id=test_visitor.id)
    assert len(result) == 1
    assert result[0].booking_number == test_booking.booking_number


def test_get_bookings_by_ticket(db: Session, test_booking, test_ticket):
    result = get_bookings_by_ticket(db=db, ticket_id=test_ticket.id)
    assert len(result) == 1
    assert result[0].booking_number == test_booking.booking_number


def test_get_bookings_by_event(db: Session, test_booking, test_event):
    result = get_bookings_by_event(db=db, event_id=test_event.id)
    assert len(result) == 1
    assert result[0].booking_number == test_booking.booking_number


def test_create_booking_success(db: Session, test_visitor, test_event):
    ticket_data = TicketCreate(event_id=test_event.id, seat_num="C3", price=25)
    new_ticket = create_ticket(db=db, ticket=ticket_data)
    booking_data = BookingCreate(user_id=test_visitor.id, ticket_id=new_ticket.id)
    result = create_booking(db=db, booking_data=booking_data)
    assert result is not None
    assert result.user_id == test_visitor.id
    assert result.ticket_id == new_ticket.id


def test_update_booking_success(db: Session, test_booking, test_visitor, test_event):
    _ = test_visitor
    ticket_data = TicketCreate(event_id=test_event.id, seat_num="D4", price=30)
    new_ticket = create_ticket(db=db, ticket=ticket_data)
    update_data = BookingUpdate(ticket_id=new_ticket.id)
    result = update_booking(
        db=db, booking_number=test_booking.booking_number, booking_data=update_data
    )
    assert result is not None
    assert result.ticket_id == new_ticket.id


def test_update_booking_not_found(db: Session):
    update_data = BookingUpdate(user_id=1)
    with pytest.raises(MissingBookingException):
        update_booking(db=db, booking_number=999, booking_data=update_data)


def test_delete_booking_success(db: Session, test_booking):
    booking_number = test_booking.booking_number
    result = delete_booking(db=db, booking_number=booking_number)
    assert result is not None
    assert result.booking_number == booking_number
    assert (
        db.query(Booking).filter(Booking.booking_number == booking_number).first()
        is None
    )


def test_delete_booking_not_found(db: Session):
    with pytest.raises(MissingBookingException):
        delete_booking(db=db, booking_number=999)
