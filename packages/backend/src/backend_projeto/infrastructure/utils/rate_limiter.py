# utils/rate_limiter.py
# Rate limiting simples baseado em memória

import time
import logging
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple
from fastapi import Request, HTTPException, status
import redis


class InMemoryRateLimiter:
    """Rate limiter simples baseado em memória (não distribuído).
    
    Para produção com múltiplos workers, use Redis ou similar.
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Parâmetros:
            max_requests: Número máximo de requisições por janela.
            window_seconds: Tamanho da janela em segundos.
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Dict[client_id, deque[timestamp]]
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)
        logging.info(
            f"RateLimiter inicializado: {max_requests} req/{window_seconds}s"
        )
    
    def _get_client_id(self, request: Request) -> str:
        """Identifica cliente por IP ou header."""
        # Priorizar X-Forwarded-For (se atrás de proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Fallback para client.host
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _clean_old_requests(self, client_id: str, now: float):
        """Remove requisições fora da janela."""
        cutoff = now - self.window_seconds
        queue = self.requests[client_id]
        
        while queue and queue[0] < cutoff:
            queue.popleft()
    
    def check_rate_limit(self, request: Request) -> Tuple[bool, int, int]:
        """Verifica se cliente excedeu rate limit.
        
        Retorna:
            (allowed, remaining, reset_in_seconds)
        """
        client_id = self._get_client_id(request)
        now = time.time()
        
        # Limpar requisições antigas
        self._clean_old_requests(client_id, now)
        
        queue = self.requests[client_id]
        current_count = len(queue)
        
        if current_count >= self.max_requests:
            # Rate limit excedido
            oldest = queue[0]
            reset_in = int(oldest + self.window_seconds - now) + 1
            return False, 0, reset_in
        
        # Permitido - adicionar timestamp
        queue.append(now)
        remaining = self.max_requests - len(queue)
        reset_in = self.window_seconds
        
        return True, remaining, reset_in
    
    async def __call__(self, request: Request):
        """Middleware callable para FastAPI."""
        allowed, remaining, reset_in = self.check_rate_limit(request)
        
        # Adicionar headers de rate limit
        request.state.rate_limit_remaining = remaining
        request.state.rate_limit_reset = reset_in
        
        if not allowed:
            client_id = self._get_client_id(request)
            logging.warning(
                f"[RateLimit] Cliente {client_id} excedeu limite: "
                f"{self.max_requests} req/{self.window_seconds}s"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "RateLimitExceeded",
                    "message": f"Limite de {self.max_requests} requisições por {self.window_seconds}s excedido",
                    "retry_after": reset_in,
                },
                headers={"Retry-After": str(reset_in)},
            )


class RedisRateLimiter:
    """Rate limiter distribuído usando Redis."""

    def __init__(self, redis_client: redis.Redis, max_requests: int = 100, window_seconds: int = 60):
        self.redis_client = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        logging.info(
            f"RedisRateLimiter inicializado: {max_requests} req/{window_seconds}s"
        )

    def _get_client_id(self, request: Request) -> str:
        # Same as InMemoryRateLimiter
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def __call__(self, request: Request):
        client_id = self._get_client_id(request)
        key = f"rate_limit:{client_id}"

        # INCR increments the key's value, creating it if it doesn't exist
        # It returns the new value
        current_requests = self.redis_client.incr(key)

        if current_requests == 1:
            # If it's the first request in the window, set the expiry
            self.redis_client.expire(key, self.window_seconds)
            reset_in = self.window_seconds
        else:
            # Get time to live for the key
            reset_in = self.redis_client.ttl(key)
            if reset_in == -1: # Key exists but has no expire set
                self.redis_client.expire(key, self.window_seconds)
                reset_in = self.window_seconds
            elif reset_in == -2: # Key does not exist (should not happen if incr returned > 0)
                reset_in = self.window_seconds # Fallback

        remaining = max(0, self.max_requests - current_requests)

        request.state.rate_limit_remaining = remaining
        request.state.rate_limit_reset = reset_in

        if current_requests > self.max_requests:
            logging.warning(
                f"[RedisRateLimit] Cliente {client_id} excedeu limite: "
                f"{self.max_requests} req/{self.window_seconds}s"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "RateLimitExceeded",
                    "message": f"Limite de {self.max_requests} requisições por {self.window_seconds}s excedido",
                    "retry_after": reset_in,
                },
                headers={"Retry-After": str(reset_in)},
            )
def add_rate_limit_headers(request: Request, response):
    """Adiciona headers de rate limit à resposta."""
    if hasattr(request.state, 'rate_limit_remaining'):
        response.headers["X-RateLimit-Limit"] = str(request.app.state.rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
        response.headers["X-RateLimit-Reset"] = str(request.state.rate_limit_reset)
    return response
