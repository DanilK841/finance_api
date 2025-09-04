from datetime import datetime
from http.client import HTTPException
from sqlalchemy import select, update, delete

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session
from typing import List
from typing_extensions import Annotated, Optional
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from database import verify_password
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from transactions.models import Transactions
from users.models import Users
from users.schemas import UserResponse, UserCreate, UserUpdate, Token
from database import get_db, get_password_hash


router = APIRouter(prefix='/user', tags=['ПОЛЬЗОВАТЕЛИ'])
# tags - for documentation
# prefix - for url

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "08108f97259f8c8874533f26d9404d680f201ffdf2ee2a2b2ee5d5b5aed9cccf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def authenticate_user(username: str, password: str, session):
    user_stmt = await session.execute(select(Users).where(Users.name == username))
    user = user_stmt.scalar_one_or_none()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        print(username)
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user_stmt = await session.execute(select(Users).where(Users.name==username))
    user = user_stmt.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[Users, Depends(get_current_user)],session):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/about-me", response_model=UserResponse)
async def current_user(current_user: Annotated[Users, Depends(get_current_user)],):
    return current_user



@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, session: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = Users(
        name=user.name,
        password=hashed_password
    )

    print(user.name)

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)


    return db_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate, session: Session = Depends(get_db)):

    user_db = await session.get(Users,user_id)
    name = user.name if user.name else user_db.name
    password = get_password_hash(user.password) if user.password else user_db.password

    update_stmt = update(Users).where(Users.id == user_id).values(
            name= name,
            password= password,
            updated_at= datetime.utcnow()
    )
    await session.execute(update_stmt)
    await session.commit()
    await session.refresh(user_db)
    return user_db

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: Session = Depends(get_db)):
    user_db = await session.get(Users, user_id)
    return user_db

@router.get("/all", response_model=List[UserResponse])
async def get_all_user(session: Session = Depends(get_db)):
    user_db = await session.execute(select(Users))
    return user_db.all()



@router.delete("/{user_id}")
async def delete_user(user_id: int, session: Session = Depends(get_db)):
    db_trans = await session.get(Transactions,user_id)
    if db_trans:
        HTTPException(status_code=404, detail="Exist transactions with this user")

    db_user = await session.get(Users,user_id)
    await session.delete(db_user)
    await session.commit()

    return {"msg":f"Delete user with name {db_user.name} succes"}