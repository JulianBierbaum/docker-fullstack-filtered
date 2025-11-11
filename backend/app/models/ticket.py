from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    func,
    Enum,
    Numeric,
)
from sqlalchemy.orm import relationship
from app.database.session import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    seat_num = Column(String(10), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    sold_at = Column(DateTime, nullable=False, default=func.now())
    cancelled_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="tickets")
    booking = relationship("Booking", back_populates="ticket")
