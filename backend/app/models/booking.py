from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship
from app.database.session import Base


class Booking(Base):
    __tablename__ = "bookings"

    booking_number = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, unique=True)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="bookings")
    ticket = relationship("Ticket", back_populates="booking")
