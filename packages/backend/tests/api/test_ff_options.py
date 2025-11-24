import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from src.backend_projeto.main import app

client = TestClient(app)


def _dummy_ff3_monthly():
    # 24 meses (finais de mês)
    idx = pd.date_range(start="2022-01-31", periods=24, freq="M")
    df = pd.DataFrame({
        "MKT_RF": np.random.normal(0.005, 0.02, len(idx)),
        "SMB":    np.random.normal(0.001, 0.01, len(idx)),
        "HML":    np.random.normal(0.002, 0.01, len(idx)),
        "RF":     np.full(len(idx), 0.009),
    }, index=idx)
    return df


def _dummy_prices_brl():
    # 24 meses de dados diários
    idx = pd.date_range(start="2022-01-01", periods=504, freq="B")
    # crescente suave para evitar retornos nulos
    return pd.DataFrame({"AAA.SA": 50 + np.linspace(0, 5.0, len(idx))}, index=idx)


def _dummy_fx_usdbrl(start, end):
    idx = pd.date_range(start=start, end=end, freq="B")
    return pd.DataFrame({"USD": pd.Series(5.0, index=idx)})


@pytest.fixture
def monkeypatch_ff_options(monkeypatch):
    def _patch():
        # FF3 monthly
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_ff3_us_monthly",
            lambda self, start_date, end_date: _dummy_ff3_monthly(),
            raising=True,
        )
        # FF5 monthly (reutiliza FF3 estrutura com colunas extras)
        def _dummy_ff5_monthly():
            df = _dummy_ff3_monthly()
            df = df.assign(RMW=0.0, CMA=0.0)
            return df
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_ff5_us_monthly",
            lambda self, start_date, end_date: _dummy_ff5_monthly(),
            raising=True,
        )
        # Prices daily (BRL asset)
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices",
            lambda self, assets, start_date, end_date: _dummy_prices_brl(),
            raising=True,
        )
        # FX USDBRL
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_exchange_rates",
            lambda self, currencies, start_date, end_date: _dummy_fx_usdbrl(start_date, end_date),
            raising=True,
        )
        # Asset currency info -> BRL for .SA
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_asset_info",
            lambda self, assets: {a: ("BRL" if a.upper().endswith(".SA") else "USD") for a in assets},
            raising=True,
        )
    return _patch


def test_plot_ff_betas_rf_ff_convert_to_usd(monkeypatch_ff_options):
    monkeypatch_ff_options()
    payload = {
        "model": "ff3",
        "asset": "AAA.SA",
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "rf_source": "ff",
        "convert_to_usd": True,
    }
    r = client.post("/api/v1/plots/ff-betas", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert len(r.content) > 1000


def test_ff3_endpoint_rf_ff_convert_to_usd(monkeypatch_ff_options):
    monkeypatch_ff_options()
    payload = {
        "assets": ["AAA.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "frequency": "M",
        "market": "US",
        "rf_source": "ff",
        "convert_to_usd": True,
    }
    r = client.post("/api/v1/factors/ff3", json=payload)
    assert r.status_code == 200
    data = r.json()["result"]
    assert data["model"] == "FF3"
    assert data["rf_source"] == "ff"
    assert "AAA.SA" in data["results"]


def test_ff5_endpoint_rf_ff_convert_to_usd(monkeypatch_ff_options):
    monkeypatch_ff_options()
    payload = {
        "assets": ["AAA.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "rf_source": "ff",
        "convert_to_usd": True,
    }
    r = client.post("/api/v1/factors/ff5", json=payload)
    assert r.status_code == 200
    data = r.json()["result"]
    assert data["model"] == "FF5"
    assert data["rf_source"] == "ff"
    assert "AAA.SA" in data["results"]