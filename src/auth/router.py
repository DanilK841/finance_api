from datetime import datetime
from http.client import HTTPException
from sqlalchemy import select, update, delete
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from typing_extensions import Annotated, Optional
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from database import get_db, get_password_hash, verify_password

from transactions.models import Transactions
from users.models import Users
from users.schemas import UserResponse
from auth.schemas import Token



router = APIRouter(prefix='/auth', tags=['АВТОРИЗАЦИЯ'])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
SECRET_KEY_ACCESS = "08108f97259f8c8874533f26d9404d680f201ffdf2ee2a2b2ee5d5b5aed9cccf"
SECRET_KEY_REFRESH = "f901c42e07a0388d515f569d2d3b1bcbf1eb6dc4608e22ed63eac49e51e41249"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 3

async def authenticate_user(username: str, password: str, session):
    user = (await session.execute(select(Users).where(Users.name == username))).scalar_one_or_none()

    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

async def get_user(username:str, session):
    user_stmt = await session.execute(select(Users).where(Users.name == username))
    user = user_stmt.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Could not find user")
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY_ACCESS, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return await get_user(username=username, session=session)

async def get_current_active_user(current_user: Annotated[Users, Depends(get_current_user)],session):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def create_token(data: dict, SECRET_KEY: str, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_db)) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    username = user.name

    print(username)

    access_token = create_token(
        data={"sub": username}, SECRET_KEY=SECRET_KEY_ACCESS, expires_delta=access_token_expires
    )
    refresh_token = create_token(
        data={"sub": username}, SECRET_KEY=SECRET_KEY_REFRESH, expires_delta=refresh_token_expires
    )
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/refresh", response_model=Token)
async def refresh_token_get_access(refresh_token: str, session: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token,SECRET_KEY_REFRESH,algoritms=ALGORITHM)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user = await get_user(username=username, session=session)
    if user is None:
        raise HTTPException(status_code=401, detail="Couldnt find user")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_token(
        data={"sub": username}, SECRET_KEY=SECRET_KEY_ACCESS, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


@router.post("/about-me", response_model=UserResponse)
async def current_user(current_user: Annotated[Users, Depends(get_current_user)],):
    return current_user