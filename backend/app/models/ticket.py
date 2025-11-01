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
from app.models.enums import TicketStatus


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    seat_num = Column(String(10), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.AVAILABLE)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    event = relationship("Event", back_populates="tickets")
    booking = relationship("Booking", back_populates="ticket")
