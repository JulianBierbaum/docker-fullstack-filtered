from datetime import date, time

from fastapi import status
from fastapi.testclient import TestClient

from app.models.event import Event


def test_create_event_success_admin(
    client_with_superuser: TestClient, db, test_location, test_organizer
):
    data = {
        "title": "Admin Created Event",
        "event_date": str(date(2025, 12, 31)),
        "start_time": str(time(20, 0)),
        "description": "New Year Party by Admin",
        "location_id": test_location.id,
        "organizer_id": test_organizer.id,
        "ticket_capacity": 100,
    }
    response = client_with_superuser.post("/api/events/", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == data["title"]

    event = db.query(Event).filter(Event.title == data["title"]).first()
    assert event is not None
    assert event.organizer_id == test_organizer.id


def test_create_event_success_organizer(
    client_with_organizer: TestClient, db, test_location, test_organizer
):
    data = {
        "title": "Organizer Created Event",
        "event_date": str(date(2025, 12, 30)),
        "start_time": str(time(19, 0)),
        "description": "Pre-New Year Party by Organizer",
        "location_id": test_location.id,
        "organizer_id": test_organizer.id,
        "ticket_capacity": 80,
    }
    response = client_with_organizer.post("/api/events/", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == data["title"]

    event = db.query(Event).filter(Event.title == data["title"]).first()
    assert event is not None
    assert event.organizer_id == test_organizer.id


def test_create_event_unauthorized_visitor(
    client_with_visitor: TestClient, test_location, test_organizer
):
    data = {
        "title": "Visitor Attempt Event",
        "event_date": str(date(2025, 12, 29)),
        "start_time": str(time(18, 0)),
        "description": "Unauthorized Event",
        "location_id": test_location.id,
        "organizer_id": test_organizer.id,
        "ticket_capacity": 50,
    }
    response = client_with_visitor.post("/api/events/", json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]


def test_get_events(client: TestClient, test_event):
    response = client.get("/api/events/")
    assert response.status_code == status.HTTP_200_OK
    events = response.json()
    assert any(event["id"] == test_event.id for event in events)


def test_get_event_success(client: TestClient, test_event):
    response = client.get(f"/api/events/{test_event.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_event.id
    assert response.json()["title"] == test_event.title


def test_get_event_missing(client: TestClient):
    response = client.get("/api/events/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Event not found" in response.json()["detail"]


def test_update_event_success_admin(client_with_superuser: TestClient, db, test_event):
    updated_title = "Updated Event Title"
    data = {"title": updated_title}
    response = client_with_superuser.put(f"/api/events/{test_event.id}", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == updated_title

    event = db.query(Event).filter(Event.id == test_event.id).first()
    assert event.title == updated_title


def test_update_event_unauthorized_visitor(client_with_visitor: TestClient, test_event):
    data = {"title": "Unauthorized Update"}
    response = client_with_visitor.put(f"/api/events/{test_event.id}", json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]


def test_update_event_missing(client_with_superuser: TestClient):
    data = {"title": "Missing Event Update"}
    response = client_with_superuser.put("/api/events/9999", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Event not found" in response.json()["detail"]


def test_delete_event_success_admin(client_with_superuser: TestClient, db, test_event):
    event_id = test_event.id
    response = client_with_superuser.delete(f"/api/events/{event_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == event_id
    assert response.json()["deleted_at"] is not None

    event = db.query(Event).filter(Event.id == event_id).first()
    assert event.deleted_at is not None


def test_delete_event_unauthorized_visitor(client_with_visitor: TestClient, test_event):
    response = client_with_visitor.delete(f"/api/events/{test_event.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]


def test_delete_event_missing(client_with_superuser: TestClient):
    response = client_with_superuser.delete("/api/events/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Event not found" in response.json()["detail"]


def test_get_events_by_location(client: TestClient, test_event, test_location):
    response = client.get(f"/api/events/location/{test_location.id}")
    assert response.status_code == status.HTTP_200_OK
    events = response.json()
    assert any(event["id"] == test_event.id for event in events)


def test_get_events_by_organizer(client: TestClient, test_event, test_organizer):
    response = client.get(f"/api/events/organizer/{test_organizer.id}")
    assert response.status_code == status.HTTP_200_OK
    events = response.json()
    assert any(event["id"] == test_event.id for event in events)
