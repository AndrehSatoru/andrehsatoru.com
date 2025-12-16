
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from backend_projeto.domain.portfolio_analyzer import PortfolioAnalyzer
from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.infrastructure.utils.config import Settings


@pytest.fixture
def sample_transactions():
    data = {
        'Data': ['2023-01-03', '2023-01-10'],
        'Ativo': ['PETR4.SA', 'VALE3.SA'],
        'Quantidade': [100, 50],
        'Preco': [25.0, 70.0],
        'Taxas': [0.0, 0.0]
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_data_loader():
    loader = MagicMock(spec=YFinanceProvider)
    return loader


@pytest.fixture
def mock_config():
    config = Settings()
    return config


def test_monte_carlo_simulation_distributions(sample_transactions, mock_data_loader, mock_config):
    """
    Test verifies that MGB and Bootstrap methods produce distinct distributions
    and that the simulation runs with the new default of 100,000 paths.
    """
    analyzer = PortfolioAnalyzer(
        transactions_df=sample_transactions,
        data_loader=mock_data_loader,
        config=mock_config,
        end_date='2023-06-30'
    )

    # Mock prices to generate a portfolio value series
    dates = pd.date_range(start='2023-01-03', end='2023-06-30', freq='B')
    # Generate random walk prices
    np.random.seed(42)
    returns1 = np.random.normal(0.001, 0.02, len(dates))
    returns2 = np.random.normal(0.0005, 0.015, len(dates))

    price1 = 25.0 * np.exp(np.cumsum(returns1))
    price2 = 70.0 * np.exp(np.cumsum(returns2))

    prices = pd.DataFrame({
        'PETR4.SA': price1,
        'VALE3.SA': price2
    }, index=dates)

    mock_data_loader.fetch_stock_prices.return_value = prices
    mock_data_loader.fetch_cdi_daily.return_value = pd.Series(0.0004, index=dates)  # Mock CDI
    mock_data_loader.fetch_dividends.return_value = pd.DataFrame()

    # Force calculation of portfolio value
    analyzer.positions = analyzer._calculate_positions()
    analyzer.portfolio_value = analyzer._calculate_portfolio_value()
    analyzer._portfolio_returns = analyzer.calculate_returns(method='log')

    # Run Monte Carlo
    # Using fewer paths for test speed, but enough to show divergence
    result = analyzer._generate_monte_carlo_simulation(n_paths=1000, n_days=20)

    assert 'mgb' in result
    assert 'bootstrap' in result
    assert 'distribution' in result

    # Verify stats
    mgb_stats = result['mgb']
    bootstrap_stats = result['bootstrap']

    # They should not be identical (unlikely to be exactly same with random seed)
    assert mgb_stats['median'] != bootstrap_stats['median']
    assert mgb_stats['mean'] != bootstrap_stats['mean']

    # Verify structure
    assert 'params' in result
    # Check if params reflect input
    assert result['params']['n_paths'] == 1000
    assert result['params']['n_days'] == 20

    # Check distribution data
    dist = result['distribution']
    assert len(dist) > 0
    assert 'mgb' in dist[0]
    assert 'bootstrap' in dist[0]


def test_monte_carlo_default_params(sample_transactions, mock_data_loader, mock_config):
    """Test that default parameters are 100k paths."""
    analyzer = PortfolioAnalyzer(
        transactions_df=sample_transactions,
        data_loader=mock_data_loader,
        config=mock_config
    )

    # Mock minimal data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='B')
    prices = pd.DataFrame({'PETR4.SA': np.ones(100) * 10, 'VALE3.SA': np.ones(100) * 10}, index=dates)
    mock_data_loader.fetch_stock_prices.return_value = prices
    mock_data_loader.fetch_cdi_daily.return_value = pd.Series(0.0, index=dates)
    mock_data_loader.fetch_dividends.return_value = pd.DataFrame()

    analyzer.positions = analyzer._calculate_positions()
    analyzer.portfolio_value = analyzer._calculate_portfolio_value()
    analyzer._portfolio_returns = analyzer.calculate_returns()

    # Run with defaults
    # To avoid long test run, we'll patch numpy to return small arrays
    # or just trust the previous test for logic and check defaults by inspection or
    # by running a very short n_days with default n_paths.

    result = analyzer._generate_monte_carlo_simulation(n_days=1)
    assert result['params']['n_paths'] == 100000

