import math
import pytest
from fastapi.testclient import TestClient
import pandas as pd

from src.backend_projeto.main import app

client = TestClient(app)


def _dummy_prices():
    idx = pd.date_range(start="2024-01-01", periods=80, freq="B")
    df = pd.DataFrame({
        "AAA": 10 + (idx.to_series().rank(method="first").values * 0.02),
        "BBB": 20 + ((idx.to_series().rank(method="first") % 4).values * 0.03),
    }, index=idx)
    return df


def _dummy_benchmark():
    idx = pd.date_range(start="2024-01-01", periods=80, freq="B")
    s = pd.Series(1000 + (idx.to_series().rank(method="first").values * 0.4), index=idx, name="^DUMMY")
    return s


@pytest.fixture
def monkeypatch_prices(monkeypatch):
    def _patch():
        def fake_prices(self, assets, start_date, end_date):
            df = _dummy_prices()
            cols = [a for a in assets if a in df.columns]
            return df[cols] if cols else df
        monkeypatch.setattr("src.backend_projeto.core.data_handling.YFinanceProvider.fetch_stock_prices", fake_prices, raising=True)
    return _patch


@pytest.fixture
def monkeypatch_benchmark(monkeypatch):
    def _patch(return_none=False):
        def fake_bench(self, ticker, start_date, end_date):
            if return_none:
                return None
            return _dummy_benchmark()
        monkeypatch.setattr("src.backend_projeto.core.data_handling.YFinanceProvider.fetch_benchmark_data", fake_bench, raising=True)
    return _patch


def test_ivar_std_and_ewma(monkeypatch_prices):
    monkeypatch_prices()
    payload_base = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-04-30",
        "weights": [0.6, 0.4],
        "alpha": 0.99,
        "delta": 0.02,
    }
    # std
    r1 = client.post("/api/v1/risk/ivar", json={**payload_base, "method": "std"})
    assert r1.status_code == 200
    ivar1 = r1.json()["result"]["ivar"]
    assert set(ivar1.keys()) == {"AAA", "BBB"}
    # ewma
    r2 = client.post("/api/v1/risk/ivar", json={**payload_base, "method": "ewma", "ewma_lambda": 0.94})
    assert r2.status_code == 200
    ivar2 = r2.json()["result"]["ivar"]
    assert set(ivar2.keys()) == {"AAA", "BBB"}


def test_mvar_single_asset_nan(monkeypatch_prices):
    monkeypatch_prices()
    payload = {
        "assets": ["AAA"],
        "start_date": "2024-01-01",
        "end_date": "2024-04-30",
        "weights": [1.0],
        "alpha": 0.99,
        "method": "historical",
    }
    r = client.post("/api/v1/risk/mvar", json=payload)
    assert r.status_code == 200
    res = r.json()["result"]
    assert "mvar" in res
    # valor deve ser NaN para o único ativo
    val = res["mvar"]["AAA"]
    # JSON converte NaN para null
    assert val is None


def test_relvar_methods_std_ewma(monkeypatch_prices, monkeypatch_benchmark):
    monkeypatch_prices()
    monkeypatch_benchmark()
    base = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-04-30",
        "weights": [0.5, 0.5],
        "alpha": 0.95,
    }
    # std
    r1 = client.post("/api/v1/risk/relvar", json={**base, "method": "std", "benchmark": "^DUMMY"})
    assert r1.status_code == 200
    rel1 = r1.json()["result"]["relative_var"]
    assert isinstance(rel1, float)
    # ewma
    r2 = client.post("/api/v1/risk/relvar", json={**base, "method": "ewma", "ewma_lambda": 0.9, "benchmark": "^DUMMY"})
    assert r2.status_code == 200
    rel2 = r2.json()["result"]["relative_var"]
    assert isinstance(rel2, float)


def test_relvar_missing_benchmark_returns_error(monkeypatch_prices, monkeypatch_benchmark):
    monkeypatch_prices()
    # benchmark retorna None
    monkeypatch_benchmark(return_none=True)
    payload = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-04-30",
        "weights": [0.5, 0.5],
        "alpha": 0.95,
        "method": "historical",
        "benchmark": "^NOTFOUND",
    }
    r = client.post("/api/v1/risk/relvar", json=payload)
    assert r.status_code == 200
    res = r.json()["result"]
    assert res.get("error") == "benchmark_data_unavailable"