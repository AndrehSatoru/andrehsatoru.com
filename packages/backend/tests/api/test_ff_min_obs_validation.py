import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from src.backend_projeto.main import app

client = TestClient(app)


def _daily_prices_for_months(months=5):
    # Create daily business days covering `months` months
    start = "2024-01-01"
    end = pd.to_datetime(start) + pd.DateOffset(months=months, days=5)
    idx = pd.date_range(start=start, end=end, freq="B")
    return pd.DataFrame({"AAA": 100 + np.linspace(0, 1.0, len(idx))}, index=idx)


def _ff3_monthly_n(n=5):
    idx = pd.date_range(start="2024-01-31", periods=n, freq="M")
    df = pd.DataFrame({
        "MKT_RF": np.linspace(0.002, 0.004, n),
        "SMB":    0.0,
        "HML":    0.0,
        "RF":     0.001,
    }, index=idx)
    return df


def _ff5_monthly_n(n=5):
    idx = pd.date_range(start="2024-01-31", periods=n, freq="M")
    df = pd.DataFrame({
        "MKT_RF": np.linspace(0.002, 0.004, n),
        "SMB":    0.0,
        "HML":    0.0,
        "RMW":    0.0,
        "CMA":    0.0,
        "RF":     0.001,
    }, index=idx)
    return df


@pytest.fixture
def monkeypatch_min_obs(monkeypatch):
    def _patch():
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices",
            lambda self, assets, start_date, end_date: _daily_prices_for_months(5),
            raising=True,
        )
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_ff3_us_monthly",
            lambda self, start_date, end_date: _ff3_monthly_n(5),
            raising=True,
        )
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_ff5_us_monthly",
            lambda self, start_date, end_date: _ff5_monthly_n(5),
            raising=True,
        )
        # RF sources won't be used with rf_source='ff'
    return _patch


def test_ff3_min_obs_422(monkeypatch_min_obs):
    monkeypatch_min_obs()
    payload = {
        "assets": ["AAA"],
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "rf_source": "ff"
    }
    r = client.post("/api/v1/factors/ff3", json=payload)
    assert r.status_code == 422
    assert "insuficiente" in r.json()["detail"].lower() or "menos de 6" in r.json()["detail"].lower()


def test_ff5_min_obs_422(monkeypatch_min_obs):
    monkeypatch_min_obs()
    payload = {
        "assets": ["AAA"],
        "start_date": "2024-01-01",
        "end_date": "2024-06-30",
        "rf_source": "ff"
    }
    r = client.post("/api/v1/factors/ff5", json=payload)
    assert r.status_code == 422
    assert "insuficiente" in r.json()["detail"].lower() or "menos de 6" in r.json()["detail"].lower()