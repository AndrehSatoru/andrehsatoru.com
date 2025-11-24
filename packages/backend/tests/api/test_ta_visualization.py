import pytest
from fastapi.testclient import TestClient
import pandas as pd

from src.backend_projeto.main import app

client = TestClient(app)


def _dummy_prices():
    idx = pd.date_range(start="2024-01-01", periods=50, freq="B")
    df = pd.DataFrame({
        "PETR4.SA": 30 + (idx.to_series().rank(method="first").values * 0.05),
    }, index=idx)
    return df


@pytest.fixture
def monkeypatch_prices(monkeypatch):
    def _patch():
        def fake_prices(self, assets, start_date, end_date):
            df = _dummy_prices()
            cols = [a for a in assets if a in df.columns]
            return df[cols] if cols else df
        monkeypatch.setattr("backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices", fake_prices, raising=True)
    return _patch


def test_plot_ta_ma_returns_png(monkeypatch_prices):
    """Testa endpoint de plot com médias móveis."""
    monkeypatch_prices()
    payload = {
        "asset": "PETR4.SA",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "plot_type": "ma",
        "ma_windows": [5, 21],
        "ma_method": "sma"
    }
    r = client.post("/api/v1/plots/ta", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert len(r.content) > 1000  # PNG deve ter tamanho razoável


def test_plot_ta_macd_returns_png(monkeypatch_prices):
    """Testa endpoint de plot com MACD."""
    monkeypatch_prices()
    payload = {
        "asset": "PETR4.SA",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "plot_type": "macd",
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9
    }
    r = client.post("/api/v1/plots/ta", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert len(r.content) > 1000


def test_plot_ta_combined_returns_png(monkeypatch_prices):
    """Testa endpoint de plot combinado (MAs + MACD)."""
    monkeypatch_prices()
    payload = {
        "asset": "PETR4.SA",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "plot_type": "combined",
        "ma_windows": [5, 21],
        "ma_method": "ema",
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9
    }
    r = client.post("/api/v1/plots/ta", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert len(r.content) > 1000


def test_plot_ta_empty_asset_returns_422(monkeypatch_prices):
    """Testa validação de asset vazio."""
    monkeypatch_prices()
    payload = {
        "asset": "",
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "plot_type": "ma"
    }
    r = client.post("/api/v1/plots/ta", json=payload)
    assert r.status_code == 422


def test_config_endpoint_returns_dict():
    """Testa endpoint de configurações."""
    r = client.get("/api/v1/config")
    assert r.status_code == 200
    data = r.json()
    assert "DIAS_UTEIS_ANO" in data
    assert "MAX_ASSETS_PER_REQUEST" in data
    assert "CACHE_ENABLED" in data
    assert data["DIAS_UTEIS_ANO"] == 252