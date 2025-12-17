# config.py
# Classe Config com configurações centralizadas

import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Any # Import Optional and Any

class Settings(BaseSettings):
    """Manages application settings with Pydantic, supporting .env files."""
    
    # Model configuration
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Simulation
    CAPITAL_INICIAL: float = 100_000_000.0
    DATA_FINAL_SIMULACAO: str = "2025-10-01"
    SLIPPAGE_PERCENTUAL: float = 0.0005
    ARQUIVO_TRANSACOES: str = 'Carteira.xlsx'
    INPUT_DIR: str = 'inputs'
    OUTPUT_DIR: str = 'outputs'
    
    # Benchmark
    BENCHMARK_TICKER: str = '^BVSP'
    
    # Risk
    VAR_CONFIDENCE_LEVEL: float = 0.99
    CONSECUTIVE_NAN_THRESHOLD: int = 3
    
    # Monte Carlo
    MONTE_CARLO_SIMULATIONS: int = 100000
    MONTE_CARLO_DAYS: int = 252
    MONTE_CARLO_GBM_ANNUAL_DRIFT: float = 0.0
    
    # Models
    USE_GARCH_VOL: bool = True
    USE_BLACK_LITTERMAN: bool = True
    
    # Calendar
    DIAS_UTEIS_ANO: int = 252
    DIAS_CALENDARIO_ANO: float = 365.25

    # API
    MAX_ASSETS_PER_REQUEST: int = 100
    REQUEST_TIMEOUT_SECONDS: int = 300
    ENABLE_CACHE: bool = False
    CACHE_TTL_SECONDS: int = 3600
    CACHE_DIR: str = 'cache'
    GZIP_MINIMUM_SIZE: int = 1000

    # Logging
    LOG_LEVEL: str = 'INFO'
    LOG_FORMAT: str = 'text'

    # Rate Limiting
    # Rate limiting habilitado por padrão em produção ou se env var RATE_LIMIT_ENABLED for true
    RATE_LIMIT_ENABLED: bool = os.getenv("ENVIRONMENT") == "production" or os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    USE_REDIS_RATE_LIMITER: bool = False

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # External APIs - Timeouts and Retries
    YFINANCE_TIMEOUT: int = 30
    YFINANCE_MAX_RETRIES: int = 3
    YFINANCE_BACKOFF_FACTOR: float = 2.0

    # Data Provider settings
    DATA_PROVIDER_MAX_RETRIES: int = 3
    DATA_PROVIDER_BACKOFF_FACTOR: float = 2.0
    DATA_PROVIDER_TIMEOUT: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ['*']
    
    # Risk-free rate
    RISK_FREE_RATE: float = 0.0
    
    # Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API Keys
    FINNHUB_API_KEY: str
    ALPHA_VANTAGE_API_KEY: str

    @field_validator('MAX_ASSETS_PER_REQUEST', 'REQUEST_TIMEOUT_SECONDS', 'RATE_LIMIT_REQUESTS', 'RATE_LIMIT_WINDOW_SECONDS', 'YFINANCE_TIMEOUT', 'DATA_PROVIDER_TIMEOUT')
    def _validate_positive(cls, v):
        if v <= 0:
            raise ValueError("must be positive")
        return v

    @field_validator('VAR_CONFIDENCE_LEVEL')
    def _validate_confidence_level(cls, v):
        if not (0 < v < 1):
            raise ValueError("must be between 0 and 1")
        return v

    def to_dict(self) -> dict:
        """Returns public settings as a dictionary."""
        return {
            'DIAS_UTEIS_ANO': self.DIAS_UTEIS_ANO,
            'VAR_CONFIDENCE_LEVEL': self.VAR_CONFIDENCE_LEVEL,
            'CONSECUTIVE_NAN_THRESHOLD': self.CONSECUTIVE_NAN_THRESHOLD,
            'MAX_ASSETS_PER_REQUEST': self.MAX_ASSETS_PER_REQUEST,
            'CACHE_ENABLED': self.ENABLE_CACHE,
            'CACHE_TTL_SECONDS': self.CACHE_TTL_SECONDS,
        }

# Singleton instance of the settings
settings = Settings()
