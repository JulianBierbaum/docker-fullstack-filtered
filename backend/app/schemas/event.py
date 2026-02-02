from datetime import date, datetime, time

from pydantic import BaseModel, Field


class EventBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    event_date: date
    start_time: time
    description: str | None = None
    location_id: int
    organizer_id: int
    ticket_capacity: int = Field(..., ge=1)


class EventCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    event_date: date
    start_time: time
    description: str | None = None
    location_id: int
    organizer_id: int
    ticket_capacity: int


class EventUpdate(BaseModel):
    title: str | None = Field(None, min_length=5, max_length=100)
    event_date: date | None = None
    start_time: time | None = None
    description: str | None = None
    location_id: int | None = None
    organizer_id: int | None = None
    ticket_capacity: int | None = None


class EventInDBBase(EventBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True


class Event(EventInDBBase):
    pass
