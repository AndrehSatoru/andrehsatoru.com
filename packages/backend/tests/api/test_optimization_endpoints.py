import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from src.backend_projeto.main import app
    return TestClient(app)

def test_opt_markowitz(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "objective": "max_sharpe"
    }
    r = client.post("/api/v1/opt/markowitz", json=payload)
    assert r.status_code == 200
    js = r.json()["result"]
    assert "weights" in js and "sharpe" in js

def test_opt_blacklitterman(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "market_caps": {"AAA.SA": 1000000, "BBB.SA": 2000000},
        "views": [],
        "tau": 0.05
    }
    r = client.post("/api/v1/opt/blacklitterman", json=payload)
    assert r.status_code == 200
    js = r.json()["result"]
    assert "weights" in js and "sharpe" in js

def test_frontier_data(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "n_samples": 100,
        "long_only": True,
        "rf": 0.01
    }
    r = client.post("/api/v1/opt/markowitz/frontier-data", json=payload)
    assert r.status_code == 200
    js = r.json()
    assert "points" in js and len(js["points"]) == 100

def test_bl_frontier_data(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "n_samples": 100,
        "long_only": True,
        "rf": 0.01,
        "market_caps": {"AAA.SA": 1000000, "BBB.SA": 2000000},
        "views": [],
        "tau": 0.05
    }
    r = client.post("/api/v1/opt/blacklitterman/frontier-data", json=payload)
    assert r.status_code == 200
    js = r.json()
    assert "points" in js and len(js["points"]) == 100
