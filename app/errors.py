from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class BaseHTTPError(Exception):
    code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "Произошла непредвиденная ошибка"
    headers: dict | None = None

    def __init__(self, message: str | None = None) -> None:
        if message is not None:
            self.message = message


class ProfileNotFoundError(BaseHTTPError):
    code: int = status.HTTP_404_NOT_FOUND
    message: str = "Профиль не найден"


class ProfileAlreadyExistsError(BaseHTTPError):
    code: int = status.HTTP_409_CONFLICT
    message: str = "Профиль для этого пользователя уже создан"


class UnauthorizedError(BaseHTTPError):
    code: int = status.HTTP_401_UNAUTHORIZED
    message: str = "Для доступа к ресурсу необходимо авторизоваться"

    def __init__(self) -> None:
        self.headers = {"WWW-Authenticate": "Bearer"}


class ForbiddenError(BaseHTTPError):
    code: int = status.HTTP_403_FORBIDDEN
    message: str = "У вас недостаточно прав для выполнения этого действия"


async def handle_base_http_error(_: Request, exc: BaseHTTPError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.code,
        content={"message": exc.message},
        headers=getattr(exc, "headers", None),
    )


def setup_exceptions(app: FastAPI) -> None:
    app.add_exception_handler(BaseHTTPError, handle_base_http_error)
