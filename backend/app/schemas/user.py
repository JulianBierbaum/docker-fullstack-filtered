from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import UserRole


class UserBase(BaseModel):
    username: str = Field(..., min_length=5, max_length=15)
    email: EmailStr = Field(..., min_length=7, max_length=50)
    role: UserRole = Field(...)


class UserCreate(UserBase):
    password: str = Field(..., min_length=1, max_length=50)


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    email: EmailStr | None = None
    role: UserRole | None = None


class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
