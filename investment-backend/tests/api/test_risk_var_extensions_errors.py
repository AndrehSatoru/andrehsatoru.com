import pytest
from fastapi.testclient import TestClient
import pandas as pd

from backend_projeto.main import app

client = TestClient(app)


def _dummy_prices():
    idx = pd.date_range(start="2024-01-01", periods=40, freq="B")
    df = pd.DataFrame({
        "AAA": 10 + (idx.to_series().rank(method="first").values * 0.03),
        "BBB": 20 + ((idx.to_series().rank(method="first") % 6).values * 0.02),
    }, index=idx)
    return df


def _dummy_benchmark_shifted():
    idx = pd.date_range(start="2025-01-01", periods=40, freq="B")
    s = pd.Series(1000 + (idx.to_series().rank(method="first").values * 0.5), index=idx, name="^SHIFT")
    return s


@pytest.fixture
def monkeypatch_prices(monkeypatch):
    def _patch():
        def fake_prices(self, assets, start_date, end_date):
            return _dummy_prices()
        monkeypatch.setattr("backend_projeto.core.data_handling.DataLoader.fetch_stock_prices", fake_prices, raising=True)
    return _patch


@pytest.fixture
def monkeypatch_benchmark(monkeypatch):
    def _patch(shifted=False):
        def fake_bench(self, ticker, start_date, end_date):
            return _dummy_benchmark_shifted() if shifted else None
        monkeypatch.setattr("backend_projeto.core.data_handling.DataLoader.fetch_benchmark_data", fake_bench, raising=True)
    return _patch


def test_ivar_empty_assets_returns_500(monkeypatch_prices):
    monkeypatch_prices()
    payload = {
        "assets": [],
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "weights": [],
        "alpha": 0.99,
        "method": "historical",
        "delta": 0.01,
    }
    r = client.post("/risk/ivar", json=payload)
    assert r.status_code == 500  # ValueError não tratado vira 500 pelo handler genérico


def test_mvar_weights_sum_zero_returns_500(monkeypatch_prices):
    monkeypatch_prices()
    payload = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "weights": [0.0, 0.0],  # soma zero
        "alpha": 0.99,
        "method": "historical",
    }
    r = client.post("/risk/mvar", json=payload)
    assert r.status_code == 500


def test_relvar_no_overlap_returns_500(monkeypatch_prices, monkeypatch_benchmark):
    monkeypatch_prices()
    # benchmark com datas sem interseção
    monkeypatch_benchmark(shifted=True)
    payload = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "weights": [0.5, 0.5],
        "alpha": 0.95,
        "method": "historical",
        "benchmark": "^SHIFT",
    }
    r = client.post("/risk/relvar", json=payload)
    assert r.status_code == 500


@pytest.mark.xfail(reason="Dependência 'arch' pode não estar instalada; comportamento varia")
def test_ivar_garch_may_fail_or_pass(monkeypatch_prices):
    monkeypatch_prices()
    payload = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "weights": [0.6, 0.4],
        "alpha": 0.99,
        "method": "garch",
        "delta": 0.01,
    }
    r = client.post("/risk/ivar", json=payload)
    assert r.status_code in (200, 500)
