import uuid
from dataclasses import dataclass
from typing import Tuple
from unittest.mock import MagicMock, patch

from httpx import BasicAuth
from pytest_asyncio import fixture
from starlette.testclient import TestClient

# pylint: disable=redefined-outer-name,import-outside-toplevel,disable=unused-argument


@dataclass
class ITContext:
    client: TestClient
    basic_auth: BasicAuth


@fixture(scope="session")
def context(client: TestClient, config: Tuple[str, str]) -> ITContext:
    username, password = config
    return ITContext(
        client=client,
        basic_auth=BasicAuth(username=username, password=password),
    )


@fixture(scope="session")
def client() -> TestClient:
    from webapp.server import app

    return TestClient(app)


@fixture(scope="session", autouse=True)
def config() -> Tuple[str, str]:
    username, password = uuid.uuid4().hex, uuid.uuid4().hex

    with patch.dict("os.environ", {"BASIC_AUTH_USERNAME": username, "BASIC_AUTH_PASSWORD": password}):
      yield username, password
