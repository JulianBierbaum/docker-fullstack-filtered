import pytest
from sqlalchemy.orm import Session

from app.crud.user import (
    authenticate_user,
    create_user,
    get_user,
    get_user_by_email,
    get_users,
    update_user,
)
from app.exceptions.user import (
    DuplicateEmailException,
    MissingUserException,
)
from app.models.enums import UserRole
from app.schemas.user import UserCreate, UserUpdate


def test_get_user_success(db: Session, test_superuser):
    result = get_user(db=db, user_id=test_superuser.id)
    assert result is not None
    assert result.id == test_superuser.id
    assert result.username == "superuser"


def test_get_user_not_found(db: Session):
    with pytest.raises(MissingUserException):
        get_user(db=db, user_id=999)


def test_get_user_by_email_success(db: Session, test_superuser):
    result = get_user_by_email(db=db, email=test_superuser.email)
    assert result is not None
    assert result.email == test_superuser.email


def test_get_user_by_email_not_found(db: Session):
    result = get_user_by_email(db=db, email="nonexistent@example.com")
    assert result is None


def test_get_users(db: Session, test_superuser, test_organizer, test_visitor):
    _ = test_superuser
    _ = test_visitor
    _ = test_organizer
    result = get_users(db=db)
    assert len(result) == 3


def test_create_user_success(db: Session):
    user_data = UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="password123",
        role=UserRole.VISITOR,
    )
    result = create_user(db=db, user=user_data)
    assert result is not None
    assert result.username == "newuser"
    assert result.role == UserRole.VISITOR.value


def test_create_duplicate_email(db: Session, test_superuser):
    user_data = UserCreate(
        username="anotheruser",
        email=test_superuser.email,
        password="password123",
        role=UserRole.VISITOR,
    )
    with pytest.raises(DuplicateEmailException):
        create_user(db=db, user=user_data)


def test_update_user_success(db: Session, test_visitor):
    update_data = UserUpdate(username="updateduser", role=UserRole.ORGANIZER)
    result = update_user(db=db, user=update_data, user_id=test_visitor.id)
    assert result is not None
    assert result.username == "updateduser"
    assert result.role == UserRole.ORGANIZER.value


def test_update_user_not_found(db: Session):
    update_data = UserUpdate(username="nonexistent")
    with pytest.raises(MissingUserException):
        update_user(db=db, user=update_data, user_id=999)


def test_update_user_duplicate_email(db: Session, test_visitor, test_organizer):
    update_data = UserUpdate(email=test_organizer.email)
    with pytest.raises(DuplicateEmailException):
        update_user(db=db, user=update_data, user_id=test_visitor.id)


def test_authenticate_user_success(db: Session, test_superuser):
    authenticated_user = authenticate_user(
        db=db, email=test_superuser.email, password="Kennwort1"
    )
    assert authenticated_user is not None
    assert authenticated_user.email == test_superuser.email


def test_authenticate_user_wrong_password(db: Session, test_superuser):
    authenticated_user = authenticate_user(
        db=db, email=test_superuser.email, password="wrongpassword"
    )
    assert authenticated_user is None


def test_authenticate_user_not_found(db: Session):
    authenticated_user = authenticate_user(
        db=db, email="nonexistent@example.com", password="password"
    )
    assert authenticated_user is None
