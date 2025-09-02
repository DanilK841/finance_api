from fastapi import FastAPI, Depends, HTTPException

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, delete
from database import *
from classes import *
from src.users.router import router as users_router
from src.transaction_types.router import router as transaction_types_router
from src.transactions.router import router as transaction

app = FastAPI()
app.include_router(users_router)
app.include_router(transaction_types_router)
app.include_router(transaction)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
# устарело
# actual - https://fastapi.tiangolo.com/advanced/events/




