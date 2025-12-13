from datetime import date, time, datetime
from pydantic import BaseModel, Field
from typing import Optional


class EventBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    event_date: date
    start_time: time
    description: Optional[str] = None
    location_id: int
    organizer_id: int
    ticket_capacity: int


class EventCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    event_date: date
    start_time: time
    description: Optional[str] = None
    location_id: int
    organizer_id: Optional[int] = None
    ticket_capacity: int


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=100)
    event_date: Optional[date] = None
    start_time: Optional[time] = None
    description: Optional[str] = None
    location_id: Optional[int] = None
    organizer_id: Optional[int] = None
    ticket_capacity: Optional[int] = None


class EventInDBBase(EventBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Event(EventInDBBase):
    pass
