from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, delete
from src.database import *
from src.users.router import router as users_router
from src.transaction_types.router import router as transaction_types_router
from src.transactions.router import router as transaction

@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        future=True,
        pool_size=20,
        max_overflow=0
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.state.engine = engine
    app.state.AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
app.include_router(transaction_types_router)
app.include_router(transaction)



# actual - https://fastapi.tiangolo.com/advanced/events/




