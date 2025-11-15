"""
Testes unitários para o DashboardGenerator.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import plotly.graph_objects as go

from src.backend_projeto.core.dashboard_generator import DashboardGenerator
from src.backend_projeto.utils.config import Settings

# Fixtures
@pytest.fixture
def mock_config():
    config = Settings()
    config.DIAS_UTEIS_ANO = 252
    return config

@pytest.fixture
def sample_data():
    """Retorna dados de exemplo para os testes."""
    # Criar índice de datas
    dates = pd.date_range(start='2023-01-01', periods=100, freq='B')
    
    # Criar dados de preços
    np.random.seed(42)
    n_assets = 3
    assets = [f'ASSET_{i+1}' for i in range(n_assets)]
    
    # Criar preços com alguma correlação
    base = np.cumsum(np.random.normal(0.001, 0.02, (len(dates), 1)), axis=0) + 100
    noise = np.random.normal(0, 0.01, (len(dates), n_assets))
    prices = pd.DataFrame(
        base + np.hstack([base * 0.5] + [base * 0.1 * (i+1) for i in range(n_assets-1)]) + noise,
        index=dates,
        columns=assets
    )
    
    # Criar retornos
    returns = prices.pct_change().dropna()
    
    # Criar pesos
    weights = pd.Series(
        np.random.dirichlet(np.ones(n_assets), size=1).flatten(),
        index=assets
    )
    
    return {
        'prices': prices,
        'returns': returns,
        'weights': weights,
        'benchmark_returns': returns.mean(axis=1),  # Benchmark simples
        'risk_free_rate': 0.01
    }

# Testes para a classe DashboardGenerator
class TestDashboardGenerator:
    def test_initialization(self, mock_config):
        """Testa a inicialização do DashboardGenerator."""
        dashboard = DashboardGenerator(config=mock_config)
        assert dashboard.config == mock_config
        assert dashboard.fig is not None
        
    def test_add_title(self, mock_config):
        """Testa a adição de um título ao dashboard."""
        dashboard = DashboardGenerator(config=mock_config)
        title = "Meu Dashboard de Teste"
        dashboard.add_title(title)
        
        # Verificar se o título foi adicionado corretamente
        assert dashboard.fig.layout.title.text == title
        
    def test_add_returns_chart(self, mock_config, sample_data):
        """Testa a adição de um gráfico de retornos."""
        dashboard = DashboardGenerator(config=mock_config)
        returns = sample_data['returns']
        
        # Adicionar gráfico de retornos
        dashboard.add_returns_chart(
            returns=returns,
            title="Retornos Diários",
            show_legend=True
        )
        
        # Verificar se o gráfico foi adicionado
        assert len(dashboard.fig.data) > 0
        assert dashboard.fig.layout.title.text == "Retornos Diários"
        
    def test_add_drawdown_chart(self, mock_config, sample_data):
        """Testa a adição de um gráfico de drawdown."""
        dashboard = DashboardGenerator(config=mock_config)
        prices = sample_data['prices']
        
        # Adicionar gráfico de drawdown
        dashboard.add_drawdown_chart(
            prices=prices,
            title="Drawdown",
            show_legend=True
        )
        
        # Verificar se o gráfico foi adicionado
        assert len(dashboard.fig.data) > 0
        
    def test_add_rolling_volatility_chart(self, mock_config, sample_data):
        """Testa a adição de um gráfico de volatilidade rolante."""
        dashboard = DashboardGenerator(config=mock_config)
        returns = sample_data['returns']
        
        # Adicionar gráfico de volatilidade
        dashboard.add_rolling_volatility_chart(
            returns=returns,
            window=21,
            title="Volatilidade Móvel (21 dias)",
            show_legend=True
        )
        
        # Verificar se o gráfico foi adicionado
        assert len(dashboard.fig.data) > 0
        
    def test_add_correlation_heatmap(self, mock_config, sample_data):
        """Testa a adição de um mapa de calor de correlação."""
        dashboard = DashboardGenerator(config=mock_config)
        returns = sample_data['returns']
        
        # Adicionar mapa de calor
        dashboard.add_correlation_heatmap(
            returns=returns,
            title="Matriz de Correlação"
        )
        
        # Verificar se o heatmap foi adicionado
        assert len(dashboard.fig.data) > 0
        
    def test_add_portfolio_allocation(self, mock_config, sample_data):
        """Testa a adição de um gráfico de alocação de portfólio."""
        dashboard = DashboardGenerator(config=mock_config)
        weights = sample_data['weights']
        
        # Adicionar gráfico de alocação
        dashboard.add_portfolio_allocation(
            weights=weights,
            title="Alocação do Portfólio"
        )
        
        # Verificar se o gráfico de pizza foi adicionado
        assert len(dashboard.fig.data) > 0
        
    def test_add_risk_metrics_table(self, mock_config, sample_data):
        """Testa a adição de uma tabela de métricas de risco."""
        dashboard = DashboardGenerator(config=mock_config)
        returns = sample_data['returns']
        
        # Adicionar tabela de métricas
        dashboard.add_risk_metrics_table(
            returns=returns,
            risk_free_rate=0.01,
            title="Métricas de Risco"
        )
        
        # Verificar se a tabela foi adicionada
        assert len(dashboard.fig.layout.annotations) > 0
        
    def test_save_dashboard(self, mock_config, tmp_path):
        """Testa o salvamento do dashboard em um arquivo HTML."""
        dashboard = DashboardGenerator(config=mock_config)
        output_path = tmp_path / "test_dashboard.html"
        
        # Adicionar um título para ter algo no dashboard
        dashboard.add_title("Dashboard de Teste")
        
        # Salvar o dashboard
        result_path = dashboard.save_dashboard(output_path)
        
        # Verificar se o arquivo foi criado
        assert result_path == str(output_path)
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        
    def test_show_dashboard(self, mock_config):
        """Testa a exibição do dashboard (apenas verifica se não há erros)."""
        dashboard = DashboardGenerator(config=mock_config)
        dashboard.add_title("Dashboard de Teste")
        
        # Não podemos testar a exibição real, mas podemos verificar se o método existe
        # e não levanta exceções
        try:
            dashboard.show_dashboard()
            assert True
        except Exception as e:
            pytest.fail(f"show_dashboard() falhou com erro: {e}")

# Testes para erros e casos extremos
class TestErrorHandling:
    def test_empty_data(self, mock_config):
        """Testa o comportamento com dados vazios."""
        dashboard = DashboardGenerator(config=mock_config)
        
        # Testar com DataFrame vazio
        empty_df = pd.DataFrame()
        
        with pytest.raises(ValueError):
            dashboard.add_returns_chart(returns=empty_df, title="Teste")
            
        with pytest.raises(ValueError):
            dashboard.add_drawdown_chart(prices=empty_df, title="Teste")
            
    def test_invalid_weights(self, mock_config, sample_data):
        """Testa o comportamento com pesos inválidos."""
        dashboard = DashboardGenerator(config=mock_config)
        
        # Pesos que não somam 1
        invalid_weights = pd.Series({"A": 0.4, "B": 0.5})  # Soma 0.9
        
        with pytest.raises(ValueError):
            dashboard.add_portfolio_allocation(weights=invalid_weights, title="Teste")
            
        # Pesos com valores negativos
        negative_weights = pd.Series({"A": 0.8, "B": 0.3})  # Soma 1.1
        
        with pytest.raises(ValueError):
            dashboard.add_portfolio_allocation(weights=negative_weights, title="Teste")

# Testes de integração entre os componentes do dashboard
class TestDashboardIntegration:
    def test_complete_dashboard(self, mock_config, sample_data, tmp_path):
        """Testa a criação de um dashboard completo com múltiplos componentes."""
        # Criar dashboard
        dashboard = DashboardGenerator(
            config=mock_config,
            title="Dashboard Completo de Teste",
            rows=2,
            cols=2,
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "heatmap"}, {"type": "pie"}]]
        )
        
        # Adicionar vários componentes
        dashboard.add_returns_chart(
            returns=sample_data['returns'],
            title="Retornos Diários",
            row=1, col=1
        )
        
        dashboard.add_drawdown_chart(
            prices=sample_data['prices'],
            title="Drawdown",
            row=1, col=2
        )
        
        dashboard.add_correlation_heatmap(
            returns=sample_data['returns'],
            title="Matriz de Correlação",
            row=2, col=1
        )
        
        dashboard.add_portfolio_allocation(
            weights=sample_data['weights'],
            title="Alocação do Portfólio",
            row=2, col=2
        )
        
        # Adicionar métricas de risco como anotações
        dashboard.add_risk_metrics_table(
            returns=sample_data['returns'],
            risk_free_rate=sample_data['risk_free_rate'],
            title="Métricas de Risco"
        )
        
        # Salvar o dashboard
        output_path = tmp_path / "complete_dashboard.html"
        dashboard.save_dashboard(output_path)
        
        # Verificações básicas
        assert output_path.exists()
        assert output_path.stat().st_size > 0
        
        # Verificar se todos os gráficos foram adicionados
        assert len(dashboard.fig.data) >= 4  # Pelo menos 4 traços (um por gráfico)
        
        # Verificar se o layout está correto
        assert dashboard.fig.layout.grid.rows == 2
        assert dashboard.fig.layout.grid.columns == 2
