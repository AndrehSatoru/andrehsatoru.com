import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from backend_projeto.main import app

client = TestClient(app)

@pytest.fixture
def monkeypatch_rolling_beta(monkeypatch):
    def _patch():
        def fake_prices(self, assets, start_date, end_date):
            idx = pd.date_range(start=start_date, end=end_date, freq="B")
            data = {
                "PETR4.SA": 100 + np.cumsum(np.random.normal(0, 1, len(idx))),
                "^BVSP": 120000 + np.cumsum(np.random.normal(0, 100, len(idx))),
            }
            return pd.DataFrame(data, index=idx)
        
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices",
            fake_prices,
            raising=True,
        )
    return _patch

def test_plot_rolling_beta(monkeypatch_rolling_beta):
    monkeypatch_rolling_beta()
    payload = {
        "asset": "PETR4.SA",
        "benchmark": "^BVSP",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "window": 60
    }
    r = client.post("/api/v1/plots/advanced/rolling-beta", json=payload)
    assert r.status_code == 200
    assert r.headers['content-type'] == 'image/png'
    assert len(r.content) > 1000

def test_plot_underwater(monkeypatch_rolling_beta):
    monkeypatch_rolling_beta()
    payload = {
        "assets": ["PETR4.SA"],
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
    }
    r = client.post("/api/v1/plots/advanced/underwater", json=payload)
    assert r.status_code == 200
    assert r.headers['content-type'] == 'image/png'
    assert len(r.content) > 1000

@pytest.fixture
def monkeypatch_sector_analysis(monkeypatch):
    def _patch():
        def fake_prices(self, assets, start_date, end_date):
            idx = pd.date_range(start=start_date, end=end_date, freq="B")
            data = {
                "PETR4.SA": 100 + np.cumsum(np.random.normal(0, 1, len(idx))),
                "VALE3.SA": 50 + np.cumsum(np.random.normal(0, 0.5, len(idx))),
                "ITUB4.SA": 20 + np.cumsum(np.random.normal(0, 0.2, len(idx))),
            }
            return pd.DataFrame(data, index=idx)
        
        def fake_asset_info(self, assets):
            info = {
                "PETR4.SA": {"currency": "BRL", "sector": "Oil & Gas"},
                "VALE3.SA": {"currency": "BRL", "sector": "Mining"},
                "ITUB4.SA": {"currency": "BRL", "sector": "Financials"},
            }
            return {asset: info[asset] for asset in assets}

        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices",
            fake_prices,
            raising=True,
        )
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_asset_info",
            fake_asset_info,
            raising=True,
        )
    return _patch

@pytest.mark.skip(reason="Test causing infinite loading - needs investigation")
def test_generate_sector_analysis_dashboard(monkeypatch_sector_analysis):
    monkeypatch_sector_analysis()
    payload = {
        "assets": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
    }
    r = client.post("/api/v1/plots/dashboard/sector-analysis", json=payload)
    if r.status_code != 200:
        print(r.json())
    assert r.status_code == 200
    assert r.headers['content-type'] == 'image/png'
    assert len(r.content) > 1000

@pytest.fixture
def monkeypatch_monte_carlo_dashboard(monkeypatch):
    def fake_get_config():
        class MockConfig:
            DIAS_UTEIS_ANO = 252
            VAR_CONFIDENCE_LEVEL = 0.99
        return MockConfig()

    def _patch():
        def fake_prices(self, assets, start_date, end_date):
            idx = pd.date_range(start=start_date, end=end_date, freq="B")
            data = {
                "PETR4.SA": 100 + np.cumsum(np.random.normal(0, 1, len(idx))),
            }
            return pd.DataFrame(data, index=idx)
        
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices",
            fake_prices,
            raising=True,
        )
        monkeypatch.setattr(
            "backend_projeto.domain.simulation.MonteCarloEngine.simulate_gbm",
            lambda self, assets, start_date, end_date, weights, n_paths, n_days, vol_method, ewma_lambda, seed: {
                "params": {"mu": 0.001, "sigma": 0.02, "vol_method": vol_method},
                "var": 0.05,
                "es": 0.06,
                "confidence": 0.99,
                "n_paths": n_paths,
                "n_days": n_days,
                "prices_paths": np.random.rand(n_days, n_paths).tolist(),
                "terminal_distribution": np.random.normal(0, 0.1, n_paths).tolist(),
            },
            raising=True,
        )
        monkeypatch.setattr(
            "backend_projeto.api.deps.get_config",
            fake_get_config,
            raising=True,
        )
    return _patch

def test_generate_monte_carlo_dashboard(monkeypatch_monte_carlo_dashboard):
    monkeypatch_monte_carlo_dashboard()
    payload = {
        "assets": ["PETR4.SA"],
        "start_date": "2023-01-01",
        "end_date": "2023-01-31",
        "n_paths": 100,
        "n_days": 20,
        "vol_method": "std",
    }
    r = client.post("/api/v1/plots/dashboard/monte-carlo", json=payload)
    assert r.status_code == 200
    assert r.headers['content-type'] == 'image/png'
    assert len(r.content) > 1000

@pytest.fixture
def monkeypatch_efficient_frontier(monkeypatch):
    class MockConfig:
        DIAS_UTEIS_ANO = 252

    def _patch():
        def fake_prices(self, assets, start_date, end_date):
            idx = pd.date_range(start=start_date, end=end_date, freq="B")
            data = {
                "PETR4.SA": 100 + np.cumsum(np.random.normal(0, 1, len(idx))),
                "VALE3.SA": 50 + np.cumsum(np.random.normal(0, 0.5, len(idx))),
            }
            return pd.DataFrame(data, index=idx)
        
        monkeypatch.setattr(
            "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices",
            fake_prices,
            raising=True,
        )
        monkeypatch.setattr(
            "backend_projeto.api.deps.get_config", # Mock the get_config dependency
            lambda: MockConfig(), # get_config is a function that returns a Config object
            raising=True,
        )
    return _patch

def test_plot_efficient_frontier_with_cml(monkeypatch_efficient_frontier):
    monkeypatch_efficient_frontier()
    payload = {
        "assets": ["PETR4.SA", "VALE3.SA"],
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "n_samples": 100,
        "rf": 0.01
    }
    r = client.post("/api/v1/plots/efficient-frontier", json=payload)
    assert r.status_code == 200
    assert r.headers['content-type'] == 'image/png'
    assert len(r.content) > 1000

