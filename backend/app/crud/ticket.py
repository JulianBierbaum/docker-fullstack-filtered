from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions.ticket import MissingTicketException
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.crud.event import get_event


def get_tickets(db: Session):
    return db.query(Ticket).all()


def get_ticket(*, db: Session, ticket_id: int):
    db_ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not db_ticket:
        raise MissingTicketException()
    return db_ticket


def get_tickets_by_event(*, db: Session, event_id: int):
    return db.query(Ticket).filter(Ticket.event_id == event_id).all()

def get_available_tickets_by_event(*, db: Session, event_id: int):
    return db.query(Ticket).filter(Ticket.event_id == event_id, Ticket.cancelled_at.is_not(None)).all()


def get_available_ticket_count_by_event(*, db: Session, event_id: int):
    return db.query(Ticket).filter(Ticket.event_id == event_id, Ticket.cancelled_at.is_not(None)).count()


def create_ticket(*, db: Session, ticket: TicketCreate):
    _ = get_event(db=db, event_id=ticket.event_id)

    db_ticket = Ticket(
        event_id=ticket.event_id,
        seat_num=ticket.seat_num,
        price=ticket.price,
    )

    try:
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket
    except IntegrityError as e:
        db.rollback()
        raise e


def update_ticket(*, db: Session, ticket: TicketUpdate, ticket_id: int):
    db_ticket = get_ticket(db=db, ticket_id=ticket_id)

    try:
        update_data = ticket.model_dump(exclude_unset=True)

        if "event_id" in update_data:
            _ = get_event(db=db, event_id=update_data["event_id"])

        for key, value in update_data.items():
            setattr(db_ticket, key, value)
        
        db.commit()
        db.refresh(db_ticket)
        return db_ticket
    except IntegrityError as e:
        db.rollback()
        raise e


def cancel_ticket(*, db: Session, ticket_id: int):
    db_ticket = get_ticket(db=db, ticket_id=ticket_id)

    try:
        db_ticket.cancelled_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(db_ticket)
        return db_ticket
    except IntegrityError as e:
        db.rollback()
        raise e
