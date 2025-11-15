from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class TicketBase(BaseModel):
    event_id: int
    seat_num: str = Field(..., max_length=10)
    price: int = Field(...)


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    event_id: Optional[int] = None
    seat_num: Optional[str] = Field(None, max_length=10)
    price: Optional[int] = Field(None)


class TicketInDBBase(TicketBase):
    id: int
    sold_at: datetime
    updated_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Ticket(TicketInDBBase):
    pass
