from datetime import datetime
from http.client import HTTPException

from fastapi import APIRouter, Depends
from sqlalchemy import update
from sqlalchemy.orm import Session

from transactions.models import Transactions
from users.models import Users
from users.schemas import UserResponse, UserCreate, UserUpdate
from database import get_db, get_password_hash

router = APIRouter(prefix='/user', tags=['ПОЛЬЗОВАТЕЛИ'])
# tags - for documentation
# prefix - for url


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, session: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = Users(
        name=user.name,
        password=hashed_password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, session: Session = Depends(get_db)):

    user_db = session.query(Users).filter(Users.id == user_id).first()
    name = user.name if user.name else user_db.name
    password = get_password_hash(user.password) if user.password else user_db.password

    update_stmt = update(Users).where(Users.id == user_id).values(
            name= name,
            password= password,
            updated_at= datetime.utcnow()
    )
    session.execute(update_stmt)
    session.commit()
    session.refresh(user_db)
    return user_db

@router.get("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, session: Session = Depends(get_db)):
    user_db = session.query(Users).filter(Users.id == user_id).first()
    return user_db

@router.get("/all/", response_model=list[UserResponse])
def update_user(session: Session = Depends(get_db)):
    user_db = session.query(Users).all()
    return user_db


@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_db)):
    db_trans = session.query(Transactions).filter(Transactions.user_id == user_id)
    if db_trans:
        HTTPException(status_code=404, detail="Exist transactions with this user")

    db_user = session.query(Users).filter(Users.id == user_id).first()
    session.delete(db_user)
    session.commit()
    return {"msg":f"Delete user with name {db_user.name} succes"}