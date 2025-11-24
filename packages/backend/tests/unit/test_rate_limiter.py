import pytest
import time
from fastapi import Request, HTTPException
from backend_projeto.infrastructure.utils.rate_limiter import InMemoryRateLimiter


class MockRequest:
    """Mock de Request para testes."""
    def __init__(self, client_host: str = "127.0.0.1", headers: dict = None):
        self.client = type('obj', (object,), {'host': client_host})
        self.headers = headers or {}


class TestInMemoryRateLimiter:
    def test_allows_requests_within_limit(self):
        limiter = InMemoryRateLimiter(max_requests=5, window_seconds=60)
        request = MockRequest()
        
        for i in range(5):
            allowed, remaining, reset = limiter.check_rate_limit(request)
            assert allowed is True
            assert remaining == 4 - i
    
    def test_blocks_requests_exceeding_limit(self):
        limiter = InMemoryRateLimiter(max_requests=3, window_seconds=60)
        request = MockRequest()
        
        # Primeiras 3 permitidas
        for _ in range(3):
            allowed, _, _ = limiter.check_rate_limit(request)
            assert allowed is True
        
        # 4ª bloqueada
        allowed, remaining, reset = limiter.check_rate_limit(request)
        assert allowed is False
        assert remaining == 0
        assert reset > 0
    
    def test_resets_after_window(self):
        limiter = InMemoryRateLimiter(max_requests=2, window_seconds=1)
        request = MockRequest()
        
        # 2 requisições
        limiter.check_rate_limit(request)
        limiter.check_rate_limit(request)
        
        # 3ª bloqueada
        allowed, _, _ = limiter.check_rate_limit(request)
        assert allowed is False
        
        # Aguardar janela passar
        time.sleep(1.1)
        
        # Deve permitir novamente
        allowed, _, _ = limiter.check_rate_limit(request)
        assert allowed is True
    
    def test_different_clients_independent(self):
        limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)
        request1 = MockRequest(client_host="192.168.1.1")
        request2 = MockRequest(client_host="192.168.1.2")
        
        # Cliente 1: 2 requisições
        limiter.check_rate_limit(request1)
        limiter.check_rate_limit(request1)
        
        # Cliente 1: bloqueado
        allowed, _, _ = limiter.check_rate_limit(request1)
        assert allowed is False
        
        # Cliente 2: ainda permitido
        allowed, _, _ = limiter.check_rate_limit(request2)
        assert allowed is True
    
    def test_uses_x_forwarded_for_header(self):
        limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
        request = MockRequest(
            client_host="127.0.0.1",
            headers={"X-Forwarded-For": "203.0.113.1, 198.51.100.1"}
        )
        
        # Primeira permitida
        allowed, _, _ = limiter.check_rate_limit(request)
        assert allowed is True
        
        # Segunda bloqueada (mesmo X-Forwarded-For)
        allowed, _, _ = limiter.check_rate_limit(request)
        assert allowed is False
    
    @pytest.mark.asyncio
    async def test_middleware_raises_429(self):
        limiter = InMemoryRateLimiter(max_requests=1, window_seconds=60)
        request = MockRequest()
        
        # Primeira: OK
        await limiter(request)
        
        # Segunda: deve levantar HTTPException 429
        with pytest.raises(HTTPException) as exc_info:
            await limiter(request)
        
        assert exc_info.value.status_code == 429
        assert "RateLimitExceeded" in str(exc_info.value.detail)
