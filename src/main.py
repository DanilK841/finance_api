from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, delete
from database import *
from users.router import router as users_router
from transaction_types.router import router as transaction_types_router
from transactions.router import router as transaction

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
app.include_router(transaction_types_router)
app.include_router(transaction)



# actual - https://fastapi.tiangolo.com/advanced/events/




