import pytest
from fastapi.testclient import TestClient
import pandas as pd

from src.backend_projeto.main import app

client = TestClient(app)


def _dummy_prices():
    idx = pd.date_range(start="2024-01-01", periods=15, freq="B")
    df = pd.DataFrame({
        "AAA": [10 + i*0.2 for i in range(len(idx))],
    }, index=idx)
    return df


@pytest.fixture
def monkeypatch_prices(monkeypatch):
    def _patch():
        def fake_fetch(self, assets, start_date, end_date):
            df = _dummy_prices()
            cols = [a for a in assets if a in df.columns]
            return df[cols] if cols else df
        monkeypatch.setattr(
            "src.backend_projeto.core.data_handling.YFinanceProvider.fetch_stock_prices",
            fake_fetch,
            raising=True,
        )
    return _patch


def test_ta_moving_averages_ema_custom_windows(monkeypatch_prices):
    monkeypatch_prices()
    payload = {
        "assets": ["AAA"],
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "method": "ema",
        "windows": [3, 7],
    }
    r = client.post("/api/v1/ta/moving-averages", json=payload)
    assert r.status_code == 200
    data = r.json()
    cols = data["columns"]
    assert "AAA_EMA_3" in cols
    assert "AAA_EMA_7" in cols
    assert "AAA_SMA_3" not in cols


def test_ta_moving_averages_invalid_method_422(monkeypatch_prices):
    monkeypatch_prices()
    payload = {
        "assets": ["AAA"],
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "method": "wma",
        "windows": [5, 21],
    }
    r = client.post("/api/v1/ta/moving-averages", json=payload)
    assert r.status_code == 422