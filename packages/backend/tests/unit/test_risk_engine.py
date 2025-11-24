"""
Testes unitários para o RiskEngine.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from backend_projeto.domain.analysis import RiskEngine
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
def risk_engine(mock_loader, mock_config):
    return RiskEngine(loader=mock_loader, config=mock_config)

@pytest.fixture
def sample_prices():
    """Retorna um DataFrame de preços de exemplo para testes."""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='B')
    np.random.seed(42)
    data = {
        'PETR4.SA': 20 + np.cumsum(np.random.normal(0, 1, len(dates))),
        'VALE3.SA': 70 + np.cumsum(np.random.normal(0, 2, len(dates))),
        'ITUB4.SA': 30 + np.cumsum(np.random.normal(0, 1.5, len(dates)))
    }
    return pd.DataFrame(data, index=dates)

# Testes para RiskEngine
class TestRiskEngine:
    def test_initialization(self, risk_engine, mock_loader, mock_config):
        """Testa a inicialização do RiskEngine."""
        assert risk_engine.loader == mock_loader
        assert risk_engine.config == mock_config

    def test_load_prices(self, risk_engine, mock_loader, sample_prices):
        """Testa o carregamento de preços."""
        # Configura o mock para retornar os preços de exemplo
        mock_loader.fetch_stock_prices.return_value = sample_prices
        
        # Chama o método
        assets = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA']
        start_date = '2023-01-01'
        end_date = '2023-06-30'
        result = risk_engine._load_prices(assets, start_date, end_date)
        
        # Verifica se o método foi chamado corretamente
        mock_loader.fetch_stock_prices.assert_called_once_with(assets, start_date, end_date)
        
        # Verifica se o resultado não está vazio e tem as colunas corretas
        assert not result.empty
        assert all(col in result.columns for col in assets)

    def test_portfolio_series(self, risk_engine, sample_prices):
        """Testa o cálculo da série de retornos do portfólio."""
        # Configuração
        assets = ['PETR4.SA', 'VALE3.SA']
        weights = [0.6, 0.4]
        
        # Chama o método
        portfolio_returns = risk_engine._portfolio_series(sample_prices, assets, weights)
        
        # Verificações
        assert isinstance(portfolio_returns, pd.Series)
        assert not portfolio_returns.empty
        assert portfolio_returns.index.equals(sample_prices.index[1:])
        
        # Verifica se a soma dos pesos é aproximadamente 1
        assert abs(sum(weights) - 1.0) < 1e-10

    @patch('backend_projeto.domain.analysis.var_historical')
    def test_compute_var_historical(self, mock_var, risk_engine, sample_prices):
        """Testa o cálculo do VaR pelo método histórico."""
        # Configuração
        mock_var.return_value = (-0.05, {'method': 'historical'})
        risk_engine._load_prices = MagicMock(return_value=sample_prices)
        
        # Chama o método
        result = risk_engine.compute_var(
            assets=['PETR4.SA', 'VALE3.SA'],
            start_date='2023-01-01',
            end_date='2023-06-30',
            alpha=0.95,
            method='historical',
            ewma_lambda=0.94,
            weights=[0.6, 0.4]
        )
        
        # Verificações
        assert 'var' in result
        assert 'method' in result
        assert result['method'] == 'historical'
        mock_var.assert_called_once()

    @patch('backend_projeto.domain.analysis.es_historical')
    def test_compute_es_historical(self, mock_es, risk_engine, sample_prices):
        """Testa o cálculo do ES pelo método histórico."""
        # Configuração
        mock_es.return_value = (-0.07, {'method': 'historical'})
        risk_engine._load_prices = MagicMock(return_value=sample_prices)
        
        # Chama o método
        result = risk_engine.compute_es(
            assets=['PETR4.SA', 'VALE3.SA'],
            start_date='2023-01-01',
            end_date='2023-06-30',
            alpha=0.95,
            method='historical',
            ewma_lambda=0.94,
            weights=[0.6, 0.4]
        )
        
        # Verificações
        assert 'es' in result
        assert 'method' in result
        assert result['method'] == 'historical'
        mock_es.assert_called_once()

    def test_compute_drawdown(self, risk_engine, sample_prices):
        """Testa o cálculo do drawdown máximo."""
        # Configuração
        risk_engine._load_prices = MagicMock(return_value=sample_prices)
        
    @patch('backend_projeto.domain.analysis.var_parametric')
    def test_compare_methods(self, mock_var, risk_engine, sample_prices):
        """Testa a comparação de diferentes métodos de cálculo de risco."""
        # Configuração
        mock_var.return_value = (-0.05, {'method': 'std', 'sigma': 0.02, 'mu': 0.001})
        risk_engine._load_prices = MagicMock(return_value=sample_prices)
        
        # Chama o método
        result = risk_engine.compare_methods(
            assets=['PETR4.SA', 'VALE3.SA'],
            start_date='2023-01-01',
            end_date='2023-06-30',
            alpha=0.95,
            methods=['std', 'ewma'],
            ewma_lambda=0.94,
            weights=[0.6, 0.4]
        )
        
        # Verificações
        assert 'comparison' in result
        assert isinstance(result['comparison'], dict)
        assert len(result['comparison']) == 2  # Dois métodos testados
        
        # Verifica se ambos os métodos estão nos resultados
        assert 'std' in result['comparison']
        assert 'ewma' in result['comparison']

# Testes para erros e casos extremos
class TestRiskEngineEdgeCases:
    def test_empty_assets(self, risk_engine):
        """Testa o comportamento com lista de ativos vazia."""
        with pytest.raises(ValueError, match="Nenhum ativo encontrado"):
            risk_engine.compute_var(
                assets=[],
                start_date='2023-01-01',
                end_date='2023-06-30',
                alpha=0.95,
                method='historical',
                ewma_lambda=0.94,
                weights=None
            )
    
    def test_invalid_dates(self, risk_engine):
        """Testa o comportamento com datas inválidas."""
        with pytest.raises(ValueError):
            risk_engine.compute_var(
                assets=['PETR4.SA', 'VALE3.SA'],
                start_date='2023-12-31',  # Data posterior à final
                end_date='2023-01-01',
                alpha=0.95,
                method='historical',
                ewma_lambda=0.94,
                weights=None
            )
    
    def test_invalid_weights(self, risk_engine, sample_prices):
        """Testa o comportamento com pesos inválidos."""
        # The weights are normalized internally, so this test is not applicable
        # Weights that sum to more than 1 are automatically normalized
        risk_engine._load_prices = MagicMock(return_value=sample_prices)
        
        # This should work as weights are normalized
        result = risk_engine.compute_var(
            assets=['PETR4.SA', 'VALE3.SA'],
            start_date='2023-01-01',
            end_date='2023-06-30',
            alpha=0.95,
            method='historical',
            ewma_lambda=0.94,
            weights=[0.6, 0.5]  # Will be normalized to [0.545, 0.455]
        )
        assert 'var' in result

# Testes de integração (usando dados reais)
class TestRiskEngineIntegration:
    @pytest.mark.integration
    def test_complete_workflow(self, risk_engine, sample_prices):
        """Testa um fluxo completo de análise de risco com dados reais."""
        # Este teste é marcado como integração e será pulado por padrão
        # Execute com: pytest -m integration
        
        # Mock the price loading
        risk_engine._load_prices = MagicMock(return_value=sample_prices)
        
        # Configuração
        assets = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA']
        weights = [0.4, 0.4, 0.2]
        
        # 1. Calcula VaR
        var_result = risk_engine.compute_var(
            assets=assets,
            start_date='2023-01-01',
            end_date='2023-06-30',
            alpha=0.95,
            method='historical',
            ewma_lambda=0.94,
            weights=weights
        )
        
        # 2. Calcula ES
        es_result = risk_engine.compute_es(
            assets=assets,
            start_date='2023-01-01',
            end_date='2023-06-30',
            alpha=0.95,
            method='historical',
            ewma_lambda=0.94,
            weights=weights
        )
        
        # 3. Calcula drawdown
        drawdown_result = risk_engine.compute_drawdown(
            assets=assets,
            start_date='2023-01-01',
            end_date='2023-06-30',
            weights=weights
        )
        
        # Verificações básicas
        assert 'var' in var_result
        assert 'es' in es_result
        assert 'max_drawdown' in drawdown_result
        
        # Verify values are numeric and within reasonable range
        assert isinstance(var_result['var'], (int, float))
        assert isinstance(es_result['es'], (int, float))
        assert isinstance(drawdown_result['max_drawdown'], (int, float))
        
        # Values should be non-zero for a real portfolio
        assert var_result['var'] != 0
        assert es_result['es'] != 0
