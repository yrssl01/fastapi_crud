from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from typing import Annotated
from src.routers.dependencies import SessionDep
from src.schemas.auth import Token
from src.models.users import User as UserModel
from src.utils.utils import verify_password
from src.routers.oauth2 import create_access_token


router = APIRouter()


@router.post('/login')
async def login(user_cred: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> Token:
    query  = await session.execute(select(UserModel).where(UserModel.email == user_cred.username))
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )
    if not verify_password(user_cred.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
        )
    access_token = create_access_token(data = {"username": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
                