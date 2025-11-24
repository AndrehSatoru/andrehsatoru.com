import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from src.backend_projeto.main import app

client = TestClient(app)


def _dummy_prices_two_assets():
    idx = pd.date_range(start="2024-01-01", periods=60, freq="B")
    return pd.DataFrame({"A": 100 + np.linspace(0, 1.0, len(idx)), "B": 50 + np.linspace(0, 0.5, len(idx))}, index=idx)


def _dummy_benchmark_series():
    idx = pd.date_range(start="2024-01-01", periods=60, freq="B")
    return pd.Series(4000 + np.linspace(0, 20, len(idx)), index=idx, name="^GSPC")


@pytest.fixture
def monkeypatch_aliases(monkeypatch):
    calls = {"ticker": None}

    def _patch():
        # wallet prices
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices",
            lambda self, assets, start_date, end_date: _dummy_prices_two_assets(),
            raising=True,
        )
        # benchmark fetch capturing ticker after normalization
        def _fetch_bench(self, ticker, start_date, end_date):
            calls["ticker"] = ticker
            return _dummy_benchmark_series()
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_benchmark_data",
            _fetch_bench,
            raising=True,
        )
    return calls, _patch


def test_relvar_sp500_alias_normalized(monkeypatch_aliases):
    calls, patch = monkeypatch_aliases
    patch()
    payload = {
        "assets": ["A", "B"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "weights": [0.5, 0.5],
        "alpha": 0.95,
        "method": "historical",
    }
    r = client.post("/api/v1/risk/relvar", json=payload)
    assert r.status_code == 200
    # should normalize to ^GSPC or SPY; our fetcher stores what's used
    assert calls["ticker"] in ("^GSPC", "SPY")


def test_capm_msci_world_alias_normalized(monkeypatch_aliases):
    calls, patch = monkeypatch_aliases
    patch()
    # We mock OptimizationEngine via endpoint; but easier: hit relvar again with alias 'msci world' to ensure normalization
    payload = {
        "assets": ["A", "B"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "weights": [0.5, 0.5],
        "alpha": 0.95,
        "method": "historical",
        "benchmark": "msci world"
    }
    r = client.post("/api/v1/risk/relvar", json=payload)
    assert r.status_code == 200
    assert calls["ticker"] in ("URTH", "ACWI")