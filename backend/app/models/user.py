from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.session import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    email: Mapped[EmailStr] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role : Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now())

    organized_events = relationship("Event", back_populates="organizer")
    bookings = relationship("Booking", back_populates="user")
