import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from backend_projeto.main import app
    return TestClient(app)

def test_factors_ff3(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "rf_source": "ff"
    }
    r = client.post("/api/v1/factors/ff3", json=payload)
    assert r.status_code == 200
    js = r.json()["result"]
    assert "results" in js and isinstance(js["results"], dict)

def test_factors_ff5(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "rf_source": "ff"
    }
    r = client.post("/api/v1/factors/ff5", json=payload)
    assert r.status_code == 200
    js = r.json()["result"]
    assert "results" in js and isinstance(js["results"], dict)

def test_factors_capm(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "benchmark": "^BVSP"
    }
    r = client.post("/api/v1/factors/capm", json=payload)
    assert r.status_code == 200
    js = r.json()["result"]
    assert "metrics" in js
    metrics = js["metrics"]
    assert "AAA.SA" in metrics and "beta" in metrics["AAA.SA"]

def test_factors_apt(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "factors": ["MKT_RF", "SMB", "HML"]
    }
    r = client.post("/api/v1/factors/apt", json=payload)
    assert r.status_code == 200
    js = r.json()["result"]
    assert "metrics" in js
    metrics = js["metrics"]
    assert "AAA.SA" in metrics and "betas" in metrics["AAA.SA"]
