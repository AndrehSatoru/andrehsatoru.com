import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from src.backend_projeto.main import app
    return TestClient(app)

def test_portfolio_weights_series(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "weights": [0.5, 0.5]
    }
    r = client.post("/api/v1/portfolio/weights-series", json=payload)
    assert r.status_code == 200
    js = r.json()
    assert "index" in js and "weights" in js
    assert len(js["index"]) > 0
    assert "AAA.SA" in js["weights"]
