"""
Testes unitários para os motores principais do sistema.
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from backend_projeto.domain.optimization import OptimizationEngine
from backend_projeto.domain.simulation import MonteCarloEngine
from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.infrastructure.utils.config import Settings

# Fixtures
@pytest.fixture
def mock_config():
    config = Settings()
    config.DIAS_UTEIS_ANO = 252
    return config

@pytest.fixture
def mock_loader():
    loader = MagicMock(spec=YFinanceProvider)
    return loader

@pytest.fixture
def optimization_engine(mock_loader, mock_config):
    return OptimizationEngine(loader=mock_loader, config=mock_config)

@pytest.fixture
def monte_carlo_engine(mock_loader, mock_config):
    return MonteCarloEngine(loader=mock_loader, config=mock_config)

# Testes para OptimizationEngine
class TestOptimizationEngine:
    def test_load_prices(self, optimization_engine, mock_loader):
        # Configuração
        assets = ['PETR4.SA', 'VALE3.SA']
        start_date = '2023-01-01'
        end_date = '2023-12-31'
        mock_prices = pd.DataFrame({
            'PETR4.SA': [10.0, 10.5, 10.8],
            'VALE3.SA': [70.0, 72.0, 71.5]
        }, index=pd.date_range(start=start_date, periods=3))
        mock_loader.fetch_stock_prices.return_value = mock_prices

        # Execução
        result = optimization_engine.load_prices(assets, start_date, end_date)

        # Verificação
        assert not result.empty
        assert all(asset in result.columns for asset in assets)
        mock_loader.fetch_stock_prices.assert_called_once_with(assets, start_date, end_date)

    def test_optimize_markowitz_invalid_assets(self, optimization_engine):
        # Teste com menos de 2 ativos
        # Mock load_prices to return a single asset DataFrame
        optimization_engine.load_prices = MagicMock(return_value=pd.DataFrame({'PETR4.SA': [10.0, 11.0, 10.5]}))
        with pytest.raises(ValueError, match="pelo menos 2 ativos"):
            optimization_engine.optimize_markowitz(
                assets=['PETR4.SA'],
                start_date='2023-01-01',
                end_date='2023-12-31'
            )

    @patch('backend_projeto.domain.financial_math._annualize_mean_cov')
    @patch('backend_projeto.domain.financial_math._returns_from_prices')
    def test_optimize_markowitz_max_sharpe(self, mock_returns, mock_annualize, optimization_engine, mock_loader):
        # Configuração
        assets = ['PETR4.SA', 'VALE3.SA']
        mock_prices = pd.DataFrame({
            'PETR4.SA': [10.0, 10.5, 10.8],
            'VALE3.SA': [70.0, 72.0, 71.5]
        })
        mock_loader.fetch_stock_prices.return_value = mock_prices
        
        # Configurar mocks para retornos e médias anuais
        mock_returns.return_value = pd.DataFrame({
            'PETR4.SA': [0.05, 0.03],
            'VALE3.SA': [0.03, 0.04]
        })
        mock_annualize.return_value = (
            np.array([0.1, 0.08]),  # mu
            np.array([[0.04, 0.02], [0.02, 0.03]])  # cov
        )

        # Execução
        result = optimization_engine.optimize_markowitz(
            assets=assets,
            start_date='2023-01-01',
            end_date='2023-12-31',
            objective='max_sharpe'
        )

        # Verificação
        assert 'weights' in result
        assert 'ret_annual' in result
        assert all(0 <= w <= 1 for w in result['weights'].values())
        assert abs(sum(result['weights'].values()) - 1.0) < 1e-6

# Testes para MonteCarloEngine
class TestMonteCarloEngine:
    def test_portfolio_returns(self, monte_carlo_engine):
        # Configuração
        prices = pd.DataFrame({
            'PETR4.SA': [10.0, 10.5, 10.8],
            'VALE3.SA': [70.0, 72.0, 71.5]
        }, index=pd.date_range('2023-01-01', periods=3))
        assets = ['PETR4.SA', 'VALE3.SA']
        weights = [0.5, 0.5]

        # Execução
        returns = monte_carlo_engine._portfolio_returns(prices, assets, weights)

        # Verificação
        assert isinstance(returns, pd.Series)
        assert not returns.empty
        assert len(returns) == 2  # Um retorno a menos que o número de preços

    @pytest.mark.parametrize("vol_method,expected_sigma", [
        ('std', 0.02),
        ('ewma', 0.02),
    ])
    def test_estimate_params(self, monte_carlo_engine, vol_method, expected_sigma):
        # Configuração
        np.random.seed(42)
        n = 100
        mu = 0.0005
        sigma = 0.02
        returns = pd.Series(np.random.normal(mu, sigma, n))

        # Execução
        params = monte_carlo_engine._estimate_params(returns, vol_method=vol_method)

        # Verificação
        assert 'mu' in params
        assert 'sigma' in params
        assert isinstance(params['mu'], float)
        assert isinstance(params['sigma'], float)
        assert abs(params['sigma'] - sigma) < 0.05  # Tolerância para variação

    @pytest.mark.skipif(True, reason="Requires arch package")
    def test_estimate_params_garch(self, monte_carlo_engine):
        # Teste para o método GARCH (requer o pacote arch)
        np.random.seed(42)
        n = 1000
        returns = pd.Series(np.random.normal(0, 0.02, n))
        
        params = monte_carlo_engine._estimate_params(returns, vol_method='garch')
        
        assert 'mu' in params
        assert 'sigma' in params
        assert isinstance(params['mu'], float)
        assert isinstance(params['sigma'], float)
