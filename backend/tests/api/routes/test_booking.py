from fastapi import status
from fastapi.testclient import TestClient

from app.models.booking import Booking


def test_get_bookings_admin(client_with_superuser: TestClient, test_booking):
    response = client_with_superuser.get("/api/bookings/")
    assert response.status_code == status.HTTP_200_OK
    bookings = response.json()
    assert any(
        booking["booking_number"] == test_booking.booking_number for booking in bookings
    )


def test_get_bookings_unauthorized_visitor(
    client_with_visitor: TestClient, test_booking
):
    _ = test_booking
    response = client_with_visitor.get("/api/bookings/")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_bookings_me(client_with_visitor: TestClient, test_booking):
    response = client_with_visitor.get("/api/bookings/me")
    assert response.status_code == status.HTTP_200_OK
    bookings = response.json()
    assert any(
        booking["booking_number"] == test_booking.booking_number for booking in bookings
    )


def test_get_booking_admin(client_with_superuser: TestClient, test_booking):
    response = client_with_superuser.get(f"/api/bookings/{test_booking.booking_number}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["booking_number"] == test_booking.booking_number


def test_get_booking_unauthorized_visitor(
    client_with_visitor: TestClient, test_booking
):
    response = client_with_visitor.get(f"/api/bookings/{test_booking.booking_number}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_booking_missing(client_with_superuser: TestClient):
    response = client_with_superuser.get("/api/bookings/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Booking not found" in response.json()["detail"]


def test_book_event_success(client_with_visitor: TestClient, db, test_event):
    _ = db
    response = client_with_visitor.post(f"/api/bookings/event/{test_event.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["ticket_id"] is not None
    assert response.json()["user_id"] is not None


def test_book_event_not_found(client_with_visitor: TestClient):
    response = client_with_visitor.post("/api/bookings/event/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_bookings_by_event_organizer(
    client_with_organizer: TestClient, test_booking, test_event
):
    response = client_with_organizer.get(f"/api/bookings/event/{test_event.id}")
    assert response.status_code == status.HTTP_200_OK
    bookings = response.json()
    assert any(
        booking["booking_number"] == test_booking.booking_number for booking in bookings
    )


def test_get_bookings_by_event_admin(
    client_with_superuser: TestClient, test_booking, test_event
):
    response = client_with_superuser.get(f"/api/bookings/event/{test_event.id}")
    assert response.status_code == status.HTTP_200_OK
    bookings = response.json()
    assert any(
        booking["booking_number"] == test_booking.booking_number for booking in bookings
    )


def test_get_bookings_by_event_unauthorized_visitor(
    client_with_visitor: TestClient, test_booking, test_event
):
    _ = test_booking
    response = client_with_visitor.get(f"/api/bookings/event/{test_event.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_own_booking_success(client_with_visitor: TestClient, db, test_booking):
    booking_number = test_booking.booking_number
    response = client_with_visitor.delete(f"/api/bookings/me/{booking_number}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["booking_number"] == booking_number
    assert (
        db.query(Booking).filter(Booking.booking_number == booking_number).first()
        is None
    )


def test_delete_own_booking_not_own(client_with_organizer: TestClient, test_booking):
    response = client_with_organizer.delete(
        f"/api/bookings/me/{test_booking.booking_number}"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "You can only delete your own bookings" in response.json()["detail"]


def test_delete_own_booking_missing(client_with_visitor: TestClient):
    response = client_with_visitor.delete("/api/bookings/me/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_booking_admin(
    client_with_superuser: TestClient, db, test_booking, test_ticket
):
    _ = db
    data = {"ticket_id": test_ticket.id}
    response = client_with_superuser.put(
        f"/api/bookings/{test_booking.booking_number}", json=data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["ticket_id"] == test_ticket.id


def test_update_booking_unauthorized_visitor(
    client_with_visitor: TestClient, test_booking, test_ticket
):
    data = {"ticket_id": test_ticket.id}
    response = client_with_visitor.put(
        f"/api/bookings/{test_booking.booking_number}", json=data
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_booking_missing(client_with_superuser: TestClient, test_ticket):
    data = {"ticket_id": test_ticket.id}
    response = client_with_superuser.put("/api/bookings/9999", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_booking_admin(client_with_superuser: TestClient, db, test_booking):
    booking_number = test_booking.booking_number
    response = client_with_superuser.delete(f"/api/bookings/{booking_number}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["booking_number"] == booking_number
    assert (
        db.query(Booking).filter(Booking.booking_number == booking_number).first()
        is None
    )


def test_delete_booking_unauthorized_visitor(
    client_with_visitor: TestClient, test_booking
):
    response = client_with_visitor.delete(
        f"/api/bookings/{test_booking.booking_number}"
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_booking_missing(client_with_superuser: TestClient):
    response = client_with_superuser.delete("/api/bookings/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_bookings_by_user_admin(
    client_with_superuser: TestClient, test_booking, test_visitor
):
    response = client_with_superuser.get(f"/api/bookings/user/{test_visitor.id}")
    assert response.status_code == status.HTTP_200_OK
    bookings = response.json()
    assert any(
        booking["booking_number"] == test_booking.booking_number for booking in bookings
    )


def test_get_bookings_by_user_unauthorized_visitor(
    client_with_visitor: TestClient, test_booking, test_visitor
):
    _ = test_booking
    response = client_with_visitor.get(f"/api/bookings/user/{test_visitor.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_bookings_by_ticket_admin(
    client_with_superuser: TestClient, test_booking, test_ticket
):
    response = client_with_superuser.get(f"/api/bookings/ticket/{test_ticket.id}")
    assert response.status_code == status.HTTP_200_OK
    bookings = response.json()
    assert any(
        booking["booking_number"] == test_booking.booking_number for booking in bookings
    )


def test_get_bookings_by_ticket_unauthorized_visitor(
    client_with_visitor: TestClient, test_booking, test_ticket
):
    _ = test_booking
    response = client_with_visitor.get(f"/api/bookings/ticket/{test_ticket.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
