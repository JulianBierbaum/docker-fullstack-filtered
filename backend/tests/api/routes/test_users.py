from fastapi import status
from fastapi.testclient import TestClient

from app.models.user import User


def test_register_user_success_admin(client_with_superuser: TestClient, db):
    user_data = {
        "username": "TestUserReg",
        "email": "userregister@test.com",
        "password": "Kennwort1",
        "role": "visitor",
    }
    response = client_with_superuser.post("/api/users/register", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == user_data["email"]

    user = db.query(User).filter(User.email == user_data["email"]).first()
    assert user is not None
    assert user.username == user_data["username"]


def test_register_user_duplicate_email(client_with_superuser: TestClient, test_visitor):
    user_data = {
        "username": "DuplicateUser",
        "email": test_visitor.email,  # Use an existing email
        "password": "Kennwort1",
        "role": "visitor",
    }
    response = client_with_superuser.post("/api/users/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        f"Email '{test_visitor.email}' already exists in the db."
        in response.json()["detail"]
    )


def test_register_user_unauthorized_visitor(client_with_visitor: TestClient):
    user_data = {
        "username": "UnauthorizedVisitor",
        "email": "unauth_visitor@test.com",
        "password": "Kennwort1",
        "role": "visitor",
    }
    response = client_with_visitor.post("/api/users/register", json=user_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]


def test_get_users_admin(client_with_superuser: TestClient, test_visitor):
    response = client_with_superuser.get("/api/users/")
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert any(user["id"] == test_visitor.id for user in users)


def test_get_users_unauthorized_visitor(client_with_visitor: TestClient):
    response = client_with_visitor.get("/api/users/")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]


def test_get_user_self(client_with_visitor: TestClient, test_visitor):
    response = client_with_visitor.get(f"/api/users/{test_visitor.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_visitor.id
    assert response.json()["email"] == test_visitor.email


def test_get_user_admin(client_with_superuser: TestClient, test_visitor):
    response = client_with_superuser.get(f"/api/users/{test_visitor.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_visitor.id


def test_get_user_other_forbidden(client_with_visitor: TestClient, test_organizer):
    response = client_with_visitor.get(f"/api/users/{test_organizer.id}")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "You can only view your own user info" in response.json()["detail"]


def test_get_user_missing(client_with_superuser: TestClient):
    response = client_with_superuser.get("/api/users/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]


def test_update_user_success_admin(client_with_superuser: TestClient, db, test_visitor):
    updated_username = "UpdatedVisitor"
    data = {"username": updated_username}
    response = client_with_superuser.put(
        f"/api/users/update/{test_visitor.id}", json=data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == updated_username

    user = db.query(User).filter(User.id == test_visitor.id).first()
    assert user.username == updated_username


def test_update_user_duplicate_email(
    client_with_superuser: TestClient, test_visitor, test_organizer
):
    data = {"email": test_organizer.email}
    response = client_with_superuser.put(
        f"/api/users/update/{test_visitor.id}", json=data
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        f"Email '{test_organizer.email}' already exists in the db."
        in response.json()["detail"]
    )


def test_update_user_unauthorized_visitor(
    client_with_visitor: TestClient, test_visitor
):
    data = {"username": "Unauthorized Update"}
    response = client_with_visitor.put(
        f"/api/users/update/{test_visitor.id}", json=data
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "The user doesn't have enough privileges" in response.json()["detail"]


def test_update_user_missing(client_with_superuser: TestClient):
    data = {"username": "Missing User Update"}
    response = client_with_superuser.put("/api/users/update/9999", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "User not found" in response.json()["detail"]
