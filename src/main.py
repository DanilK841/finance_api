from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from typing_extensions import Annotated, Optional

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, delete

from src.database import *

from src.users.router import router as users_router
from src.transaction_types.router import router as transaction_types_router
from src.transactions.router import router as transaction
from src.auth.router import router as auth
from src.verification_email.router import router as verification_email


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()




app = FastAPI(lifespan=lifespan)

# app = FastAPI()
app.include_router(users_router)
app.include_router(transaction_types_router)
app.include_router(transaction)
app.include_router(auth)
app.include_router(verification_email)

