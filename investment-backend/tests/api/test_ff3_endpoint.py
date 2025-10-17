import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from backend_projeto.main import app

client = TestClient(app)


def _dummy_prices():
    # 6 meses de dados diários
    idx = pd.date_range(start="2024-01-01", periods=126, freq="B")
    df = pd.DataFrame({
        "AAA": 10 + np.linspace(0, 1.0, len(idx)),
        "BBB": 20 + np.linspace(0, -0.5, len(idx)),
    }, index=idx)
    return df


def _dummy_ff3_monthly():
    # 6 meses (finais de mês)
    idx = pd.date_range(start="2024-01-31", periods=6, freq="M")
    df = pd.DataFrame({
        "MKT_RF": [0.01, 0.005, -0.002, 0.012, 0.004, 0.006],
        "SMB":    [0.002, -0.001, 0.000, 0.001, -0.002, 0.003],
        "HML":    [0.003, 0.002, -0.001, 0.001, 0.000, -0.002],
        "RF":     [0.009, 0.009, 0.009, 0.009, 0.009, 0.009],
    }, index=idx)
    return df


def _dummy_rf_monthly_selic():
    idx = pd.date_range(start="2024-01-31", periods=6, freq="M")
    rf = pd.Series([0.009, 0.009, 0.009, 0.009, 0.009, 0.009], index=idx, name="RF")
    return rf


@pytest.fixture
def monkeypatch_ff3(monkeypatch):
    def _patch():
        def fake_prices(self, assets, start_date, end_date):
            df = _dummy_prices()
            cols = [a for a in assets if a in df.columns]
            return df[cols] if cols else df
        def fake_ff3(self, start_date, end_date):
            return _dummy_ff3_monthly()
        def fake_rf(self, start_date, end_date):
            return _dummy_rf_monthly_selic()
        monkeypatch.setattr("backend_projeto.core.data_handling.DataLoader.fetch_stock_prices", fake_prices, raising=True)
        monkeypatch.setattr("backend_projeto.core.data_handling.DataLoader.fetch_ff3_us_monthly", fake_ff3, raising=True)
        monkeypatch.setattr("backend_projeto.core.data_handling.DataLoader.compute_monthly_rf_from_cdi", fake_rf, raising=True)
    return _patch


def test_ff3_endpoint_selic(monkeypatch_ff3):
    monkeypatch_ff3()
    payload = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "frequency": "M",
        "market": "US",
        "rf_source": "selic"
    }
    r = client.post("/factors/ff3", json=payload)
    assert r.status_code == 200
    data = r.json()["result"]
    assert data["model"] == "FF3"
    assert data["frequency"] == "M"
    # Deve conter resultados por ativo
    assert "AAA" in data["results"]
    assert "BBB" in data["results"]
    # Verificar chaves principais
    for a in ["AAA", "BBB"]:
        m = data["results"][a]
        for k in ["alpha", "beta_mkt", "beta_smb", "beta_hml", "r2", "n_obs"]:
            assert k in m


def test_ff3_endpoint_us10y(monkeypatch_ff3, monkeypatch):
    monkeypatch_ff3()

    def fake_us10y(self, start_date, end_date):
        idx = pd.date_range(start="2024-01-31", periods=6, freq="M")
        return pd.Series([4.0, 4.1, 4.2, 4.0, 3.9, 4.05], index=idx, name="US10Y")

    monkeypatch.setattr("backend_projeto.core.data_handling.DataLoader.fetch_us10y_monthly_yield", fake_us10y, raising=True)

    payload = {
        "assets": ["AAA"],
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "rf_source": "us10y"
    }
    r = client.post("/factors/ff3", json=payload)
    assert r.status_code == 200
    data = r.json()["result"]
    assert data["model"] == "FF3"
    assert "AAA" in data["results"]
