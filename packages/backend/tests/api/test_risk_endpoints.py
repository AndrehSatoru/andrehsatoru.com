import pytest
from fastapi.testclient import TestClient

from src.backend_projeto.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_risk_var_historical(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "alpha": 0.99,
        "method": "historical"
    }
    r = client.post("/api/v1/risk/var", json=payload)
    assert r.status_code == 200
    js = r.json()
    assert "result" in js and "var" in js["result"]


def test_risk_es_std(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "alpha": 0.99,
        "method": "std"
    }
    r = client.post("/api/v1/risk/es", json=payload)
    assert r.status_code == 200
    assert "es" in r.json()["result"]


def test_risk_drawdown(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01"
    }
    r = client.post("/api/v1/risk/drawdown", json=payload)
    assert r.status_code == 200
    js = r.json()["result"]
    assert "max_drawdown" in js


def test_validate_backtest_request_model():
    from backend_projeto.domain.models.models import BacktestRequest
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2023-01-01",
        "end_date": "2024-03-01",
        "alpha": 0.99,
        "method": "ewma",
        "ewma_lambda": 0.94
    }
    try:
        BacktestRequest(**payload)
    except Exception as e:
        pytest.fail(f"BacktestRequest validation failed: {e}")

def test_risk_backtest_ewma(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2023-01-01",
        "end_date": "2024-03-01",
        "alpha": 0.99,
        "method": "ewma",
        "ewma_lambda": 0.94
    }
    r = client.post("/api/v1/risk/backtest", json=payload)
    if r.status_code != 200:
        print(f"API Response (Status: {r.status_code}): {r.json()}")
    assert r.status_code == 200
    js = r.json()["result"]
    assert {"n", "exceptions", "basel_zone"}.issubset(js.keys())


def test_covariance_ledoit_wolf(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01"
    }
    r = client.post("/api/v1/risk/covariance", json=payload)
    assert r.status_code == 200
    js = r.json()["result"]
    assert set(js.keys()) >= {"cov", "shrinkage", "columns"}


def test_risk_attribution(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "weights": [0.6, 0.4],
        "method": "std",
        "ewma_lambda": 0.94
    }
    r = client.post("/api/v1/risk/attribution", json=payload)
    assert r.status_code == 200
    js = r.json()["result"]
    assert set(js.keys()) >= {"assets", "weights", "portfolio_vol", "contribution_vol"}


def test_risk_compare(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "methods": ["historical", "std", "ewma"],
        "alpha": 0.99
    }
    r = client.post("/api/v1/risk/compare", json=payload)
    assert r.status_code == 200
    js = r.json()["result"]
    assert "comparison" in js and isinstance(js["comparison"], dict)
