from typing import List
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from app.crud import booking as crud
from app.crud import ticket as ticket_crud
from app.crud import event as crud_event
from app.schemas import booking as schemas
from app.schemas import ticket as ticket_schemas
from app.api.deps import SessionDep, roles_required, get_current_user
from app.models.enums import UserRole
from app.models.user import User
from app.exceptions.booking import MissingBookingException
from app.exceptions.user import MissingUserException
from app.exceptions.ticket import MissingTicketException
from app.exceptions.db import DatabaseException


router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/", response_model=List[schemas.Booking])
def get_bookings(db: SessionDep):
    return crud.get_all_bookings(db=db)


@router.get("/me", response_model=List[schemas.Booking])
def get_bookings_me(db: SessionDep, current_user: User = Depends(get_current_user)):
    return crud.get_bookings_by_user(db=db, user_id=current_user.id)


@router.post("/event/{event_id}", response_model=schemas.Booking)
def book_event(db: SessionDep, event_id: int, current_user: User = Depends(get_current_user)):
    available = ticket_crud.get_available_ticket_count_by_event(db=db, event_id=event_id)
    if available <= 0:
        raise HTTPException(status_code=400, detail="No tickets available")

    event = crud_event.get_event(db=db, event_id=event_id)

    ticket_in = ticket_schemas.TicketCreate(
        event_id=event_id,
        seat_num="temp",
        price=25
    )
    ticket = ticket_crud.create_ticket(db=db, ticket=ticket_in)
    
    final_seat_num = f"{event.title}-{ticket.id}"
    ticket_update_in = ticket_schemas.TicketUpdate(seat_num=final_seat_num)
    ticket = ticket_crud.update_ticket(db=db, ticket_id=ticket.id, ticket=ticket_update_in)
    
    booking_in = schemas.BookingCreate(
        user_id=current_user.id,
        ticket_id=ticket.id
    )
    return crud.create_booking(db=db, booking_data=booking_in)


@router.post("/", response_model=schemas.Booking)
def create_booking(db: SessionDep, booking: schemas.BookingCreate, current_user: User = Depends(get_current_user)):
    try:
        booking.user_id = current_user.id
        return crud.create_booking(db=db, booking_data=booking)
    except MissingUserException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except MissingTicketException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{booking_number}", response_model=schemas.Booking)
def get_booking(db: SessionDep, booking_number: int):
    try:
        return crud.get_booking(db=db, booking_number=booking_number)
    except MissingBookingException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/{booking_number}",
    dependencies=[Depends(roles_required([UserRole.ADMIN, UserRole.ORGANIZER]))],
    response_model=schemas.Booking,
)
def update_booking(db: SessionDep, booking_number: int, booking: schemas.BookingUpdate):
    try:
        return crud.update_booking(
            db=db, booking_number=booking_number, booking_data=booking
        )
    except MissingBookingException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{booking_number}",
    dependencies=[Depends(roles_required([UserRole.ADMIN, UserRole.ORGANIZER]))],
    response_model=schemas.Booking,
)
def cancel_booking(db: SessionDep, booking_number: int):
    try:
        return crud.cancel_booking(db=db, booking_number=booking_number)
    except MissingBookingException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/user/{user_id}", response_model=List[schemas.Booking])
def get_bookings_by_user(db: SessionDep, user_id: int):
    return crud.get_bookings_by_user(db=db, user_id=user_id)


@router.get("/ticket/{ticket_id}", response_model=List[schemas.Booking])
def get_bookings_by_ticket(db: SessionDep, ticket_id: int):
    return crud.get_bookings_by_ticket(db=db, ticket_id=ticket_id)