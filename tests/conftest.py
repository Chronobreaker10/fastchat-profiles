from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime
from typing import Any

import pytest
from config import settings
from database import db_helper
from dependencies import check_api_key, get_current_user, get_redis
from fakeredis import FakeAsyncRedis
from httpx import ASGITransport, AsyncClient
from main import app
from models import Base, Profile
from redis.asyncio import Redis
from schemas import User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
session_factory = async_sessionmaker(
    bind=test_engine, autoflush=False, autocommit=False, expire_on_commit=False
)


@pytest.fixture(autouse=True, scope="function")
async def setup_database() -> AsyncGenerator[None]:
    """Создает и очищает БД для каждого теста"""
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture(name="session")
async def get_session_override() -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        yield session


@pytest.fixture(name="redis")
def get_fake_redis() -> Redis:
    return FakeAsyncRedis(decode_responses=True)


@pytest.fixture(name="client")
async def test_client(
    session: AsyncSession, redis: Redis
) -> AsyncGenerator[AsyncClient, Any]:
    app.dependency_overrides[db_helper.get_session] = lambda: session
    app.dependency_overrides[get_current_user] = lambda: User(
        id=1,
        username="johndoe",
        created_at=datetime.now(UTC),
    )
    app.dependency_overrides[check_api_key] = lambda: None
    app.dependency_overrides[get_redis] = lambda: redis
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=f"http://testhost{settings.api_config.prefix}",
    ) as client:
        yield client
    app.dependency_overrides.clear()


@asynccontextmanager
async def _create_profile(
    user_id: int,
    first_name: str,
    last_name: str,
    date_of_birth: date,
    email: str,
    is_private: bool,
    session: AsyncSession,
) -> AsyncGenerator[Profile, Any]:
    test_profile = Profile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        email=email,
        is_private=is_private,
    )
    session.add(test_profile)
    await session.flush()
    try:
        yield test_profile
    finally:
        await session.rollback()


@pytest.fixture(scope="function", name="test_profile")
async def create_test_profile(
    session: AsyncSession, setup_database: None
) -> AsyncGenerator[Profile, Any]:
    async with _create_profile(
        1,
        "John",
        "Doe",
        datetime.now(UTC).date(),
        "john.doe@example.com",
        True,
        session,
    ) as user:
        yield user


@pytest.fixture(scope="function", name="private_profile")
async def create_private_profile(
    session: AsyncSession, setup_database: None
) -> AsyncGenerator[Profile, Any]:
    async with _create_profile(
        2,
        "Bob",
        "Doe",
        datetime.now(UTC).date(),
        "bob.doe@example.com",
        True,
        session,
    ) as user:
        yield user


@pytest.fixture(scope="function", name="public_profile")
async def create_public_profile(
    session: AsyncSession, setup_database: None
) -> AsyncGenerator[Profile, Any]:
    async with _create_profile(
        3,
        "Jack",
        "Doe",
        datetime.now(UTC).date(),
        "jack.doe@example.com",
        False,
        session,
    ) as user:
        yield user
