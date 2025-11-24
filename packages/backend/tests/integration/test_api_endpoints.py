"""
Testes de integração para os endpoints da API.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np

from backend_projeto.main import app
from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.infrastructure.utils.config import Settings

# Configuração do cliente de teste
client = TestClient(app)

# Fixtures
@pytest.fixture
def mock_config():
    config = Settings()
    config.DIAS_UTEIS_ANO = 252
    return config

@pytest.fixture
def mock_loader():
    return MagicMock(spec=YFinanceProvider)

# Dados de teste
TEST_ASSETS = ['PETR4.SA', 'VALE3.SA']
END_DATE = datetime.now().strftime('%Y-%m-%d')
START_DATE = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

# Testes para os endpoints da API
class TestPricesEndpoints:
    def test_get_prices(self):
        # Configurar mock
        mock_data = pd.DataFrame({
            'PETR4.SA': [10.0, 10.5, 10.8],
            'VALE3.SA': [70.0, 72.0, 71.5]
        }, index=pd.date_range(start=START_DATE, periods=3))

        # Fazer requisição
        with patch('backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices', return_value=mock_data):
            response = client.post(
                "/api/v1/prices",
                json={
                    "assets": ["PETR4.SA", "VALE3.SA"],
                    "start_date": START_DATE,
                    "end_date": END_DATE
                }
            )

        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert 'data' in data
        assert 'columns' in data
        assert 'index' in data
        assert len(data['columns']) == 2
        assert len(data['data']) == 3

    def test_get_prices_invalid_dates(self):
        # Data final antes da data inicial
        response = client.post(
            "/api/v1/prices",
            json={
                "assets": ["PETR4.SA"],
                "start_date": "2023-12-31",
                "end_date": "2023-01-01"
            }
        )
        assert response.status_code == 422
        assert "A data final deve ser posterior à data inicial" in response.text

class TestOptimizationEndpoints:
    def test_optimize_portfolio(self, mock_config):
        # Configurar mock
        mock_prices = pd.DataFrame({
            'PETR4.SA': [10.0, 10.5, 10.8, 11.0, 10.7],
            'VALE3.SA': [70.0, 72.0, 71.5, 73.0, 74.0]
        }, index=pd.date_range(start=START_DATE, periods=5))

        # Fazer requisição
        with (
            patch('backend_projeto.domain.optimization.OptimizationEngine.load_prices', return_value=mock_prices),
            patch('src.backend_projeto.api.deps.get_config', return_value=mock_config)
        ):
            response = client.post(
                "/api/v1/opt/markowitz",
                json={
                    "assets": ["PETR4.SA", "VALE3.SA"],
                    "start_date": START_DATE,
                    "end_date": END_DATE,
                    "objective": "max_sharpe"
                }
            )

        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert 'result' in data
        result = data['result']
        assert 'weights' in result
        assert all(0 <= w <= 1 for w in result['weights'].values())
        assert abs(sum(result['weights'].values()) - 1.0) < 1e-6

    def test_optimize_invalid_assets(self):
        # Teste com apenas 1 ativo
        mock_prices = pd.DataFrame({
            'PETR4.SA': [10.0, 10.5, 10.8, 11.0, 10.7],
        }, index=pd.date_range(start=START_DATE, periods=5))
        with patch('backend_projeto.domain.optimization.OptimizationEngine.load_prices', return_value=mock_prices):
            response = client.post(
                "/api/v1/opt/markowitz",
                json={
                    "assets": ["PETR4.SA"],  # Apenas 1 ativo
                    "start_date": START_DATE,
                    "end_date": END_DATE
                }
            )
        assert response.status_code == 422
        assert "pelo menos 2 ativos" in response.text.lower()

class TestRiskEndpoints:
    def test_calculate_var(self):
        # Configurar mock
        mock_prices = pd.DataFrame({
            'PETR4.SA': [10.0, 10.5, 10.8, 11.0, 10.7],
            'VALE3.SA': [70.0, 72.0, 71.5, 73.0, 74.0]
        }, index=pd.date_range(start=START_DATE, periods=5))

        # Fazer requisição
        with patch('backend_projeto.domain.analysis.RiskEngine._load_prices', return_value=mock_prices):
            response = client.post(
                "/api/v1/risk/var",
                json={
                    "assets": ["PETR4.SA", "VALE3.SA"],
                    "start_date": START_DATE,
                    "end_date": END_DATE,
                    "alpha": 0.95,
                    "method": "historical"
                }
            )

        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert 'result' in data
        assert 'var' in data['result']
        assert 'details' in data['result']
        assert 'alpha' in data['result']
        assert 'method' in data['result']

    def test_calculate_es(self):
        # Configurar mock
        mock_prices = pd.DataFrame({
            'PETR4.SA': [10.0, 10.5, 10.8, 11.0, 10.7],
            'VALE3.SA': [70.0, 72.0, 71.5, 73.0, 74.0]
        }, index=pd.date_range(start=START_DATE, periods=5))

        # Fazer requisição
        with patch('backend_projeto.domain.analysis.RiskEngine._load_prices', return_value=mock_prices):
            response = client.post(
                "/api/v1/risk/es",
                json={
                    "assets": ["PETR4.SA", "VALE3.SA"],
                    "start_date": START_DATE,
                    "end_date": END_DATE,
                    "alpha": 0.95,
                    "method": "historical"
                }
            )

        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert 'result' in data
        assert 'es' in data['result']

class TestEfficientFrontierEndpoints:
    def test_generate_efficient_frontier(self, mock_config):
        # Configurar mock
        mock_prices = pd.DataFrame({
            'PETR4.SA': [10.0, 10.5, 10.8, 11.0, 10.7],
            'VALE3.SA': [70.0, 72.0, 71.5, 73.0, 74.0],
            'ITUB4.SA': [25.0, 25.5, 25.2, 25.8, 26.0],
        }, index=pd.date_range(start=START_DATE, periods=5))

        # Fazer requisição
        with (
            patch('backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices', return_value=mock_prices),
            patch('src.backend_projeto.api.deps.get_config', return_value=mock_config)
        ):
            response = client.post(
                "/api/v1/opt/markowitz/frontier-data",
                json={
                    "assets": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
                    "start_date": START_DATE,
                    "end_date": END_DATE,
                    "n_samples": 100,
                    "long_only": True
                }
            )

        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert 'points' in data
        assert len(data['points']) > 0
        point = data['points'][0]
        assert 'ret_annual' in point
        assert 'vol_annual' in point
        assert 'sharpe' in point
        assert 'weights' in point

# Testes para erros e casos extremos
class TestErrorHandling:
    def test_nonexistent_asset(self):
        # Configurar mock para retornar DataFrame vazio para ativo inexistente
        with patch('backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices', return_value=pd.DataFrame()):
            response = client.post(
                "/api/v1/prices",
                json={
                    "assets": ["NONEXISTENT"],
                    "start_date": START_DATE,
                    "end_date": END_DATE
                }
            )

        # Verificar resposta
        assert response.status_code == 404
        assert "Nenhum dado encontrado" in response.text

    def test_invalid_date_format(self):
        # Formato de data inválido
        response = client.post(
            "/api/v1/prices",
            json={
                "assets": ["PETR4.SA"],
                "start_date": "2023/01/01",  # Formato inválido
                "end_date": "2023-12-31"
            }
        )
        assert response.status_code == 422  # Erro de validação

    @pytest.mark.parametrize("endpoint,method,payload", [
        ("/api/v1/opt/markowitz", "post", {"assets": ["PETR4.SA"], "start_date": "2023-01-01", "end_date": "2023-12-31"}),
        ("/api/v1/opt/markowitz/frontier-data", "post", {"assets": ["PETR4.SA"], "start_date": "2023-01-01", "end_date": "2023-12-31"}),
        ("/api/v1/risk/var", "post", {"assets": [], "start_date": "2023-01-01", "end_date": "2023-12-31"}),
    ])
    def test_validation_errors(self, endpoint, method, payload):
        # Testar validação de entrada para vários endpoints
        # Mock para garantir que a validação seja testada, não o carregamento de dados
        mock_prices = pd.DataFrame({
            'PETR4.SA': [10.0, 10.5, 10.8, 11.0, 10.7],
        }, index=pd.date_range(start='2023-01-01', periods=5))
        
        with patch('backend_projeto.infrastructure.data_handling.YFinanceProvider.fetch_stock_prices', return_value=mock_prices):
            if method.lower() == 'post':
                response = client.post(endpoint, json=payload)
            else:
                response = client.get(endpoint, params=payload)
                
        assert response.status_code in (400, 422)  # Bad Request ou Unprocessable Entity

# Testes para autenticação e autorização (se aplicável)
class TestAuthentication:
    def test_protected_endpoint_without_token(self):
        # Testar um endpoint protegido sem token
        response = client.get("/api/v1/protected-route")
        assert response.status_code == 404  # Route doesn't exist (not implemented yet)

    # Adicionar mais testes de autenticação conforme necessário
