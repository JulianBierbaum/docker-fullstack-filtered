from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import SessionDep, roles_required
from app.crud import ticket as crud
from app.exceptions.db import DatabaseException
from app.exceptions.event import MissingEventException
from app.exceptions.ticket import MissingTicketException
from app.models.enums import UserRole
from app.schemas import ticket as schemas

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get(
    "/",
    dependencies=[Depends(roles_required([UserRole.ADMIN]))],
    response_model=list[schemas.Ticket],
)
def get_tickets(db: SessionDep):
    return crud.get_tickets(db=db)


@router.post(
    "/",
    dependencies=[Depends(roles_required([UserRole.ORGANIZER, UserRole.ADMIN]))],
    response_model=schemas.Ticket,
)
def create_ticket(db: SessionDep, ticket: schemas.TicketCreate):
    try:
        return crud.create_ticket(db=db, ticket=ticket)
    except MissingEventException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{ticket_id}", response_model=schemas.Ticket)
def get_ticket(db: SessionDep, ticket_id: int):
    try:
        return crud.get_ticket(db=db, ticket_id=ticket_id)
    except MissingTicketException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/{ticket_id}",
    dependencies=[Depends(roles_required([UserRole.ORGANIZER, UserRole.ADMIN]))],
    response_model=schemas.Ticket,
)
def update_ticket(db: SessionDep, ticket_id: int, ticket: schemas.TicketUpdate):
    try:
        return crud.update_ticket(db=db, ticket_id=ticket_id, ticket=ticket)
    except MissingTicketException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{ticket_id}",
    dependencies=[Depends(roles_required([UserRole.ADMIN]))],
    response_model=schemas.TicketDeleted,
)
def delete_ticket(db: SessionDep, ticket_id: int):
    """Delete a ticket (Admin only). Note: Prefer deleting via bookings."""
    try:
        return crud.delete_ticket(db=db, ticket_id=ticket_id)
    except MissingTicketException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/event/{event_id}", response_model=list[schemas.Ticket])
def get_tickets_by_event(db: SessionDep, event_id: int):
    return crud.get_tickets_by_event(db=db, event_id=event_id)


@router.get("/event/{event_id}/available", response_model=list[schemas.Ticket])
def get_available_tickets_by_event(db: SessionDep, event_id: int):
    return crud.get_available_tickets_by_event(db=db, event_id=event_id)


@router.get("/event/{event_id}/available/count", response_model=int)
def get_available_ticket_count_by_event(db: SessionDep, event_id: int):
    return crud.get_available_ticket_count_by_event(db=db, event_id=event_id)
