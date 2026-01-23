from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    func,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    event_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    description = Column(Text, nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticket_capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    location = relationship("Location", back_populates="events")
    organizer = relationship("User", back_populates="organized_events")
    tickets = relationship("Ticket", back_populates="event")
