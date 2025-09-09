from datetime import datetime
from http.client import HTTPException
from sqlalchemy import select, update, delete
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from typing_extensions import Annotated, Optional
from datetime import datetime, timedelta, timezone

from src.database import get_db

from src.transactions.models import Transactions
from src.users.models import Users
from src.users.schemas import UserResponse, UserCreate, UserUpdate



router = APIRouter(prefix='/user', tags=['ПОЛЬЗОВАТЕЛИ'])
# tags - for documentation
# prefix - for url



@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, session: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = Users(
        name=user.name,
        password=hashed_password,
        email=user.email
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)


    return db_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate, session: Session = Depends(get_db)):

    user_db = await session.get(Users,user_id)
    name = user.name if user.name else user_db.name
    email = user.email if user.email else user_db.email
    password = get_password_hash(user.password) if user.password else user_db.password

    update_stmt = update(Users).where(Users.id == user_id).values(
            name= name,
            password= password,
            email= email,
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
    print("PRINTPRINTPRINT11111")
    user_db = await session.execute(select(Users))
    print("PRINTPRINTPRINT")
    print(user_db.all())
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