from config import settings
from fastapi import status
from httpx import AsyncClient
from models import Profile
from redis.asyncio import Redis


async def test_get_profile(
    client: AsyncClient,
    test_profile: Profile,
    redis: Redis,
) -> None:
    cache_key = f"{settings.cache_config.profiles_key_prefix}:{test_profile.user_id}"
    assert await redis.get(cache_key) is None
    response = await client.get(
        f"/profiles/{test_profile.user_id}",
    )
    assert response.status_code == status.HTTP_200_OK
    profile = response.json()
    assert profile["first_name"] == test_profile.first_name
    assert profile["last_name"] == test_profile.last_name
    assert profile["date_of_birth"] == str(test_profile.date_of_birth)
    assert profile["email"] == test_profile.email
    assert profile["about_me"] == test_profile.about_me
    assert await redis.get(cache_key) is not None


async def test_get_private_profile(
    client: AsyncClient,
    private_profile: Profile,
) -> None:
    response = await client.get(
        f"/profiles/{private_profile.user_id}",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_get_not_exists_profile(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/profiles/1",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_public_profile(
    client: AsyncClient,
    public_profile: Profile,
) -> None:
    response = await client.get(
        f"/profiles/{public_profile.user_id}",
    )
    assert response.status_code == status.HTTP_200_OK
    chat = response.json()
    assert chat["first_name"] == public_profile.first_name
    assert chat["last_name"] == public_profile.last_name
    assert chat["date_of_birth"] == str(public_profile.date_of_birth)
    assert chat["email"] == public_profile.email
    assert chat["about_me"] == public_profile.about_me
