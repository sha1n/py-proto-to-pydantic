import os
from dataclasses import dataclass
from typing import Tuple

from faker import Faker
from httpx import BasicAuth
from pytest_asyncio import fixture
from starlette.testclient import TestClient


# pylint: disable=redefined-outer-name,import-outside-toplevel,disable=unused-argument


@dataclass
class ITContext:
    client: TestClient
    basic_auth: BasicAuth
    faker: Faker


@fixture(scope="session")
def context(client: TestClient, config: Tuple[str, str], faker: Faker) -> ITContext:
    username, password = config
    return ITContext(
        client=client,
        basic_auth=BasicAuth(username=username, password=password),
        faker=faker,
    )


@fixture(scope="session")
def client() -> TestClient:
    from webapp.http_server import app

    return TestClient(app)


@fixture(scope="session", autouse=True)
def config(faker: Faker) -> Tuple[str, str]:
    username, password = faker.word(), faker.word()

    os.environ["BASIC_AUTH_USERNAME"] = username
    os.environ["BASIC_AUTH_PASSWORD"] = password

    return username, password


@fixture(scope="session")
def faker() -> Faker:
    return Faker()
