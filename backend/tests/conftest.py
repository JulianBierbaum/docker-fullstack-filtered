import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.database.session import Base
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.location import Location
from app.models.event import Event
from app.models.ticket import Ticket
from app.models.booking import Booking
from app.main import app
from datetime import date, time
from passlib.context import CryptContext
from app.models.enums import UserRole

SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"
ALGORITHM = "HS256"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@pytest.fixture(scope="function")
def db():
    """Creates a new database session and ensures tables exist."""
    Base.metadata.create_all(bind=engine)  
    session = TestingSessionLocal()
    try:
        yield session  
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)  

@pytest.fixture(scope="function")
def client(db):
    """Provides a FastAPI test client using the same session as the test."""
    
    def override_get_db():
        Base.metadata.create_all(bind=engine) 
        yield db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture
def test_superuser(db):
    """Creates a superuser in the test database."""
    user = User(username="superuser", email="superuser@example.com", hashed_password=hash_password("Kennwort1"), role=UserRole.ADMIN)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_organizer(db):
    """Creates an organizer in the test database."""
    user = User(username="organizer", email="organizer@example.com", hashed_password=hash_password("Kennwort1"), role=UserRole.ORGANIZER)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_visitor(db):
    """Creates a visitor in the test database."""
    user = User(username="visitor", email="visitor@example.com", hashed_password=hash_password("Kennwort1"), role=UserRole.VISITOR)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_location(db):
    """Creates a location in the test database."""
    location = Location(
        name="Test Location",
        address="123 Test Street",
        capacity=100,
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location

@pytest.fixture
def test_event(db, test_location, test_organizer):
    """Creates an event in the test database."""
    event = Event(
        title="Test Event",
        event_date=date(2025, 12, 25),
        start_time=time(18, 0),
        description="A test event",
        location_id=test_location.id,
        organizer_id=test_organizer.id,
        ticket_capacity=50,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@pytest.fixture
def test_ticket(db, test_event):
    """Creates a ticket in the test database."""
    ticket = Ticket(
        event_id=test_event.id,
        seat_num="A1",
        price=50,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

@pytest.fixture
def test_booking(db, test_visitor, test_ticket):
    """Creates a booking in the test database."""
    booking = Booking(
        user_id=test_visitor.id,
        ticket_id=test_ticket.id,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@pytest.fixture
def client_with_superuser(client, test_superuser):
    """Override `get_current_active_superuser` to return an admin user."""
    def override_get_current_user():
        return test_superuser  
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    return client
