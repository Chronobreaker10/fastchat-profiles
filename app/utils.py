import hashlib
from collections.abc import Callable
from datetime import UTC, datetime
from functools import wraps
from typing import Any

from config import settings
from fastapi import Response, status
from middlewares import request_context
from pydantic import BaseModel


def get_current_naive_dt() -> datetime:
    dt = datetime.now(tz=UTC)
    return dt.replace(microsecond=0, tzinfo=None)


def add_etag(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Response:  # noqa: ANN401
        request = request_context.get()
        content = await func(*args, **kwargs)

        if isinstance(content, Response):
            return content

        if isinstance(content, BaseModel):
            content = content.model_dump_json()

        content_bytes = content.encode("utf-8")
        etag = f'"{hashlib.sha256(content_bytes).hexdigest()}"'
        client_etag = request.headers.get("If-None-Match")

        if client_etag == etag:
            return Response(status_code=status.HTTP_304_NOT_MODIFIED)

        return Response(
            content=content_bytes,
            media_type="application/json",
            headers={
                "ETag": etag,
                "Cache-Control": f"max-age={settings.cache_config.max_age}",
            },
        )

    return wrapper
