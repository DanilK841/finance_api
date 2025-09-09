from datetime import datetime
from http.client import HTTPException
from sqlalchemy import select, update, delete
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from typing_extensions import Annotated, Optional
from datetime import datetime, timedelta, timezone

from src.database import get_db

from src.verification_email.service import EmailService
from src.verification_email.redis_util import get_redis
from src.verification_email.verification_service import VerificationService
from src.auth.router import get_current_user
from src.users.models import Users

router = APIRouter(prefix='/verification-email', tags=['ВЕРИФИКАЦИЯ ПОЧТЫ'])

async def get_verification_service() -> VerificationService:
    async with get_redis() as redis_client:
        yield VerificationService(redis_client)

@router.post("/send-code")
async def send_verification_code(
        service_email: Annotated[EmailService, Depends(EmailService)],
        background_tasks: BackgroundTasks,
        current_user: Annotated[Users, Depends(get_current_user)],
        service: VerificationService = Depends(get_verification_service)

):
    email = current_user.email
    code = await service.generate_code(email)

    background_tasks.add_task(service_email.send_email, email, "Verification code", code)

    print(f"Verification code for {email}: {code}")
# тут service это как подключение к redis, а не экземпляр класса?
    return {"message": "Verification code sent"}


@router.post("/verify-email")
async def verify_email(
        current_user: Annotated[Users, Depends(get_current_user)],
        code: str,
        service: VerificationService = Depends(get_verification_service),
        session: Session = Depends(get_db)

):
    email = current_user.email
    is_valid = await service.verify_code(email, code)

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid code")
    current_user.is_active = is_valid
    await session.commit()
    return {"message": "Email verified successfully"}