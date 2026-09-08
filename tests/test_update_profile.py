from fastapi import status
from httpx import AsyncClient
from models import Profile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def test_update_profile(
    client: AsyncClient,
    session: AsyncSession,
    test_profile: Profile,
) -> None:
    data = {"first_name": "Tom", "is_private": False}
    response = await client.patch(
        f"/profiles/{test_profile.user_id}",
        json=data,
    )
    assert response.status_code == status.HTTP_200_OK
    result = await session.execute(
        select(Profile.first_name, Profile.is_private).where(
            Profile.user_id == test_profile.user_id
        )
    )
    profile_from_db = result.mappings().one()
    assert profile_from_db == data
