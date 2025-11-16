from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class LocationBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=50)
    address: str = Field(..., min_length=5, max_length=200)
    capacity: int = Field(...)


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=50)
    address: Optional[str] = Field(None, min_length=5, max_length=200)
    capacity: Optional[int] = Field(None)


class LocationInDBBase(LocationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Location(LocationInDBBase):
    pass
