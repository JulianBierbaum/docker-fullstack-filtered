from datetime import datetime

from pydantic import BaseModel


class BookingBase(BaseModel):
    user_id: int
    ticket_id: int


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    user_id: int | None = None
    ticket_id: int | None = None


class BookingInDBBase(BookingBase):
    booking_number: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class Booking(BookingInDBBase):
    pass


class BookingDeleted(BaseModel):
    booking_number: int
    user_id: int
    ticket_id: int

    class Config:
        from_attributes = True
