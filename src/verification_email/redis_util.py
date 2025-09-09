import redis.asyncio as redis
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")

async def init_redis():
    return await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

@asynccontextmanager
async def get_redis():
    client = await init_redis()
    try:
        yield client
    finally:
        await client.aclose()