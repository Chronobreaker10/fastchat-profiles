from collections.abc import Callable
from contextvars import ContextVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

request_context: ContextVar[Request] = ContextVar("request_context")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        token = request_context.set(request)
        try:
            return await call_next(request)
        finally:
            request_context.reset(token)
