from typing import Annotated

from dependencies import CurrentUserDep, ProfileServiceDep, check_api_key
from fastapi import APIRouter, Depends, Path, status
from schemas import ProfileCreate, ProfileRead, ProfileUpdate
from utils import add_etag

router = APIRouter(
    prefix="/profiles",
    tags=["Профили"],
)


UserDep = Annotated[
    int,
    Path(
        ge=1,
        title="ID пользователя",
        description="Уникальный идентификатор пользователя",
    ),
]


@router.get(
    "/{user_id}",
    summary="Получение профиля по идентификатору пользователя",
)
@add_etag
async def get_user_profile(
    user_id: UserDep,
    service: ProfileServiceDep,
    current_user: CurrentUserDep,
) -> ProfileRead:
    return await service.get_profile_by_user_id(user_id, current_user)


@router.post(
    "/",
    summary="Создание профиля пользователя",
    response_model=ProfileRead,
    dependencies=[Depends(check_api_key)],
    status_code=status.HTTP_201_CREATED,
)
async def create_user_profile(
    profile_date: ProfileCreate,
    service: ProfileServiceDep,
) -> ProfileRead:
    return await service.create_profile(profile_date)


@router.patch(
    "/{user_id}",
    summary="Обновление профиля пользователя",
    response_model=ProfileRead,
)
async def update_user_profile(
    user_id: UserDep,
    profile_date: ProfileUpdate,
    service: ProfileServiceDep,
    current_user: CurrentUserDep,
) -> ProfileRead:
    return await service.update_profile(user_id, profile_date, current_user)
