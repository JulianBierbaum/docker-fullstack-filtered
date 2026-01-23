from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.exceptions.db import DatabaseException
from app.exceptions.user import DuplicateEmailException, MissingUserException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(*, db: Session, user: UserCreate):
    if get_user_by_email(db=db, email=user.email):
        raise DuplicateEmailException(email=user.email)

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        role=user.role.value,
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise DatabaseException(str(e))


def get_user(*, db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise MissingUserException()
    return db_user


def get_users(db: Session):
    return db.query(User).all()


def authenticate_user(*, db: Session, email: str, password: str):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        return None
    if not verify_password(password, str(db_user.hashed_password)):
        return None
    return db_user


def get_user_by_email(*, db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def update_user(*, db: Session, user: UserUpdate, user_id: int):
    db_user = get_user(db=db, user_id=user_id)

    if not db_user:
        raise MissingUserException(user=user.username)

    if get_user_by_email(db=db, email=user.email) and db_user.email != user.email:
        raise DuplicateEmailException(email=user.email)

    try:
        update_data = user.model_dump(exclude_unset=True)
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            del update_data["password"]

        if "role" in update_data:
            update_data["role"] = update_data["role"].value

        for key, value in update_data.items():
            setattr(db_user, key, value)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise DatabaseException(str(e))
