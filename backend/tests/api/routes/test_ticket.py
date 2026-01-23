from fastapi import status
from fastapi.testclient import TestClient

from app.models.ticket import Ticket


def test_create_ticket_success(client_with_organizer: TestClient, db, test_event):
    data = {"event_id": test_event.id, "seat_num": "B10", "price": 75.00}
    response = client_with_organizer.post("/api/tickets/", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["seat_num"] == data["seat_num"]

    ticket = db.query(Ticket).filter(Ticket.seat_num == data["seat_num"]).first()
    assert ticket is not None


def test_create_ticket_invalid_event_id(client_with_organizer: TestClient):
    data = {"event_id": 9999, "seat_num": "C1", "price": 25.00}
    response = client_with_organizer.post("/api/tickets/", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Event not found in the db." in response.json()["detail"]


def test_create_ticket_unauthorized_visitor(
    client_with_visitor: TestClient, test_event
):
    data = {"event_id": test_event.id, "seat_num": "X1", "price": 50.00}
    response = client_with_visitor.post("/api/tickets/", json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_tickets_admin(client_with_superuser: TestClient, test_ticket):
    response = client_with_superuser.get("/api/tickets/")
    assert response.status_code == status.HTTP_200_OK
    tickets = response.json()
    assert any(ticket["id"] == test_ticket.id for ticket in tickets)


def test_get_tickets_unauthorized_visitor(client_with_visitor: TestClient):
    response = client_with_visitor.get("/api/tickets/")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]


def test_get_ticket_success(client: TestClient, test_ticket):
    response = client.get(f"/api/tickets/{test_ticket.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_ticket.id
    assert response.json()["seat_num"] == test_ticket.seat_num


def test_get_ticket_missing(client: TestClient):
    response = client.get("/api/tickets/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Ticket not found" in response.json()["detail"]


def test_update_ticket_success_admin(
    client_with_superuser: TestClient, db, test_ticket
):
    updated_price = 100.00
    data = {"price": updated_price}
    response = client_with_superuser.put(f"/api/tickets/{test_ticket.id}", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["price"] == updated_price

    ticket = db.query(Ticket).filter(Ticket.id == test_ticket.id).first()
    assert ticket.price == updated_price


def test_update_ticket_success_organizer(
    client_with_organizer: TestClient, db, test_ticket
):
    updated_seat_num = "D1"
    data = {"seat_num": updated_seat_num}
    response = client_with_organizer.put(f"/api/tickets/{test_ticket.id}", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["seat_num"] == updated_seat_num

    ticket = db.query(Ticket).filter(Ticket.id == test_ticket.id).first()
    assert ticket.seat_num == updated_seat_num


def test_update_ticket_unauthorized_visitor(
    client_with_visitor: TestClient, test_ticket
):
    data = {"price": 10.00}
    response = client_with_visitor.put(f"/api/tickets/{test_ticket.id}", json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]


def test_update_ticket_missing(client_with_superuser: TestClient):
    data = {"price": 5.00}
    response = client_with_superuser.put("/api/tickets/9999", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Ticket not found" in response.json()["detail"]


def test_delete_ticket_success_admin(
    client_with_superuser: TestClient, db, test_ticket
):
    ticket_id = test_ticket.id
    response = client_with_superuser.delete(f"/api/tickets/{ticket_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == ticket_id
    assert db.query(Ticket).filter(Ticket.id == ticket_id).first() is None


def test_delete_ticket_unauthorized_visitor(
    client_with_visitor: TestClient, test_ticket
):
    response = client_with_visitor.delete(f"/api/tickets/{test_ticket.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_ticket_missing(client_with_superuser: TestClient):
    response = client_with_superuser.delete("/api/tickets/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Ticket not found" in response.json()["detail"]


def test_get_tickets_by_event(client: TestClient, test_event, test_ticket):
    response = client.get(f"/api/tickets/event/{test_event.id}")
    assert response.status_code == status.HTTP_200_OK
    tickets = response.json()
    assert any(ticket["id"] == test_ticket.id for ticket in tickets)


def test_get_available_ticket_count_by_event(client: TestClient, test_event):
    response = client.get(f"/api/tickets/event/{test_event.id}/available/count")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), int)
    assert response.json() >= 0
