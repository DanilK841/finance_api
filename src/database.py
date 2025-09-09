import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from passlib.context import CryptContext



class Base(DeclarativeBase): pass

sqlite_file_name = "finuser:pas1@localhost:5432/mydb"
# DATABASE_URL = os.getenv(
#     "DATABASE_URL",
#     "postgresql+asyncpg:///{sqlite_file_name}"
#     )

DATABASE_URL = "postgresql+asyncpg://finuser:pas1@localhost:5432/mydb"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=0
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


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

# Настройка хеширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)




