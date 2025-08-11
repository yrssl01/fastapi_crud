import jwt
from jwt.exceptions import InvalidTokenError
from typing import Annotated
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from src.models.users import User as UserModel
from src.routers.dependencies import SessionDep
from src.schemas.auth import TokenData
from src.config import Settings

settings = Settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, creds_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = str(payload.get("username"))
        if username is None: 
            raise creds_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise creds_exception
    

    return token_data


async def get_current_user(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]):
    creds_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token = verify_access_token(token, creds_exception)

    query = await session.execute(select(UserModel).where(UserModel.email == token.username))
    user = query.scalar_one_or_none()
    
    return user

