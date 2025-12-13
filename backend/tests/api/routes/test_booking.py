from fastapi import status
from app.models.booking import Booking
from fastapi.testclient import TestClient

def test_create_booking_success(client_with_visitor: TestClient, db, test_visitor, test_ticket):
    data = {
        "user_id": test_visitor.id,
        "ticket_id": test_ticket.id
    }
    response = client_with_visitor.post("/api/bookings/", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["user_id"] == data["user_id"]
    assert response.json()["ticket_id"] == data["ticket_id"]
    
    booking = db.query(Booking).filter(Booking.user_id == data["user_id"], Booking.ticket_id == data["ticket_id"]).first()
    assert booking is not None

def test_create_booking_invalid_ticket_id(client_with_visitor: TestClient, test_visitor):
    data = {
        "user_id": test_visitor.id,
        "ticket_id": 9999
    }
    response = client_with_visitor.post("/api/bookings/", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ticket not found in the db." in response.json()["detail"]

def test_get_bookings(client: TestClient, test_booking):
    response = client.get("/api/bookings/")
    assert response.status_code == status.HTTP_200_OK
    bookings = response.json()
    assert any(booking["booking_number"] == test_booking.booking_number for booking in bookings)

def test_get_booking_success(client: TestClient, test_booking):
    response = client.get(f"/api/bookings/{test_booking.booking_number}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["booking_number"] == test_booking.booking_number
    assert response.json()["user_id"] == test_booking.user_id

def test_get_booking_missing(client: TestClient):
    response = client.get("/api/bookings/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Booking not found" in response.json()["detail"]

def test_update_booking_success_admin(client_with_superuser: TestClient, db, test_booking, test_ticket):
    new_ticket = test_ticket # Assuming test_ticket is available and different
    data = {"ticket_id": new_ticket.id}
    response = client_with_superuser.put(f"/api/bookings/{test_booking.booking_number}", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["ticket_id"] == new_ticket.id

    booking = db.query(Booking).filter(Booking.booking_number == test_booking.booking_number).first()
    assert booking.ticket_id == new_ticket.id

def test_update_booking_unauthorized_visitor(client_with_visitor: TestClient, test_booking, test_ticket):
    data = {"ticket_id": test_ticket.id}
    response = client_with_visitor.put(f"/api/bookings/{test_booking.booking_number}", json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]

def test_update_booking_missing(client_with_superuser: TestClient, test_ticket):
    data = {"ticket_id": test_ticket.id}
    response = client_with_superuser.put("/api/bookings/9999", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Booking not found" in response.json()["detail"]

def test_cancel_booking_success_admin(client_with_superuser: TestClient, db, test_booking):
    booking_number = test_booking.booking_number
    response = client_with_superuser.delete(f"/api/bookings/{booking_number}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["booking_number"] == booking_number
    assert response.json()["cancelled_at"] is not None

    booking = db.query(Booking).filter(Booking.booking_number == booking_number).first()
    assert booking.cancelled_at is not None

def test_cancel_booking_unauthorized_visitor(client_with_visitor: TestClient, test_booking):
    response = client_with_visitor.delete(f"/api/bookings/{test_booking.booking_number}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]

def test_cancel_booking_missing(client_with_superuser: TestClient):
    response = client_with_superuser.delete("/api/bookings/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Booking not found" in response.json()["detail"]

def test_get_bookings_by_user(client: TestClient, test_booking, test_visitor):
    response = client.get(f"/api/bookings/user/{test_visitor.id}")
    assert response.status_code == status.HTTP_200_OK
    bookings = response.json()
    assert any(booking["booking_number"] == test_booking.booking_number for booking in bookings)

def test_get_bookings_by_ticket(client: TestClient, test_booking, test_ticket):
    response = client.get(f"/api/bookings/ticket/{test_ticket.id}")
    assert response.status_code == status.HTTP_200_OK
    bookings = response.json()
    assert any(booking["booking_number"] == test_booking.booking_number for booking in bookings)
