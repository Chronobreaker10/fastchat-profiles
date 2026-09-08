from __future__ import annotations

from config import settings
from redis.asyncio import Redis
from schemas import ProfileRead


class ProfileCache:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, user_id: int) -> ProfileRead | None:
        profile_key = f"{settings.cache_config.profiles_key_prefix}:{user_id}"
        data = await self.redis.get(profile_key)
        if data is not None:
            return ProfileRead.model_validate_json(data)
        return None

    async def put(self, user_id: int, profile: ProfileRead) -> None:
        profile_key = f"{settings.cache_config.profiles_key_prefix}:{user_id}"
        await self.redis.set(
            profile_key,
            profile.model_dump_json(),
            ex=settings.cache_config.profiles_ttl,
        )

    async def delete(self, user_id: int) -> None:
        profile_key = f"{settings.cache_config.profiles_key_prefix}:{user_id}"
        await self.redis.delete(profile_key)
