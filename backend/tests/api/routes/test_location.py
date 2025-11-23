from fastapi import status
from app.models.location import Location
from fastapi.testclient import TestClient

def test_create_location_success_admin(client_with_superuser: TestClient, db):
    data = {
        "name": "Admin Created Location",
        "address": "Admin Street 1",
        "capacity": 200
    }
    response = client_with_superuser.post("/api/locations/", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == data["name"]
    
    location = db.query(Location).filter(Location.name == data["name"]).first()
    assert location is not None

def test_create_location_unauthorized_visitor(client_with_visitor: TestClient):
    data = {
        "name": "Visitor Attempt Location",
        "address": "Visitor Street 1",
        "capacity": 10
    }
    response = client_with_visitor.post("/api/locations/", json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]

def test_create_location_duplicate_name(client_with_superuser: TestClient, test_location):
    data = {
        "name": test_location.name,
        "address": "Duplicate Street 1",
        "capacity": 150
    }
    response = client_with_superuser.post("/api/locations/", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]

def test_get_locations(client: TestClient, test_location):
    response = client.get("/api/locations/")
    assert response.status_code == status.HTTP_200_OK
    locations = response.json()
    assert any(location["id"] == test_location.id for location in locations)

def test_get_location_success(client: TestClient, test_location):
    response = client.get(f"/api/locations/{test_location.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_location.id
    assert response.json()["name"] == test_location.name

def test_get_location_missing(client: TestClient):
    response = client.get("/api/locations/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Location not found" in response.json()["detail"]

def test_update_location_success_admin(client_with_superuser: TestClient, db, test_location):
    updated_name = "Updated Location Name"
    data = {"name": updated_name}
    response = client_with_superuser.put(f"/api/locations/{test_location.id}", json=data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == updated_name

    location = db.query(Location).filter(Location.id == test_location.id).first()
    assert location.name == updated_name

def test_update_location_unauthorized_visitor(client_with_visitor: TestClient, test_location):
    data = {"name": "Unauthorized Location Update"}
    response = client_with_visitor.put(f"/api/locations/{test_location.id}", json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]

def test_update_location_missing(client_with_superuser: TestClient):
    data = {"name": "Missing Location Update"}
    response = client_with_superuser.put("/api/locations/9999", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Location not found" in response.json()["detail"]

def test_delete_location_success_admin(client_with_superuser: TestClient, db, test_location):
    location_id = test_location.id
    response = client_with_superuser.delete(f"/api/locations/{location_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == location_id
    assert response.json()["deleted_at"] is not None

    location = db.query(Location).filter(Location.id == location_id).first()
    assert location.deleted_at is not None

def test_delete_location_unauthorized_visitor(client_with_visitor: TestClient, test_location):
    response = client_with_visitor.delete(f"/api/locations/{test_location.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]

def test_delete_location_missing(client_with_superuser: TestClient):
    response = client_with_superuser.delete("/api/locations/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Location not found" in response.json()["detail"]
