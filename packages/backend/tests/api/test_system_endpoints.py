import pytest
from fastapi.testclient import TestClient

from backend_projeto.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_status(client: TestClient):
    r = client.get("/api/v1/status")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
