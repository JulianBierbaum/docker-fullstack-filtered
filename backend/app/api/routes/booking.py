from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from app.crud import booking as crud
from app.schemas import booking as schemas
from app.api.deps import SessionDep, roles_required
from app.models.enums import UserRole
from app.exceptions.booking import MissingBookingException
from app.exceptions.user import MissingUserException
from app.exceptions.ticket import MissingTicketException
from app.exceptions.db import DatabaseException


router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/", response_model=List[schemas.Booking])
def get_bookings(db: SessionDep):
    return crud.get_all_bookings(db=db)


@router.post("/", response_model=schemas.Booking)
def create_booking(db: SessionDep, booking: schemas.BookingCreate):
    try:
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
    dependencies=[Depends(roles_required([UserRole.ADMIN]))],
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
    dependencies=[Depends(roles_required([UserRole.ADMIN]))],
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