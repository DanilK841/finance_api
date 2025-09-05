from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from typing_extensions import Annotated, Optional

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, delete
from database import *
from users.router import authenticate_user, create_access_token, OAuth2PasswordRequestForm, ACCESS_TOKEN_EXPIRE_MINUTES
from users.router import router as users_router
from transaction_types.router import router as transaction_types_router
from transactions.router import router as transaction
from users.schemas import Token
from redis_util import get_redis
from verification_service import VerificationService
from email_service import EmailService

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

@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_db)) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    username = user.name

    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


async def get_verification_service() -> VerificationService:
    async with get_redis() as redis_client:
        yield VerificationService(redis_client)

@app.post("/send-code")
async def send_verification_code(
        service_email: Annotated[EmailService, Depends(EmailService)],
        email: str,
        background_tasks: BackgroundTasks,
        service: VerificationService = Depends(get_verification_service)
):
    code = await service.generate_code(email)

    background_tasks.add_task(service_email.send_email, email, "Verification code", code)

    print(f"Verification code for {email}: {code}")
# тут service это как подключение к redis, а не экземпляр класса?
    return {"message": "Verification code sent"}


@app.post("/verify-email")
async def verify_email(
        email: str,
        code: str,
        service: VerificationService = Depends(get_verification_service)
):
    is_valid = await service.verify_code(email, code)

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid code")

    return {"message": "Email verified successfully"}