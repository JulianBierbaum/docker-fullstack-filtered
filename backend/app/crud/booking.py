from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.ticket import delete_ticket, get_ticket
from app.crud.user import get_user
from app.exceptions.booking import MissingBookingException
from app.exceptions.db import DatabaseException
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingUpdate


def get_all_bookings(db: Session):
    return db.query(Booking).all()


def get_booking(*, db: Session, booking_number: int):
    db_booking = (
        db.query(Booking).filter(Booking.booking_number == booking_number).first()
    )
    if not db_booking:
        raise MissingBookingException()
    return db_booking


def get_bookings_by_user(*, db: Session, user_id: int):
    return db.query(Booking).filter(Booking.user_id == user_id).all()


def get_bookings_by_ticket(*, db: Session, ticket_id: int):
    return db.query(Booking).filter(Booking.ticket_id == ticket_id).all()


def get_bookings_by_event(*, db: Session, event_id: int):
    from app.models.ticket import Ticket

    return (
        db.query(Booking)
        .join(Ticket, Booking.ticket_id == Ticket.id)
        .filter(Ticket.event_id == event_id)
        .all()
    )


def create_booking(*, db: Session, booking_data: BookingCreate):
    _ = get_ticket(db=db, ticket_id=booking_data.ticket_id)
    _ = get_user(db=db, user_id=booking_data.user_id)

    db_booking = Booking(
        user_id=booking_data.user_id,
        ticket_id=booking_data.ticket_id,
    )

    try:
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    except IntegrityError as e:
        db.rollback()
        raise DatabaseException(str(e))


def update_booking(*, db: Session, booking_number: int, booking_data: BookingUpdate):
    db_booking = get_booking(db=db, booking_number=booking_number)

    try:
        update_data = booking_data.model_dump(exclude_unset=True)

        if "user_id" in update_data:
            _ = get_user(db=db, user_id=update_data["user_id"])
        if "ticket_id" in update_data:
            _ = get_ticket(db=db, ticket_id=update_data["ticket_id"])

        for key, value in update_data.items():
            setattr(db_booking, key, value)

        db.commit()
        db.refresh(db_booking)
        return db_booking
    except IntegrityError as e:
        db.rollback()
        raise DatabaseException(str(e))


def delete_booking(*, db: Session, booking_number: int):
    db_booking = get_booking(db=db, booking_number=booking_number)
    ticket_id = db_booking.ticket_id

    try:
        db.delete(db_booking)
        db.commit()

        delete_ticket(db=db, ticket_id=ticket_id)

        return db_booking
    except IntegrityError as e:
        db.rollback()
        raise DatabaseException(str(e))
