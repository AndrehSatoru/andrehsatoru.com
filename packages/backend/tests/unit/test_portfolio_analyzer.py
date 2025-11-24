"""
Testes unitários para o PortfolioAnalyzer.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from backend_projeto.domain.analysis import PortfolioAnalyzer
from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.infrastructure.utils.config import Settings

# Fixtures
@pytest.fixture
def sample_transactions():
    """Retorna um DataFrame de transações de exemplo para testes."""
    data = {
        'Data': [
            '2023-01-03', '2023-01-10', '2023-02-15', '2023-03-01',
            '2023-03-15', '2023-04-01', '2023-04-15', '2023-05-01'
        ],
        'Ativo': ['PETR4.SA', 'VALE3.SA', 'PETR4.SA', 'ITUB4.SA', 
                 'VALE3.SA', 'PETR4.SA', 'ITUB4.SA', 'VALE3.SA'],
        'Quantidade': [100, 50, -30, 200, -20, 50, -50, -10],
        'Preco': [25.0, 70.0, 28.0, 22.0, 75.0, 30.0, 25.0, 80.0],
        'Taxas': [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
    }
    return pd.DataFrame(data)

@pytest.fixture
def mock_data_loader():
    """Retorna um mock do YFinanceProvider."""
    loader = MagicMock(spec=YFinanceProvider)
    return loader

@pytest.fixture
def mock_config():
    """Retorna uma configuração de teste."""
    config = Settings()
    config.DIAS_UTEIS_ANO = 252
    return config

# Testes para PortfolioAnalyzer
class TestPortfolioAnalyzer:
    def test_initialization(self, sample_transactions, mock_data_loader, mock_config):
        """Testa a inicialização do PortfolioAnalyzer."""
        analyzer = PortfolioAnalyzer(
            transactions_df=sample_transactions,
            data_loader=mock_data_loader,
            config=mock_config,
            end_date='2023-06-30'
        )
        
        # Verifica se os atributos foram definidos corretamente
        assert len(analyzer.transactions) == len(sample_transactions)
        assert sorted(analyzer.assets) == ['ITUB4.SA', 'PETR4.SA', 'VALE3.SA']  # Ordem alfabética
        assert isinstance(analyzer.start_date, datetime)
        assert isinstance(analyzer.end_date, datetime)
        assert analyzer.data_loader == mock_data_loader
        assert analyzer.config == mock_config

    def test_calculate_positions(self, sample_transactions, mock_data_loader, mock_config):
        """Testa o cálculo das posições ao longo do tempo."""
        analyzer = PortfolioAnalyzer(
            transactions_df=sample_transactions,
            data_loader=mock_data_loader,
            config=mock_config,
            end_date='2023-06-30'
        )
        
        # Chama o método diretamente (é chamado internamente pelo __init__)
        positions = analyzer._calculate_positions()
        
        # Verificações
        assert isinstance(positions, pd.DataFrame)
        assert not positions.empty
        assert all(asset in positions.columns for asset in analyzer.assets)
        
        # Verifica se as posições finais estão corretas
        final_positions = positions.iloc[-1]
        assert final_positions['PETR4.SA'] == 120  # 100 - 30 + 50
        assert final_positions['VALE3.SA'] == 20   # 50 - 20 - 10
        assert final_positions['ITUB4.SA'] == 150  # 200 - 50

    def test_calculate_portfolio_value(self, sample_transactions, mock_data_loader, mock_config):
        """Testa o cálculo do valor do portfólio."""
        analyzer = PortfolioAnalyzer(
            transactions_df=sample_transactions,
            data_loader=mock_data_loader,
            config=mock_config,
            end_date='2023-06-30'
        )

        dates = analyzer._calculate_positions().index
        prices = pd.DataFrame({
            'PETR4.SA': np.linspace(25, 35, len(dates)),
            'VALE3.SA': np.linspace(70, 85, len(dates)),
            'ITUB4.SA': np.linspace(20, 25, len(dates))
        }, index=dates)
        
        mock_data_loader.fetch_stock_prices.return_value = prices
        
        # Chama o método diretamente (é chamado internamente pelo __init__)
        portfolio_value = analyzer._calculate_portfolio_value()
        
        # Verificações
        assert isinstance(portfolio_value, pd.Series)
        assert not portfolio_value.empty
        assert portfolio_value.index.equals(prices.index)
        
        # O valor do portfólio não deve ser negativo
        assert (portfolio_value >= 0).all()

    def test_calculate_returns(self, sample_transactions, mock_data_loader, mock_config):
        """Testa o cálculo dos retornos do portfólio."""
        # Configura o mock para retornar preços de exemplo
        dates = pd.date_range(start='2023-01-01', end='2023-06-30', freq='B')
        prices = pd.DataFrame({
            'PETR4.SA': np.linspace(25, 35, len(dates)),
            'VALE3.SA': np.linspace(70, 85, len(dates)),
            'ITUB4.SA': np.linspace(20, 25, len(dates))
        }, index=dates)
        
        mock_data_loader.fetch_stock_prices.return_value = prices
        
        analyzer = PortfolioAnalyzer(
            transactions_df=sample_transactions,
            data_loader=mock_data_loader,
            config=mock_config,
            end_date='2023-06-30'
        )
        
        # Testa com retorno simples
        simple_returns = analyzer.calculate_returns(method='simple')
        assert isinstance(simple_returns, pd.Series)
        assert not simple_returns.empty
        
        # Testa com retorno logarítmico
        log_returns = analyzer.calculate_returns(method='log')
        assert isinstance(log_returns, pd.Series)
        assert not log_returns.empty
        
        # Verifica se os retornos têm o comprimento esperado
        assert len(log_returns) == len(simple_returns)
        
        # Verifica se há valores NaN ou infinitos
        assert not log_returns.isna().any()
        assert not np.isinf(log_returns).any()

    def test_analyze_performance(self, sample_transactions, mock_data_loader, mock_config):
        """Testa a análise de desempenho do portfólio."""
        # Configura o mock para retornar preços de exemplo
        dates = pd.date_range(start='2023-01-01', end='2023-06-30', freq='B')
        prices = pd.DataFrame({
            'PETR4.SA': np.linspace(25, 35, len(dates)),
            'VALE3.SA': np.linspace(70, 85, len(dates)),
            'ITUB4.SA': np.linspace(20, 25, len(dates))
        }, index=dates)
        
        mock_data_loader.fetch_stock_prices.return_value = prices
        
        analyzer = PortfolioAnalyzer(
            transactions_df=sample_transactions,
            data_loader=mock_data_loader,
            config=mock_config,
            end_date='2023-06-30'
        )
        
        # Executa a análise de desempenho
        performance = analyzer.analyze_performance()
        
        # Verifica se as métricas esperadas estão presentes
        expected_metrics = [
            'retorno_total_%', 'retorno_anualizado_%', 'volatilidade_anual_%',
            'indice_sharpe', 'max_drawdown_%'
        ]
        
        for metric in expected_metrics:
            assert metric in performance
            assert isinstance(performance[metric], (int, float))
        
        # Verifica se o Sharpe Ratio é razoável
        assert -10 <= performance['indice_sharpe'] <= 10
        
        # Verifica se o drawdown máximo está entre 0 e 100
        assert -100 <= performance['max_drawdown_%'] <= 0

    def test_analyze_allocation(self, sample_transactions, mock_data_loader, mock_config):
        """Testa a análise de alocação do portfólio."""
        analyzer = PortfolioAnalyzer(
            transactions_df=sample_transactions,
            data_loader=mock_data_loader,
            config=mock_config,
            end_date='2023-06-30'
        )
        
        # Garante que o mock de preços tenha o mesmo índice que as posições calculadas
        dates = analyzer._calculate_positions().index
        prices = pd.DataFrame({
            'PETR4.SA': np.linspace(25, 35, len(dates)),
            'VALE3.SA': np.linspace(70, 85, len(dates)),
            'ITUB4.SA': np.linspace(20, 25, len(dates))
        }, index=dates)
        
        mock_data_loader.fetch_stock_prices.return_value = prices

        # Testa a alocação na data mais recente
        allocation_data = analyzer.analyze_allocation()
        
        # Verifica se a alocação está correta
        assert isinstance(allocation_data, dict)
        allocation = allocation_data.get('alocacao', {})
        assert all(asset in allocation for asset in analyzer.assets)
        
        # A soma das alocações deve ser aproximadamente 100
        assert abs(sum(item['percentual'] for item in allocation.values()) - 100.0) < 1e-9
        
        # Testa com uma data específica
        specific_date = '2023-04-17' # Usar um dia útil
        allocation_specific = analyzer.analyze_allocation(date=specific_date)
        assert isinstance(allocation_specific.get('alocacao'), dict)

    def test_run_analysis(self, sample_transactions, mock_data_loader, mock_config):
        """Testa a execução de uma análise completa do portfólio."""
        analyzer = PortfolioAnalyzer(
            transactions_df=sample_transactions,
            data_loader=mock_data_loader,
            config=mock_config,
            end_date='2023-06-30'
        )

        dates = analyzer._calculate_positions().index
        prices = pd.DataFrame({
            'PETR4.SA': np.linspace(25, 35, len(dates)),
            'VALE3.SA': np.linspace(70, 85, len(dates)),
            'ITUB4.SA': np.linspace(20, 25, len(dates))
        }, index=dates)
        
        mock_data_loader.fetch_stock_prices.return_value = prices
        
        # Executa a análise completa
        analysis = analyzer.run_analysis()
        
        # Verifica se todas as seções esperadas estão presentes
        expected_sections = [
            'desempenho', 'alocacao', 'metadados'
        ]
        
        for section in expected_sections:
            assert section in analysis
            assert analysis[section] is not None
        
        # Verifica se os retornos foram calculados
        assert 'retorno_total_%' in analysis['desempenho']
        
        # Verifica se as posições foram calculadas
        assert 'alocacao' in analysis['alocacao']
        assert not analysis['alocacao']['alocacao'] == {}

# Testes para erros e casos extremos
class TestPortfolioAnalyzerEdgeCases:
    def test_empty_transactions(self, mock_data_loader, mock_config):
        """Testa o comportamento com DataFrame de transações vazio."""
        empty_df = pd.DataFrame(columns=['Data', 'Ativo', 'Quantidade', 'Preco', 'Taxas'])
        
        with pytest.raises(ValueError, match="Nenhuma transação fornecida"):
            PortfolioAnalyzer(
                transactions_df=empty_df,
                data_loader=mock_data_loader,
                config=mock_config
            )
    
    def test_missing_columns(self, mock_data_loader, mock_config):
        """Testa o comportamento com colunas ausentes no DataFrame de transações."""
        invalid_df = pd.DataFrame({
            'Data': ['2023-01-01'],
            'Ativo': ['PETR4.SA'],
            'Quantidade': [100],
            # 'Preco' column is missing
        })
        
        with pytest.raises(ValueError, match="deve conter as colunas"):
            PortfolioAnalyzer(
                transactions_df=invalid_df,
                data_loader=mock_data_loader,
                config=mock_config
            )
    
    def test_invalid_transaction_dates(self, mock_data_loader, mock_config):
        """Testa o comportamento com datas de transação inválidas."""
        invalid_dates_df = pd.DataFrame({
            'Data': ['2023-13-01', '2023-01-32'],  # Datas inválidas
            'Ativo': ['PETR4.SA', 'VALE3.SA'],
            'Quantidade': [100, 50],
            'Preco': [25.0, 70.0],
            'Taxas': [5.0, 5.0]
        })
        
        with pytest.raises(ValueError, match="month must be in 1..12"):
            PortfolioAnalyzer(
                transactions_df=invalid_dates_df,
                data_loader=mock_data_loader,
                config=mock_config
            )

# Testes de integração (usando dados reais)
class TestPortfolioAnalyzerIntegration:
    @pytest.mark.skip(reason="Integration test requires live data and may fail with insufficient data")
    @pytest.mark.integration
    def test_complete_workflow(self):
        """Testa um fluxo completo de análise de portfólio com dados reais."""
        # Este teste é marcado como integração e será pulado por padrão
        # Execute com: pytest -m integration
        
        # Cria um DataFrame de transações de exemplo
        transactions = pd.DataFrame({
            'Data': ['2023-01-03', '2023-02-01', '2023-03-01', '2023-04-03'],
            'Ativo': ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'PETR4.SA'],
            'Quantidade': [100, 50, 200, -50],
            'Preco': [25.0, 70.0, 22.0, 28.0],
            'Taxas': [5.0, 5.0, 5.0, 5.0]
        })
        
        # Cria uma instância do PortfolioAnalyzer com o YFinanceProvider real
        analyzer = PortfolioAnalyzer(
            transactions_df=transactions,
            data_loader=YFinanceProvider(config=Settings()), # Pass config here
            config=Settings()
        )
        
        # Executa a análise completa
        analysis = analyzer.run_analysis()
        
        # Verificações básicas
        assert 'desempenho' in analysis
        assert 'alocacao' in analysis
        
        # Verifica se os retornos foram calculados
        assert 'retorno_total_%' in analysis['desempenho']
        
        # Verifica se as posições foram calculadas
        assert 'alocacao' in analysis['alocacao']
        
        # Verifica se a alocação está correta
        allocation = analysis['alocacao']['alocacao']
        assert isinstance(allocation, dict)
        assert abs(sum(item['percentual'] for item in allocation.values()) - 100.0) < 1e-9  # Soma ~= 100%
