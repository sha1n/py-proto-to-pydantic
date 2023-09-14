import uuid

from tests.conftest import ITContext


def test_http_get_unauthenticated(context: ITContext):
    response = context.client.get(url=f"/api/{uuid.uuid4()}")

    assert response.status_code == 401


def test_http_get_authenticated(context: ITContext):
    response = context.client.get(url=f"/api/{uuid.uuid4()}", auth=context.basic_auth)

    assert response.status_code == 404
