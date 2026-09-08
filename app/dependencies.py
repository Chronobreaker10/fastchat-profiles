from __future__ import annotations

from datetime import datetime
from functools import cache
from typing import Annotated

from cache import ProfileCache
from config import settings
from database import db_helper
from errors import ForbiddenError, UnauthorizedError
from fastapi import Cookie, Depends
from fastapi.security import APIKeyHeader
from redis.asyncio import Redis
from repository import ProfileRepository
from schemas import User
from security import validate_token
from service import ProfileService
from sqlalchemy.ext.asyncio import AsyncSession

api_key_header = APIKeyHeader(name=settings.security.api_key_header, auto_error=False)


@cache
def get_redis() -> Redis:
    return Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
        decode_responses=True,
    )


async def get_profile_service(
    session: SessionDep,
    profile_repo: Annotated[ProfileRepository, Depends()],
    profile_cache: ProfileCacheDep,
) -> ProfileService:
    return ProfileService(profile_repo, profile_cache, session)


async def check_api_key(api_key: Annotated[str, Depends(api_key_header)]) -> None:
    if api_key != settings.security.api_key:
        raise ForbiddenError


async def get_current_user(
    auth_cookie: Annotated[
        str | None, Cookie(alias=settings.security.access_token_cookie_name)
    ] = None,
) -> User:
    if auth_cookie is None:
        raise UnauthorizedError
    token_data = validate_token(auth_cookie)
    if token_data.username is None or token_data.user_registered_at is None:
        raise UnauthorizedError
    return User(
        id=int(token_data.sub),
        username=token_data.username,
        created_at=datetime.fromisoformat(token_data.user_registered_at),
    )


async def get_profile_cache(redis: RedisDep) -> ProfileCache:
    return ProfileCache(redis)


SessionDep = Annotated[AsyncSession, Depends(db_helper.get_session)]
ProfileServiceDep = Annotated[ProfileService, Depends(get_profile_service)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
RedisDep = Annotated[Redis, Depends(get_redis)]
ProfileCacheDep = Annotated[ProfileCache, Depends(get_profile_cache)]
