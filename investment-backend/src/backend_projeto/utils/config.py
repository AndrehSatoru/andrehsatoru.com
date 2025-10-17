# config.py
# Classe Config com configurações centralizadas

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Config:
    """Agrupa todas as configurações e parâmetros da aplicação.
    
    Configurações podem ser sobrescritas via variáveis de ambiente.
    """
    # Simulação
    CAPITAL_INICIAL: float = 100_000_000.0
    DATA_FINAL_SIMULACAO: str = "2025-10-01"
    SLIPPAGE_PERCENTUAL: float = 0.0005
    ARQUIVO_TRANSACOES: str = 'Carteira.xlsx'
    INPUT_DIR: str = 'inputs'
    OUTPUT_DIR: str = 'outputs'
    
    # Benchmark
    BENCHMARK_TICKER: str = '^BVSP'
    
    # Risco
    VAR_CONFIDENCE_LEVEL: float = 0.99
    CONSECUTIVE_NAN_THRESHOLD: int = 3
    
    # Monte Carlo
    MONTE_CARLO_SIMULATIONS: int = 100000
    MONTE_CARLO_DAYS: int = 252
    MONTE_CARLO_GBM_ANNUAL_DRIFT: float = 0.0
    
    # Modelos
    USE_GARCH_VOL: bool = True
    USE_BLACK_LITTERMAN: bool = True
    
    # Calendário
    DIAS_UTEIS_ANO: int = 252
    DIAS_CALENDARIO_ANO: float = 365.25
    
    # API
    MAX_ASSETS_PER_REQUEST: int = int(os.getenv('MAX_ASSETS_PER_REQUEST', '100'))
    REQUEST_TIMEOUT_SECONDS: int = int(os.getenv('REQUEST_TIMEOUT_SECONDS', '300'))
    ENABLE_CACHE: bool = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'
    CACHE_TTL_SECONDS: int = int(os.getenv('CACHE_TTL_SECONDS', '3600'))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = os.getenv('LOG_FORMAT', 'text')  # 'text' ou 'json'
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv('RATE_LIMIT_ENABLED', 'false').lower() == 'true'
    RATE_LIMIT_REQUESTS: int = int(os.getenv('RATE_LIMIT_REQUESTS', '100'))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv('RATE_LIMIT_WINDOW_SECONDS', '60'))
    
    # External APIs
    YFINANCE_TIMEOUT: int = int(os.getenv('YFINANCE_TIMEOUT', '30'))
    YFINANCE_MAX_RETRIES: int = int(os.getenv('YFINANCE_MAX_RETRIES', '3'))
    YFINANCE_BACKOFF_FACTOR: float = float(os.getenv('YFINANCE_BACKOFF_FACTOR', '2.0'))

    # CORS
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '')
    
    def __post_init__(self):
        """Validações após inicialização."""
        if self.MAX_ASSETS_PER_REQUEST < 1:
            raise ValueError("MAX_ASSETS_PER_REQUEST deve ser >= 1")
        if self.VAR_CONFIDENCE_LEVEL <= 0 or self.VAR_CONFIDENCE_LEVEL >= 1:
            raise ValueError("VAR_CONFIDENCE_LEVEL deve estar entre 0 e 1")
        if self.DIAS_UTEIS_ANO <= 0:
            raise ValueError("DIAS_UTEIS_ANO deve ser > 0")
    
    def to_dict(self) -> dict:
        """Retorna configurações como dicionário (para expor via API)."""
        return {
            'DIAS_UTEIS_ANO': self.DIAS_UTEIS_ANO,
            'VAR_CONFIDENCE_LEVEL': self.VAR_CONFIDENCE_LEVEL,
            'CONSECUTIVE_NAN_THRESHOLD': self.CONSECUTIVE_NAN_THRESHOLD,
            'MAX_ASSETS_PER_REQUEST': self.MAX_ASSETS_PER_REQUEST,
            'CACHE_ENABLED': self.ENABLE_CACHE,
            'CACHE_TTL_SECONDS': self.CACHE_TTL_SECONDS,
        }
