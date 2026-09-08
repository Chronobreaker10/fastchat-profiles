from fastapi import status
from httpx import AsyncClient
from models import Profile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def test_create_profile(client: AsyncClient, session: AsyncSession) -> None:
    profile_data = {
        "user_id": 1,
    }
    response = await client.post(
        "/profiles/",
        json=profile_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    profile = await session.scalar(select(Profile).filter_by(user_id=1))
    assert profile.user_id == 1


async def test_create_exists_profile(
    client: AsyncClient, test_profile: Profile
) -> None:
    profile_data = {
        "user_id": 1,
    }
    response = await client.post(
        "/profiles/",
        json=profile_data,
    )
    assert response.status_code == status.HTTP_409_CONFLICT
