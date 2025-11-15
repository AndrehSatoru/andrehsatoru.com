import pytest
from fastapi.testclient import TestClient
import pandas as pd

from src.backend_projeto.main import app

client = TestClient(app)


def _dummy_prices():
    idx = pd.date_range(start="2024-01-01", periods=50, freq="B")
    df = pd.DataFrame({
        "AAA": 10 + (idx.to_series().rank(method="first").values * 0.05),
        "BBB": 20 + ((idx.to_series().rank(method="first") % 3).values * 0.07),
    }, index=idx)
    return df


def _dummy_benchmark():
    idx = pd.date_range(start="2024-01-01", periods=50, freq="B")
    s = pd.Series(1000 + (idx.to_series().rank(method="first").values * 0.6), index=idx, name="^DUMMY")
    return s


@pytest.fixture
def monkeypatch_data(monkeypatch):
    def _patch(bench_none=False, evt_value=1.23):
        def fake_prices(self, assets, start_date, end_date):
            df = _dummy_prices()
            cols = [a for a in assets if a in df.columns]
            return df[cols] if cols else df
        def fake_bench(self, ticker, start_date, end_date):
            if bench_none:
                return None
            return _dummy_benchmark()
        def fake_var_evt(series, alpha):
            # Simula retorno do var_evt (valor, detalhes)
            return (evt_value, {"mocked": True, "alpha": alpha})
        monkeypatch.setattr("src.backend_projeto.core.data_handling.YFinanceProvider.fetch_stock_prices", fake_prices, raising=True)
        monkeypatch.setattr("src.backend_projeto.core.data_handling.YFinanceProvider.fetch_benchmark_data", fake_bench, raising=True)
        monkeypatch.setattr("src.backend_projeto.core.analysis.var_evt", fake_var_evt, raising=True)
    return _patch


def test_ivar_evt_path(monkeypatch_data):
    monkeypatch_data(evt_value=2.5)
    payload = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "weights": [0.6, 0.4],
        "alpha": 0.99,
        "method": "evt",
        "delta": 0.01,
    }
    r = client.post("/api/v1/risk/ivar", json=payload)
    assert r.status_code == 200
    res = r.json()["result"]
    assert set(res.keys()) >= {"ivar", "base_var", "alpha", "method"}
    # ivar deve ter as chaves dos ativos
    assert set(res["ivar"].keys()) == {"AAA", "BBB"}


def test_mvar_evt_path(monkeypatch_data):
    monkeypatch_data(evt_value=3.14)
    payload = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "weights": [0.5, 0.5],
        "alpha": 0.95,
        "method": "evt",
    }
    r = client.post("/api/v1/risk/mvar", json=payload)
    assert r.status_code == 200
    res = r.json()["result"]
    assert set(res.keys()) >= {"mvar", "base_var", "alpha", "method"}
    assert set(res["mvar"].keys()) == {"AAA", "BBB"}


def test_relvar_evt_path(monkeypatch_data):
    monkeypatch_data(evt_value=4.56)
    payload = {
        "assets": ["AAA", "BBB"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-31",
        "weights": [0.5, 0.5],
        "alpha": 0.95,
        "method": "evt",
        "benchmark": "^DUMMY",
    }
    r = client.post("/api/v1/risk/relvar", json=payload)
    assert r.status_code == 200
    res = r.json()["result"]
    assert "relative_var" in res
    # Como var_evt foi mockado com 4.56, relative_var deve refletir esse valor
    assert abs(res["relative_var"] - 4.56) < 1e-9