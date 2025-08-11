from fastapi import APIRouter, Depends
from typing import Annotated
from src.routers.dependencies import SessionDep
from src.schemas.users import UserCreate, UserOut
from src.models.users import User
from src.routers.oauth2 import get_current_user
from src.utils.utils import hash_password


router = APIRouter(prefix='/users')


@router.post('', response_model=UserOut, status_code=201)
async def create_user(user: UserCreate, session: SessionDep):
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, password=hashed_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@router.get('/me', response_model=UserOut)
async def get_current_user(current_user: Annotated[UserOut, Depends(get_current_user)]):
    return current_user