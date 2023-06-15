from fastapi.testclient import TestClient
from myapp import server


def test_root():
    client = TestClient(server.app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
