from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import SessionDep, get_current_user, roles_required
from app.crud import booking as crud
from app.crud import event as crud_event
from app.crud import ticket as ticket_crud
from app.exceptions.booking import MissingBookingException
from app.exceptions.db import DatabaseException
from app.exceptions.event import MissingEventException
from app.models.enums import UserRole
from app.models.user import User
from app.schemas import booking as schemas
from app.schemas import ticket as ticket_schemas

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get(
    "/",
    dependencies=[Depends(roles_required([UserRole.ADMIN]))],
    response_model=list[schemas.Booking],
)
def get_bookings(db: SessionDep):
    """Get all bookings (Admin only)."""
    return crud.get_all_bookings(db=db)


@router.get("/me", response_model=list[schemas.Booking])
def get_bookings_me(db: SessionDep, current_user: User = Depends(get_current_user)):
    """Get current user's bookings."""
    return crud.get_bookings_by_user(db=db, user_id=current_user.id)


@router.post("/event/{event_id}", response_model=schemas.Booking)
def book_event(
    db: SessionDep, event_id: int, current_user: User = Depends(get_current_user)
):
    try:
        available = ticket_crud.get_available_ticket_count_by_event(
            db=db, event_id=event_id
        )
    except MissingEventException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    if available <= 0:
        raise HTTPException(status_code=400, detail="No tickets available")

    event = crud_event.get_event(db=db, event_id=event_id)

    ticket_in = ticket_schemas.TicketCreate(
        event_id=event_id, seat_num="temp", price=25
    )
    ticket = ticket_crud.create_ticket(db=db, ticket=ticket_in)

    final_seat_num = f"{event.title}-{ticket.id}"
    ticket_update_in = ticket_schemas.TicketUpdate(seat_num=final_seat_num)
    ticket = ticket_crud.update_ticket(
        db=db, ticket_id=ticket.id, ticket=ticket_update_in
    )

    booking_in = schemas.BookingCreate(user_id=current_user.id, ticket_id=ticket.id)
    return crud.create_booking(db=db, booking_data=booking_in)


@router.delete("/me/{booking_number}", response_model=schemas.BookingDeleted)
def delete_own_booking(
    db: SessionDep, booking_number: int, current_user: User = Depends(get_current_user)
):
    """Delete own booking (and associated ticket)."""
    try:
        booking = crud.get_booking(db=db, booking_number=booking_number)
        if booking.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own bookings",
            )
        return crud.delete_booking(db=db, booking_number=booking_number)
    except MissingBookingException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/event/{event_id}", response_model=list[schemas.Booking])
def get_bookings_by_event(
    db: SessionDep,
    event_id: int,
    current_user: User = Depends(get_current_user),
):
    """Get all bookings for an event (Organizer of event or Admin only)."""
    try:
        event = crud_event.get_event(db=db, event_id=event_id)

        # Check permission: must be admin or the event's organizer
        if (
            current_user.role != UserRole.ADMIN.value
            and event.organizer_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view bookings for your own events",
            )

        return crud.get_bookings_by_event(db=db, event_id=event_id)
    except MissingEventException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{booking_number}",
    dependencies=[Depends(roles_required([UserRole.ADMIN]))],
    response_model=schemas.Booking,
)
def get_booking(db: SessionDep, booking_number: int):
    """Get a specific booking by number (Admin only)."""
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
    """Update a booking (Admin only)."""
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
    response_model=schemas.BookingDeleted,
)
def delete_booking(db: SessionDep, booking_number: int):
    """Delete a booking and its ticket (Admin only)."""
    try:
        return crud.delete_booking(db=db, booking_number=booking_number)
    except MissingBookingException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/user/{user_id}",
    dependencies=[Depends(roles_required([UserRole.ADMIN]))],
    response_model=list[schemas.Booking],
)
def get_bookings_by_user(db: SessionDep, user_id: int):
    """Get all bookings for a specific user (Admin only)."""
    return crud.get_bookings_by_user(db=db, user_id=user_id)


@router.get(
    "/ticket/{ticket_id}",
    dependencies=[Depends(roles_required([UserRole.ADMIN]))],
    response_model=list[schemas.Booking],
)
def get_bookings_by_ticket(db: SessionDep, ticket_id: int):
    """Get booking for a specific ticket (Admin only)."""
    return crud.get_bookings_by_ticket(db=db, ticket_id=ticket_id)
