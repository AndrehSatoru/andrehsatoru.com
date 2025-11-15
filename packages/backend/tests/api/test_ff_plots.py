import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from src.backend_projeto.main import app

client = TestClient(app)


def _dummy_ff3_monthly():
    idx = pd.date_range(start="2024-01-31", periods=6, freq="M")
    df = pd.DataFrame({
        "MKT_RF": [0.01, 0.005, -0.002, 0.012, 0.004, 0.006],
        "SMB":    [0.002, -0.001, 0.000, 0.001, -0.002, 0.003],
        "HML":    [0.003, 0.002, -0.001, 0.001, 0.000, -0.002],
        "RF":     [0.009, 0.009, 0.009, 0.009, 0.009, 0.009],
    }, index=idx)
    return df


def _dummy_ff5_monthly():
    idx = pd.date_range(start="2024-01-31", periods=6, freq="M")
    df = pd.DataFrame({
        "MKT_RF": [0.01, 0.005, -0.002, 0.012, 0.004, 0.006],
        "SMB":    [0.002, -0.001, 0.000, 0.001, -0.002, 0.003],
        "HML":    [0.003, 0.002, -0.001, 0.001, 0.000, -0.002],
        "RMW":    [0.001, 0.000, 0.002, -0.001, 0.001, 0.000],
        "CMA":    [0.000, 0.001, -0.001, 0.002, 0.000, -0.001],
        "RF":     [0.009, 0.009, 0.009, 0.009, 0.009, 0.009],
    }, index=idx)
    return df


def _dummy_prices_single():
    idx = pd.date_range(start="2024-01-01", periods=126, freq="B")
    return pd.DataFrame({"AAA": 10 + np.linspace(0, 1.0, len(idx))}, index=idx)


def _dummy_rf_monthly_selic():
    idx = pd.date_range(start="2024-01-31", periods=6, freq="M")
    return pd.Series([0.009]*6, index=idx, name="RF")


@pytest.fixture
def monkeypatch_ff_plots(monkeypatch):
    def _patch():
        monkeypatch.setattr(
            "src.backend_projeto.core.data_handling.YFinanceProvider.fetch_ff3_us_monthly",
            lambda self, start_date, end_date: _dummy_ff3_monthly(),
            raising=True,
        )
        monkeypatch.setattr(
            "src.backend_projeto.core.data_handling.YFinanceProvider.fetch_ff5_us_monthly",
            lambda self, start_date, end_date: _dummy_ff5_monthly(),
            raising=True,
        )
        monkeypatch.setattr(
            "src.backend_projeto.core.data_handling.YFinanceProvider.fetch_stock_prices",
            lambda self, assets, start_date, end_date: _dummy_prices_single(),
            raising=True,
        )
        monkeypatch.setattr(
            "src.backend_projeto.core.data_handling.YFinanceProvider.compute_monthly_rf_from_cdi",
            lambda self, start_date, end_date: _dummy_rf_monthly_selic(),
            raising=True,
        )
    return _patch


def test_plot_ff_factors_ff3(monkeypatch_ff_plots):
    monkeypatch_ff_plots()
    r = client.post("/api/v1/plots/ff-factors", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert len(r.content) > 1000


def test_plot_ff_factors_ff5(monkeypatch_ff_plots):
    monkeypatch_ff_plots()
    payload = {"model": "ff5", "start_date": "2024-01-01", "end_date": "2024-06-30"}
    r = client.post("/plots/ff-factors", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"


def test_plot_ff_betas_ff3(monkeypatch_ff_plots):
    monkeypatch_ff_plots()
    payload = {
        "model": "ff3",
        "asset": "AAA",
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "rf_source": "selic"
    }
    r = client.post("/api/v1/plots/ff-betas", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert len(r.content) > 1000


def test_plot_ff_betas_ff5(monkeypatch_ff_plots):
    monkeypatch_ff_plots()
    payload = {
        "model": "ff5",
        "asset": "AAA",
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "rf_source": "selic"
    }
    r = client.post("/plots/ff-betas", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"