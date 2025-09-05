import redis.asyncio as redis
from contextlib import asynccontextmanager

REDIS_URL = "redis://localhost:6379"

async def init_redis():
    return await redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

@asynccontextmanager
async def get_redis():
    client = await init_redis()
    try:
        yield client
    finally:
        await client.aclose()