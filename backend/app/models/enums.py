from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    ORGANIZER = "organizer"
    VISITOR = "visitor"


class TicketStatus(Enum):
    AVAILABLE = "available"
    SOLD = "sold"
