from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.crud.user import get_user_by_email
from app.database.session import engine
from app.models.enums import UserRole
from app.schemas.token import TokenData
from app.schemas.user import User


# Database Session
def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a SQLAlchemy session.

    This function is a generator that yields a SQLAlchemy session object.
    It ensures that the session is properly closed after use.

    Yields:
        Session: A SQLAlchemy session object.
    """
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

# Security
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")

TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_token_data(token: TokenDep) -> TokenData:
    """
    Retrieve the current user based on the provided session and token.

    Args:
        session (SessionDep): The database session dependency.
        token (TokenDep): The JWT token dependency.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the token is invalid, credentials cannot be validated,
                       the user is not found, or the user is inactive.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        username = payload.get("sub")
        role = payload.get("role")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return TokenData(username=username, role=role)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def get_current_user(session: SessionDep, token_data: TokenData = Depends(get_token_data)) -> User:
    """
    Retrieve the current user from the database using valid token data.
    """
    assert token_data.username is not None
    user = get_user_by_email(db=session, email=token_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def roles_required(allowed_roles: list[UserRole]):
    """
    Checks if the current user is authorized based on the JWT token role.
    """
    def role_checker(token_data: TokenData = Depends(get_token_data)):
        if token_data.role is None:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate role",
            )
        
        if not any(token_data.role == role.value for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user doesn't have enough privileges",
            )
        return token_data

    return role_checker
