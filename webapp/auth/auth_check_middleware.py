from typing import Callable, Awaitable

from starlette.datastructures import URL
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class AuthenticationCheckMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, is_protected: Callable[[URL], Awaitable[bool]] = lambda _: True):
        super().__init__(app)
        self._is_protected = is_protected

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if self._is_protected(request.url) and not request.user.is_authenticated:
            return Response("Unauthorized", status_code=401)

        response = await call_next(request)

        return response
