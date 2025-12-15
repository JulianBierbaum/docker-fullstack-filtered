from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.crud import user as crud
from app.schemas import user as schemas
from app.api.deps import SessionDep, roles_required, get_current_user
from app.models.enums import UserRole
from app.models.user import User
from app.exceptions.user import DuplicateEmailException, MissingUserException
from app.exceptions.db import DatabaseException


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.User)
def get_user_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post(
    "/register",
    dependencies=[Depends(roles_required([UserRole.ADMIN]))],
    response_model=schemas.User,
)
def register_user(db: SessionDep, user: schemas.UserCreate):
    try:
        return crud.create_user(db=db, user=user)
    except DuplicateEmailException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/update/{user_id}",
    dependencies=[Depends(roles_required([UserRole.ADMIN]))],
    response_model=schemas.User,
)
def update_user(db: SessionDep, user: schemas.UserUpdate, user_id: int):
    try:
        return crud.update_user(db=db, user=user, user_id=user_id)
    except MissingUserException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateEmailException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{user_id}", response_model=schemas.User)
def get_user(db: SessionDep, user_id: int):
    try:
        return crud.get_user(db=db, user_id=user_id)
    except MissingUserException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/",
    dependencies=[Depends(roles_required([UserRole.ADMIN]))],
    response_model=List[schemas.User],
)
def get_users(db: SessionDep):
    return crud.get_users(db=db)
