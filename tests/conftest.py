import uuid
from dataclasses import dataclass
from typing import Tuple
from unittest.mock import patch, MagicMock

from pytest_asyncio import fixture
from starlette.testclient import TestClient

# pylint: disable=redefined-outer-name,import-outside-toplevel,disable=unused-argument


@dataclass
class ITContext:
    username: str
    password: str
    client: TestClient


@fixture(scope="session")
def context(client: TestClient, _basic_auth_credentials: Tuple[str, str]) -> ITContext:
    username, password = _basic_auth_credentials
    return ITContext(client=client, username=username, password=password)


@fixture(scope="session")
def client(config) -> TestClient:
    from webapp.server import app

    return TestClient(app)


@fixture(scope="session", autouse=True)
def config(_basic_auth_credentials: Tuple[str, str]):
    username, password = _basic_auth_credentials
    with patch.multiple(
        "webapp.config",
        get_basic_auth_username=MagicMock(return_value=username),
        get_basic_auth_password=MagicMock(return_value=password),
    ):
        yield


@fixture(scope="session")
def _basic_auth_credentials() -> Tuple[str, str]:
    yield uuid.uuid4().hex, uuid.uuid4().hex
