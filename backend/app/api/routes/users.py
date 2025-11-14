from typing import List
from fastapi import APIRouter, Depends
from app.crud import user as crud
from app.schemas import user as schemas
from app.api.deps import SessionDep, roles_required
from app.models.enums import UserRole


router = APIRouter()

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=schemas.User)
def register_user(db: SessionDep, user: schemas.UserCreate):
    return crud.create_user(db=db, user=user)


@router.get("/{user_id}", response_model=schemas.User)
def get_user(db: SessionDep, user_id: int):
    return crud.get_user(db=db, user_id=user_id)


@router.get(
    "/",
    dependencies=[Depends(roles_required([UserRole.ADMIN]))],
    response_model=List[schemas.User],
)
# @router.get("/", response_model=List[schemas.User])
def get_users(db: SessionDep):
    return crud.get_users(db=db)
