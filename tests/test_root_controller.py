import uuid

import pytest

from tests.conftest import ITContext


@pytest.mark.it
class TestRootController:
    def test_http_get_unauthenticated(self, context: ITContext):
        response = context.client.get(url=f"/api/{uuid.uuid4()}")

        assert response.status_code == 401

    def test_http_get_authenticated(self, context: ITContext):
        response = context.client.get(url=f"/api/{uuid.uuid4()}", auth=context.basic_auth)

        assert response.status_code == 404

    def test_http_get_root_resource(self, context: ITContext):
        response = context.client.get(url="/", auth=context.basic_auth)

        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}

