import pytest
from fastapi.testclient import TestClient
import pandas as pd

from src.backend_projeto.main import app

client = TestClient(app)


def _dummy_prices():
    idx = pd.date_range(start="2024-01-01", periods=60, freq="B")
    df = pd.DataFrame({
        "AAA": 10 + (idx.to_series().rank(method="first").values * 0.01),
        "BBB": 20 + ((idx.to_series().rank(method="first") % 5).values * 0.02),
        "CCC": 30 + ((idx.to_series().rank(method="first") % 7).values * 0.03),
    }, index=idx)
    return df


def _dummy_benchmark():
    idx = pd.date_range(start="2024-01-01", periods=60, freq="B")
    s = pd.Series(1000 + (idx.to_series().rank(method="first").values * 0.5), index=idx, name="^DUMMY")
    return s


@pytest.fixture
def monkeypatch_data(monkeypatch):
    def _patch():
        def fake_prices(self, assets, start_date, end_date):
            df = _dummy_prices()
            cols = [a for a in assets if a in df.columns]
            return df[cols] if cols else df
        def fake_bench(self, ticker, start_date, end_date):
            return _dummy_benchmark()
        monkeypatch.setattr("src.backend_projeto.core.data_handling.YFinanceProvider.fetch_stock_prices", fake_prices, raising=True)
        monkeypatch.setattr("src.backend_projeto.core.data_handling.YFinanceProvider.fetch_benchmark_data", fake_bench, raising=True)
    return _patch


def test_risk_ivar_basic(monkeypatch_data):
    monkeypatch_data()
    payload = {
        "assets": ["AAA", "BBB", "CCC"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "weights": [0.3, 0.4, 0.3],
        "alpha": 0.99,
        "method": "historical",
        "delta": 0.01,
    }
    r = client.post("/api/v1/risk/ivar", json=payload)
    assert r.status_code == 200
    data = r.json()["result"]
    assert "ivar" in data and isinstance(data["ivar"], dict)
    # Deve conter uma entrada por ativo
    for a in payload["assets"]:
        assert a in data["ivar"]


def test_risk_mvar_basic(monkeypatch_data):
    monkeypatch_data()
    payload = {
        "assets": ["AAA", "BBB", "CCC"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "weights": [0.3, 0.4, 0.3],
        "alpha": 0.99,
        "method": "std",
    }
    r = client.post("/api/v1/risk/mvar", json=payload)
    assert r.status_code == 200
    data = r.json()["result"]
    assert "mvar" in data and isinstance(data["mvar"], dict)
    for a in payload["assets"]:
        assert a in data["mvar"]


def test_risk_relvar_basic(monkeypatch_data):
    monkeypatch_data()
    payload = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "weights": [0.5, 0.5],
        "alpha": 0.95,
        "method": "ewma",
        "ewma_lambda": 0.94,
        "benchmark": "^DUMMY",
    }
    r = client.post("/api/v1/risk/relvar", json=payload)
    assert r.status_code == 200
    data = r.json()["result"]
    assert "relative_var" in data