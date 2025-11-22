from typing import List
from fastapi import APIRouter, HTTPException, status
from app.crud import ticket as crud
from app.schemas import ticket as schemas
from app.api.deps import SessionDep
from app.exceptions.ticket import MissingTicketException
from app.exceptions.db import DatabaseException


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("/", response_model=List[schemas.Ticket])
def get_tickets(db: SessionDep):
    return crud.get_tickets(db=db)


@router.post("/", response_model=schemas.Ticket)
def create_ticket(db: SessionDep, ticket: schemas.TicketCreate):
    try:
        return crud.create_ticket(db=db, ticket=ticket)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.put("/{ticket_id}", response_model=schemas.Ticket)
def update_ticket(db: SessionDep, ticket_id: int, ticket: schemas.TicketUpdate):
    try:
        return crud.update_ticket(db=db, ticket_id=ticket_id, ticket=ticket)
    except MissingTicketException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{ticket_id}", response_model=schemas.Ticket)
def cancel_ticket(db: SessionDep, ticket_id: int):
    try:
        return crud.cancel_ticket(db=db, ticket_id=ticket_id)
    except MissingTicketException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/event/{event_id}", response_model=List[schemas.Ticket])
def get_tickets_by_event(db: SessionDep, event_id: int):
    return crud.get_tickets_by_event(db=db, event_id=event_id)


@router.get("/event/{event_id}/available", response_model=List[schemas.Ticket])
def get_available_tickets_by_event(db: SessionDep, event_id: int):
    return crud.get_available_tickets_by_event(db=db, event_id=event_id)


@router.get("/event/{event_id}/available/count", response_model=int)
def get_available_ticket_count_by_event(db: SessionDep, event_id: int):
    return crud.get_available_ticket_count_by_event(db=db, event_id=event_id)
