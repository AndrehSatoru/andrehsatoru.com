import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from backend_projeto.infrastructure.utils.cache import CacheManager
import json

@pytest.fixture
def mock_redis_client():
    mock = MagicMock()
    return mock

@pytest.fixture
def cache_manager(mock_redis_client):
    manager = CacheManager(enabled=True, redis_host='localhost', redis_port=6379)
    manager.redis_client = mock_redis_client
    # Limpar cache em memória
    manager.memory_cache.clear()
    return manager

def test_cache_manager_generate_key():
    """
    Testa se a geração de chaves do CacheManager é determinística e correta.
    """
    # Arrange
    cache = CacheManager(redis_host='dummy', redis_port=1234)
    cache.redis_client = MagicMock() # Mock para evitar conexão real

    prefix = "prices"
    assets = ["PETR4.SA", "VALE3.SA"]
    start_date = "2024-01-01"
    end_date = "2024-12-31"

    # Act
    key = cache._generate_key(prefix, assets, start_date, end_date)

    # Assert
    assert key == "cache:prices:PETR4.SA_VALE3.SA:2024-01-01:2024-12-31"

def test_cache_manager_get_dataframe_hit(mocker):
    """
    Testa um cache HIT, garantindo que o dataframe é desserializado corretamente via JSON.
    """
    # Arrange
    mock_redis_client = MagicMock()
    
    # Setup do mock do Redis para retornar dados serializados em JSON
    expected_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    serialized_data = json.dumps({
        'data': [[1, 3], [2, 4]],
        'index': [0, 1],
        'columns': ['col1', 'col2']
    })
    
    mock_redis_client.get.return_value = serialized_data
    
    manager = CacheManager(enabled=True)
    manager.redis_client = mock_redis_client
    
    # Act
    result = manager.get_dataframe('test_prefix', ['asset1'], '2023-01-01', '2023-01-05')
    
    # Assert
    assert result is not None
    assert isinstance(result, pd.DataFrame)
    # Verificar colunas e dados
    assert list(result.columns) == ['col1', 'col2']
    assert result.iloc[0, 0] == 1
    mock_redis_client.get.assert_called_once()

def test_cache_manager_get_dataframe_miss(mocker):
    """
    Testa um cache MISS (retorno None).
    """
    # Arrange
    mock_redis_client = MagicMock()
    mock_redis_client.get.return_value = None
    
    manager = CacheManager(enabled=True)
    manager.redis_client = mock_redis_client
    
    # Act
    result = manager.get_dataframe('test_prefix', ['asset1'], '2023-01-01', '2023-01-05')
    
    # Assert
    assert result is None
    mock_redis_client.get.assert_called_once()

def test_cache_manager_set_dataframe(mocker):
    """
    Testa a gravação no cache (SET) com JSON.
    """
    # Arrange
    mock_redis_client = MagicMock()
    
    manager = CacheManager(enabled=True)
    manager.redis_client = mock_redis_client
    
    # Criar DF com datas no índice para testar serialização completa
    dates = pd.date_range(start='2023-01-01', periods=2)
    df = pd.DataFrame({'col1': [1, 2]}, index=dates)
    
    # Act
    manager.set_dataframe(df, 'test_prefix', ['asset1'], '2023-01-01', '2023-01-05')
    
    # Assert
    mock_redis_client.setex.assert_called_once()
    args, _ = mock_redis_client.setex.call_args
    assert args[1] == 86400  # TTL padrão
    
    # Verificar se o valor gravado é um JSON válido
    saved_json = json.loads(args[2])
    assert 'data' in saved_json
    assert 'index' in saved_json
    assert 'columns' in saved_json
    assert saved_json['columns'] == ['col1']

def test_cache_manager_disabled():
    """
    Testa o comportamento quando o cache está desabilitado.
    """
    # Arrange
    manager = CacheManager(enabled=False)
    
    # Act
    result = manager.get_dataframe('test', ['a'], '2023-01-01', '2023-01-02')
    manager.set_dataframe(pd.DataFrame(), 'test', ['a'], '2023-01-01', '2023-01-02')
    
    # Assert
    assert result is None
    assert manager.redis_client is None

def test_cache_manager_memory_fallback(mocker):
    """
    Testa o fallback para memória quando Redis falha ou retorna None.
    """
    # Arrange
    mock_redis_client = MagicMock()
    # Simula falha no Redis (exceção)
    mock_redis_client.get.side_effect = Exception("Redis error")
    
    manager = CacheManager(enabled=True)
    manager.redis_client = mock_redis_client
    
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    
    # Salva no cache (deve salvar na memória também)
    manager.set_dataframe(df, 'test_prefix', ['asset1'], '2023-01-01', '2023-01-05')
    
    # Act
    # Tenta recuperar (deve vir da memória pois Redis falha)
    result = manager.get_dataframe('test_prefix', ['asset1'], '2023-01-01', '2023-01-05')
    
    # Assert
    assert result is not None
    pd.testing.assert_frame_equal(result, df)