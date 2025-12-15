
import pytest
from sqlalchemy.orm import Session
from app.crud.location import (
    create_location,
    delete_location,
    get_location,
    get_locations,
    get_location_by_name,
    update_location,
)
from app.exceptions.location import (
    DuplicateLocationNameException,
    MissingLocationException,
)
from app.schemas.location import LocationCreate, LocationUpdate


def test_get_location_success(db: Session, test_location):
    result = get_location(db=db, location_id=test_location.id)
    assert result is not None
    assert result.id == test_location.id
    assert result.name == "Test Location"


def test_get_location_not_found(db: Session):
    with pytest.raises(MissingLocationException):
        get_location(db=db, location_id=999)


def test_get_location_by_name_success(db: Session, test_location):
    result = get_location_by_name(db=db, location_name=test_location.name)
    assert result is not None
    assert result.name == test_location.name


def test_get_location_by_name_not_found(db: Session):
    result = get_location_by_name(db=db, location_name="nonexistent")
    assert result is None


def test_get_locations(db: Session, test_location):
    result = get_locations(db=db)
    assert len(result) == 1
    assert result[0].id == test_location.id


def test_create_location_success(db: Session):
    location_data = LocationCreate(
        name="New Location", address="456 New Street"
    )
    result = create_location(db=db, location=location_data)
    assert result is not None
    assert result.name == "New Location"


def test_create_duplicate_location_name(db: Session, test_location):
    location_data = LocationCreate(
        name=test_location.name, address="789 Duplicate Street"
    )
    with pytest.raises(DuplicateLocationNameException):
        create_location(db=db, location=location_data)


def test_update_location_success(db: Session, test_location):
    update_data = LocationUpdate(name="Updated Location")
    result = update_location(
        db=db, location=update_data, location_id=test_location.id
    )
    assert result is not None
    assert result.name == "Updated Location"


def test_update_location_not_found(db: Session):
    update_data = LocationUpdate(name="nonexistent")
    with pytest.raises(MissingLocationException):
        update_location(db=db, location=update_data, location_id=999)


def test_delete_location_success(db: Session, test_location):
    result = delete_location(db=db, location_id=test_location.id)
    assert result is not None
    assert result.deleted_at is not None
    with pytest.raises(MissingLocationException):
        get_location(db=db, location_id=test_location.id)


def test_delete_location_not_found(db: Session):
    with pytest.raises(MissingLocationException):
        delete_location(db=db, location_id=999)
