from cache import ProfileCache
from errors import ForbiddenError, ProfileAlreadyExistsError, ProfileNotFoundError
from models import Profile
from repository import ProfileRepository
from schemas import ProfileCreate, ProfileRead, ProfileUpdate, User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


class ProfileService:
    def __init__(
        self, repo: ProfileRepository, cache: ProfileCache, session: AsyncSession
    ) -> None:
        self.repo = repo
        self.cache = cache
        self.session = session

    async def _get_profile_by_user_id(self, user_id: int) -> Profile:
        profile = await self.repo.get_by_user_id(self.session, user_id)
        if profile is None:
            message = f"Профиль пользователя с ID {user_id} не найден"
            raise ProfileNotFoundError(message)
        return profile

    async def _get_profile_from_cache(self, user_id: int) -> ProfileRead:
        cached_profile = await self.cache.get(user_id)
        if cached_profile is not None:
            return cached_profile
        profile = ProfileRead.model_validate(
            await self._get_profile_by_user_id(user_id)
        )
        await self.cache.put(user_id, profile)
        return profile

    async def get_profile_by_user_id(
        self, user_id: int, current_user: User
    ) -> ProfileRead:
        profile = await self._get_profile_from_cache(user_id)
        if profile.is_private and user_id != current_user.id:
            message = "У пользователя закрытый профиль"
            raise ForbiddenError(message)
        return profile

    async def create_profile(self, profile_data: ProfileCreate) -> ProfileRead:
        try:
            profile = await self.repo.create(self.session, profile_data)
            await self.session.commit()
        except IntegrityError:
            raise ProfileAlreadyExistsError
        else:
            return ProfileRead.model_validate(profile)

    async def update_profile(
        self, user_id: int, profile_data: ProfileUpdate, current_user: User
    ) -> None:
        profile = await self._get_profile_by_user_id(user_id)
        if profile.user_id != current_user.id:
            message = "У вас нет прав на редактирования профиля этого пользователя"
            raise ForbiddenError(message)
        await self.repo.update(self.session, user_id, profile_data)
        await self.session.commit()
        await self.cache.delete(user_id)
