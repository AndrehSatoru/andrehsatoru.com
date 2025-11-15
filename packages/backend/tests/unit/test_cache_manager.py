import pytest
from unittest.mock import MagicMock
from backend_projeto.utils.cache import CacheManager

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
    Testa um cache HIT, garantindo que o dataframe é desserializado corretamente.
    """
    # Arrange
    mock_redis_client = MagicMock()
    mock_pickle = mocker.patch('backend_projeto.utils.cache.pickle')
    mock_df = MagicMock()
    mock_pickle.loads.return_value = mock_df
    
    # Simula o Redis retornando dados serializados
    mock_redis_client.get.return_value = b"serialized_dataframe"

    cache = CacheManager(redis_host='dummy', redis_port=1234)
    cache.redis_client = mock_redis_client
    
    # Act
    result_df = cache.get_dataframe("prices", ["PETR4.SA"], "2024-01-01", "2024-12-31")

    # Assert
    cache.redis_client.get.assert_called_once()
    mock_pickle.loads.assert_called_once_with(b"serialized_dataframe")
    assert result_df == mock_df

def test_cache_manager_get_dataframe_miss():
    """
    Testa um cache MISS, garantindo que retorna None quando a chave não existe.
    """
    # Arrange
    mock_redis_client = MagicMock()
    mock_redis_client.get.return_value = None # Chave não encontrada

    cache = CacheManager(redis_host='dummy', redis_port=1234)
    cache.redis_client = mock_redis_client

    # Act
    result = cache.get_dataframe("prices", ["PETR4.SA"], "2024-01-01", "2024-12-31")

    # Assert
    assert result is None
