from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    VISITOR = "visitor"


class TicketStatus(Enum):
    CANCELLED = "cancelled"
    SOLD = "sold"
