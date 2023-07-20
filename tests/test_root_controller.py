from fastapi.testclient import TestClient
import pytest
from myapp import server


@pytest.mark.it
class TestRootController:
    def test_http_get(self):
        client = TestClient(server.app)
        response = client.get("/")

        assert response.status_code == 200
        assert response.json() == {"message": "Hello World"}
