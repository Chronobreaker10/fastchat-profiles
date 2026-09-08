from __future__ import annotations

from models import Profile
from schemas import ProfileCreate, ProfileUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ProfileRepository:
    @staticmethod
    async def get_by_user_id(session: AsyncSession, user_id: int) -> Profile | None:
        result = await session.execute(
            select(Profile).where(Profile.user_id == user_id),
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: ProfileCreate) -> Profile:
        instance = Profile(**data.model_dump())
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    @staticmethod
    async def update(
        session: AsyncSession,
        user_id: int,
        data: ProfileUpdate,
    ) -> Profile | None:
        profile = await ProfileRepository.get_by_user_id(session, user_id)
        if profile is None:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
        await session.flush()
        await session.refresh(profile)
        return profile
