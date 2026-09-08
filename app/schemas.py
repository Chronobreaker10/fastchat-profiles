from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProfileCreate(BaseModel):
    user_id: Annotated[
        int,
        Field(
            ge=1,
            title="ID пользователя",
            description="Уникальный идентификатор пользователя",
        ),
    ]


class ProfileBase(BaseModel):
    first_name: Annotated[
        str | None,
        Field(
            min_length=1,
            max_length=255,
            title="Имя пользователя",
            description="Имя пользователя",
        ),
    ] = None
    last_name: Annotated[
        str | None,
        Field(
            min_length=1,
            max_length=255,
            title="Фамилия пользователя",
            description="Фамилия пользователя",
        ),
    ] = None
    email: Annotated[
        EmailStr | None,
        Field(
            min_length=5,
            max_length=255,
            title="Email пользователя",
            description="Электронная почта пользователя",
        ),
    ] = None
    date_of_birth: Annotated[
        date | None,
        Field(
            title="Дата рождения пользователя", description="Дата рождения пользователя"
        ),
    ] = None
    about_me: Annotated[
        str | None,
        Field(
            title="О себе",
            description="Дополнительная инфрормация о себе",
            max_length=500,
        ),
    ] = None


class ProfileRead(ProfileBase):
    model_config = ConfigDict(from_attributes=True)
    is_private: Annotated[
        bool, Field(title="Закрытый профиль", description="Закрытый профиль")
    ] = False


class ProfileUpdate(ProfileBase):
    is_private: Annotated[
        bool | None, Field(title="Закрытый профиль", description="Закрытый профиль")
    ] = None


class User(BaseModel):
    id: Annotated[int, Field(ge=1, title="ID", description="ID пользователя")]
    username: Annotated[
        str,
        Field(
            min_length=3,
            max_length=100,
            title="Имя пользователя",
            description="Имя пользователя",
        ),
    ]
    created_at: Annotated[
        datetime,
        Field(
            title="Зарегистрировался",
            description="Зарегистрировался",
        ),
    ]


class TokenData(BaseModel):
    sub: Annotated[int | uuid.UUID, Field(title="Уникальный идентификатор сущности")]
    iss: Annotated[int | None, Field(title="Издатель токена", ge=1)] = None
    username: Annotated[str | None, Field(title="Имя пользователя")] = None
    user_registered_at: Annotated[
        str | None, Field(title="Дата регистрации пользователя")
    ] = None


class MessageResponse(BaseModel):
    message: Annotated[
        str, Field(title="Сообщение ответа", min_length=1, max_length=500)
    ]
