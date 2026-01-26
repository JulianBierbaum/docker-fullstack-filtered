from datetime import datetime

from pydantic import BaseModel, Field


class TicketBase(BaseModel):
    event_id: int
    seat_num: str = Field(..., max_length=10)
    price: int = Field(...)


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    event_id: int | None = None
    seat_num: str | None = Field(default=None, max_length=50)
    price: int | None = Field(default=None)


class TicketInDBBase(TicketBase):
    id: int
    sold_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class Ticket(TicketInDBBase):
    pass


class TicketDeleted(BaseModel):
    id: int
    event_id: int
    seat_num: str
    price: int

    class Config:
        from_attributes = True
