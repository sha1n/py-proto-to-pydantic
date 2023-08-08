import uuid

import pytest

from tests.conftest import ITContext


@pytest.mark.it
class TestRootController:
    def test_http_get_unprotected(self, context: ITContext):
        response = context.client.get(url="/")

        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

    def test_http_get_protected_unauthenticated(self, context: ITContext):
        response = context.client.get(url=f"/api/{uuid.uuid4()}")

        assert response.status_code == 401

    def test_http_get_protected_authenticated(self, context: ITContext):
        response = context.client.get(url=f"/api/{uuid.uuid4()}", auth=(context.username, context.password))

        assert response.status_code == 404
