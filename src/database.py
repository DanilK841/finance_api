import os

from sqlalchemy.orm import DeclarativeBase
from passlib.context import CryptContext



class Base(DeclarativeBase): pass

sqlite_file_name = "username:password@localhost:5432/mydatabase"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg:///{sqlite_file_name}"
    )

# Настройка хеширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
