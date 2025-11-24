import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from src.backend_projeto.main import app

client = TestClient(app)


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


@pytest.fixture
def monkeypatch_ff5_plot(monkeypatch):
    def _patch():
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_ff5_us_monthly",
            lambda self, start_date, end_date: _dummy_ff5_monthly(),
            raising=True,
        )
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices",
            lambda self, assets, start_date, end_date: _dummy_prices_single(),
            raising=True,
        )
    return _patch


def test_plot_ff_betas_ff5_with_rf_ff(monkeypatch_ff5_plot):
    monkeypatch_ff5_plot()
    payload = {
        "model": "ff5",
        "asset": "AAA",
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "rf_source": "ff"
    }
    r = client.post("/api/v1/plots/ff-betas", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert len(r.content) > 1000