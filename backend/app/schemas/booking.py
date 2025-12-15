from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class BookingBase(BaseModel):
    user_id: int
    ticket_id: int


class BookingCreate(BookingBase):
    user_id: Optional[int] = None


class BookingUpdate(BaseModel):
    user_id: Optional[int] = None
    ticket_id: Optional[int] = None


class BookingInDBBase(BookingBase):
    booking_number: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Booking(BookingInDBBase):
    pass