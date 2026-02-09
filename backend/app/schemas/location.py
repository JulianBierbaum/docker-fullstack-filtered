from datetime import datetime

from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=50)
    address: str = Field(..., min_length=5, max_length=200)
    capacity: int = Field(..., ge=1)


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: str | None = Field(None, min_length=5, max_length=50)
    address: str | None = Field(None, min_length=5, max_length=200)
    capacity: int | None = Field(None, ge=1)


class LocationInDBBase(LocationBase):
    id: int
    capacity: int
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    class Config:
        from_attributes = True


class Location(LocationInDBBase):
    pass
