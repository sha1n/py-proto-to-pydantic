import base64
import binascii
from typing import Callable, Awaitable, Optional, Tuple

from starlette.authentication import AuthenticationBackend, SimpleUser, AuthenticationError, AuthCredentials, BaseUser
from starlette.requests import HTTPConnection


class BasicAuthBackend(AuthenticationBackend):
    def __init__(self, is_allowed: Callable[[str, str], Awaitable[bool]]):
        self._is_allowed = is_allowed

    async def authenticate(self, conn: HTTPConnection) -> Optional[Tuple[AuthCredentials, BaseUser]]:
        if "Authorization" not in conn.headers:
            return

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() == "basic":
                decoded = base64.b64decode(credentials).decode("utf-8")
                username, _, password = decoded.partition(":")
                if await self._is_allowed(username, password):
                    return AuthCredentials(), SimpleUser(username=username)

        except (ValueError, binascii.Error, UnicodeDecodeError) as error:
            raise AuthenticationError("Invalid basic auth credentials") from error
