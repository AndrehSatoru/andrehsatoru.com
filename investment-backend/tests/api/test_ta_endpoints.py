import pytest
from fastapi.testclient import TestClient
import pandas as pd
from datetime import datetime

# app FastAPI
from backend_projeto.main import app

client = TestClient(app)


def _dummy_prices():
    idx = pd.date_range(start="2024-01-01", periods=10, freq="B")
    # Série com pequena tendência para gerar MACD diferente de zero
    df = pd.DataFrame({
        "AAA": [10 + i*0.1 for i in range(len(idx))],
        "BBB": [20 + (i%3)*0.2 for i in range(len(idx))],
    }, index=idx)
    return df


@pytest.fixture
def monkeypatch_prices(monkeypatch):
    def _patch():
        def fake_fetch(self, assets, start_date, end_date):
            df = _dummy_prices()
            # filtra colunas pedidas se existirem
            cols = [a for a in assets if a in df.columns]
            return df[cols] if cols else df
        monkeypatch.setattr(
            "backend_projeto.core.data_handling.DataLoader.fetch_stock_prices",
            fake_fetch,
            raising=True,
        )
    return _patch


def test_ta_moving_averages_returns_json(monkeypatch_prices):
    monkeypatch_prices()
    payload = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "method": "sma",
        "windows": [5, 21],
    }
    r = client.post("/ta/moving-averages", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert set(["columns", "index", "data"]) <= set(data.keys())
    cols = data["columns"]
    # Deve conter originais e as MAs
    assert "AAA" in cols and "BBB" in cols
    assert "AAA_SMA_5" in cols and "BBB_SMA_21" in cols
    assert len(data["index"]) >= 1
    assert len(data["data"]) == len(data["index"])  # linhas batem


def test_ta_macd_returns_json(monkeypatch_prices):
    monkeypatch_prices()
    payload = {
        "assets": ["AAA"],
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "fast": 12,
        "slow": 26,
        "signal": 9,
    }
    r = client.post("/ta/macd", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert set(["columns", "index", "data"]) <= set(data.keys())
    cols = data["columns"]
    assert "AAA" in cols
    assert "AAA_MACD" in cols
    assert "AAA_MACD_SIGNAL" in cols
    assert "AAA_MACD_HIST" in cols
    # Verificação básica de dimensão
    assert len(data["data"]) == len(data["index"])
