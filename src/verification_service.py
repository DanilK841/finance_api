import random
from datetime import timedelta


class VerificationService:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def generate_code(self, email: str) -> str:
        code = str(random.randint(100000, 999999))
        await self.redis.setex(
            f"verify:{email}",
            timedelta(minutes=15),
            code
        )
        return code

    async def verify_code(self, email: str, code: str) -> bool:
        stored_code = await self.redis.get(f"verify:{email}")
        if not stored_code:
            return False

        if stored_code != code:
            return False

        await self.redis.delete(f"verify:{email}")
        return True