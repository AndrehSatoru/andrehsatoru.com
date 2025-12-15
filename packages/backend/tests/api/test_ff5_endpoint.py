import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from backend_projeto.main import app

client = TestClient(app)


def _dummy_prices():
    # 24 meses de dados diários
    idx = pd.date_range(start="2022-01-01", periods=504, freq="B")
    df = pd.DataFrame({
        "AAA": 10 + np.linspace(0, 5.0, len(idx)),
        "BBB": 20 + np.linspace(0, -2.5, len(idx)),
    }, index=idx)
    return df


def _dummy_ff5_monthly():
    # 24 meses (finais de mês)
    idx = pd.date_range(start="2022-01-31", periods=24, freq="M")
    df = pd.DataFrame({
        "MKT_RF": np.random.normal(0.005, 0.02, len(idx)),
        "SMB":    np.random.normal(0.001, 0.01, len(idx)),
        "HML":    np.random.normal(0.002, 0.01, len(idx)),
        "RMW":    np.random.normal(0.001, 0.005, len(idx)),
        "CMA":    np.random.normal(0.001, 0.005, len(idx)),
        "RF":     np.full(len(idx), 0.009),
    }, index=idx)
    return df


def _dummy_rf_monthly_selic():
    idx = pd.date_range(start="2022-01-31", periods=24, freq="M")
    rf = pd.Series(np.full(len(idx), 0.009), index=idx, name="RF")
    return rf


@pytest.fixture
def monkeypatch_ff5(monkeypatch):
    def _patch():
        def fake_prices(self, assets, start_date, end_date):
            df = _dummy_prices()
            cols = [a for a in assets if a in df.columns]
            return df[cols] if cols else df
        def fake_ff5(self, start_date, end_date):
            return _dummy_ff5_monthly()
        def fake_rf(self, start_date, end_date):
            return _dummy_rf_monthly_selic()
        monkeypatch.setattr("backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices", fake_prices, raising=True)
        monkeypatch.setattr("backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_ff5_us_monthly", fake_ff5, raising=True)
        monkeypatch.setattr("backend_projeto.infrastructure.data_handling.YFinanceProvider.compute_monthly_rf_from_cdi", fake_rf, raising=True)
    return _patch


def test_ff5_endpoint_selic(monkeypatch_ff5):
    monkeypatch_ff5()
    payload = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "frequency": "M",
        "market": "US",
        "rf_source": "selic"
    }
    r = client.post("/api/v1/factors/ff5", json=payload)
    assert r.status_code == 200
    data = r.json()["result"]
    assert data["model"] == "FF5"
    assert data["frequency"] == "M"
    for a in ["AAA", "BBB"]:
        m = data["results"][a]
        for k in ["alpha", "beta_mkt", "beta_smb", "beta_hml", "beta_rmw", "beta_cma", "r2", "n_obs"]:
            assert k in m


def test_ff5_endpoint_us10y(monkeypatch_ff5, monkeypatch):
    monkeypatch_ff5()

    def fake_us10y(self, start_date, end_date):
        idx = pd.date_range(start="2022-01-31", periods=24, freq="M")
        return pd.Series(np.linspace(4.0, 4.5, 24), index=idx, name="US10Y")

    monkeypatch.setattr("backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_us10y_monthly_yield", fake_us10y, raising=True)

    payload = {
        "assets": ["AAA"],
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "rf_source": "us10y"
    }
    r = client.post("/api/v1/factors/ff5", json=payload)
    assert r.status_code == 200
    data = r.json()["result"]
    assert data["model"] == "FF5"
    assert "AAA" in data["results"]