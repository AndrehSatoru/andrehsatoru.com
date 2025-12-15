import pandas as pd
import numpy as np
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from backend_projeto.main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def _dummy_prices_two_assets():
    idx = pd.date_range(start="2023-01-01", periods=500, freq="B")
    np.random.seed(42) # for reproducibility
    prices_a = 100 + np.cumsum(np.random.normal(0, 1, len(idx)))
    prices_b = 50 + np.cumsum(np.random.normal(0, 0.5, len(idx)))
    return pd.DataFrame({"AAA.SA": prices_a, "BBB.SA": prices_b}, index=idx)

def _dummy_benchmark_series():
    """Generate dummy benchmark series for testing."""
    idx = pd.date_range(start="2023-01-01", periods=500, freq="B")
    np.random.seed(42)
    benchmark = 1000 + np.cumsum(np.random.normal(0.0005, 0.01, len(idx)))
    return pd.Series(benchmark, index=idx, name="Benchmark")

def _dummy_ff3_monthly():
    """Generate dummy Fama-French 3-factor data for testing."""
    idx = pd.date_range(start="2020-01-31", periods=48, freq="M")
    np.random.seed(42)
    return pd.DataFrame({
        "MKT_RF": np.random.normal(0.005, 0.02, len(idx)),
        "SMB": np.random.normal(0.001, 0.01, len(idx)),
        "HML": np.random.normal(0.002, 0.01, len(idx)),
        "RF": np.full(len(idx), 0.009),
    }, index=idx)

def _dummy_ff5_monthly():
    """Generate dummy Fama-French 5-factor data for testing."""
    df = _dummy_ff3_monthly()
    np.random.seed(43)
    df["RMW"] = np.random.normal(0.001, 0.01, len(df))
    df["CMA"] = np.random.normal(0.001, 0.01, len(df))
    return df

def _dummy_cdi_series():
    """Generate dummy CDI series for testing."""
    idx = pd.date_range(start="2020-01-31", periods=48, freq="M")
    return pd.Series(np.full(len(idx), 0.01), index=idx, name="CDI")

def _dummy_us10y_series():
    """Generate dummy US 10Y yield series for testing."""
    idx = pd.date_range(start="2020-01-31", periods=48, freq="M")
    return pd.Series(np.full(len(idx), 4.0), index=idx, name="US10Y")

from backend_projeto.infrastructure.utils.config import settings

@pytest.fixture(autouse=True)
def stub_fetch_prices(monkeypatch):
    # Mock the YFinanceProvider constructor
    def mock_yfinance_provider_init(self):
        self.config = settings
        self.fallback_providers = None
        self.cache = MagicMock() # Mock cache manager
        self.max_retries = 3
        self.backoff_factor = 1
        self.timeout = 10
        self.consecutive_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_open = False
        self.calendar = MagicMock() # Mock trading calendar

    monkeypatch.setattr(
        "backend_projeto.infrastructure.data_handling.YFinanceProvider.__init__",
        mock_yfinance_provider_init,
    )
    monkeypatch.setattr(
        "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices",
        lambda self, assets, start_date, end_date: _dummy_prices_two_assets(),
        raising=True,
    )
    monkeypatch.setattr(
        "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_asset_info",
        lambda self, assets: {asset: "USD" for asset in assets},
        raising=True,
    )
    monkeypatch.setattr(
        "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_benchmark_data",
        lambda self, ticker, start_date, end_date: _dummy_benchmark_series(),
        raising=True,
    )
    monkeypatch.setattr(
        "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_dividends",
        lambda self, assets, start_date, end_date: pd.DataFrame(),
        raising=True,
    )
    monkeypatch.setattr(
        "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_exchange_rates",
        lambda self, currencies, start_date, end_date: pd.DataFrame(),
        raising=True,
    )
    monkeypatch.setattr(
        "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_market_caps",
        lambda self, assets: {asset: 1e9 for asset in assets},
        raising=True,
    )
    # Fama-French mock data
    monkeypatch.setattr(
        "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_ff3_us_monthly",
        lambda self, start_date, end_date: _dummy_ff3_monthly(),
        raising=True,
    )
    monkeypatch.setattr(
        "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_ff5_us_monthly",
        lambda self, start_date, end_date: _dummy_ff5_monthly(),
        raising=True,
    )
    monkeypatch.setattr(
        "backend_projeto.infrastructure.data_handling.YFinanceProvider.compute_monthly_rf_from_cdi",
        lambda self, start_date, end_date: _dummy_cdi_series(),
        raising=True,
    )
    monkeypatch.setattr(
        "backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_us10y_monthly_yield",
        lambda self, start_date, end_date: _dummy_us10y_series(),
        raising=True,
    )
    yield


from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """Mocks the redis.Redis client to prevent network connections during tests."""
    mock_redis_client = MagicMock()
    mock_redis_client.ping.return_value = True
    mock_redis_client.get.return_value = None
    mock_redis_client.setex.return_value = True
    
    monkeypatch.setattr("redis.Redis", lambda *args, **kwargs: mock_redis_client)
