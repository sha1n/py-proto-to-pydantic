import base64
import binascii
import logging
from abc import ABC, abstractmethod
from typing import Iterable, Optional, Set, Tuple

from fastapi import FastAPI
from pydantic import FieldValidationInfo, field_validator
from pydantic.dataclasses import dataclass
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError, BaseUser, SimpleUser
from starlette.datastructures import URL
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import HTTPConnection
from starlette.responses import Response

__logger = logging.getLogger(__name__)


@dataclass(frozen=True, eq=True)
class UserCredentials:
    username: str
    password: str

    @field_validator("username", "password")
    @classmethod
    def not_be_empty(cls, value: str, info: FieldValidationInfo) -> str:
        if not value:
            raise ValueError(f"'{info.field_name}' must not be empty")
        return value


class UnauthorizedError(AuthenticationError):
    def __init__(self):
        super().__init__("Unauthorized")


class InvalidAuthorizationError(AuthenticationError):
    def __init__(self):
        super().__init__("Invalid Authorization Header")


class AccessGuard(ABC):
    @abstractmethod
    async def is_allowed(self, url: URL, user_credentials: UserCredentials) -> bool:
        pass


class AlwaysAllowAccessGuard(AccessGuard):
    async def is_allowed(self, url: URL, user_credentials: UserCredentials) -> bool:
        return True


class UserListAccessGuard(AccessGuard):
    def __init__(self, allowed_users: Iterable[UserCredentials] = ()):
        self._allowed_users: Set[UserCredentials] = set(allowed_users)

    async def is_allowed(self, url: URL, user_credentials: UserCredentials) -> bool:
        return user_credentials in self._allowed_users


class BasicAuthBackend(AuthenticationBackend):
    RESPONSE_HEADERS = {"WWW-Authenticate": 'Basic realm="Authentication Required"'}
    AUTHORIZATION_HEADER_NAME = "Authorization"

    def __init__(self, access_guard: AccessGuard):
        self._access_guard = access_guard

    async def authenticate(self, conn: HTTPConnection) -> Optional[Tuple[AuthCredentials, BaseUser]]:
        if self.AUTHORIZATION_HEADER_NAME not in conn.headers:
            raise UnauthorizedError()

        auth = conn.headers.get(self.AUTHORIZATION_HEADER_NAME)
        try:
            scheme, credentials = auth.split()  # type: ignore
            if scheme.lower() == "basic":
                decoded = base64.b64decode(credentials).decode("utf-8")
                username, _, password = decoded.partition(":")
                user_credentials = UserCredentials(username=username, password=password)

                if await self._access_guard.is_allowed(url=conn.url, user_credentials=user_credentials):
                    return AuthCredentials(), SimpleUser(username=username)

        except (ValueError, binascii.Error, UnicodeDecodeError) as error:
            raise InvalidAuthorizationError() from error

        except Exception as error:
            raise AuthenticationError() from error

        raise UnauthorizedError()

    @classmethod
    # pylint: disable=unused-argument
    def on_auth_error_callback(cls, connection: HTTPConnection, exception: Exception) -> Response:
        if isinstance(exception, UnauthorizedError):
            return Response(
                content=str(exception),
                status_code=401,
                headers=cls.RESPONSE_HEADERS,
            )

        if isinstance(exception, InvalidAuthorizationError):
            return Response(
                content=str(exception),
                status_code=400,
            )

        __logger.exception(exception)
        return Response(content="Internal Server Error", status_code=500)


def add_basic_auth_middleware(app: FastAPI, access_guard: AccessGuard):
    app.add_middleware(
        middleware_class=AuthenticationMiddleware,
        backend=BasicAuthBackend(access_guard=access_guard),
        on_error=BasicAuthBackend.on_auth_error_callback,
    )
