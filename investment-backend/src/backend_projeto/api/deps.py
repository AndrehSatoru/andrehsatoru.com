# api/deps.py
# Dependências reutilizáveis (Dependency Injection) para FastAPI

from ..core.data_handling import YFinanceProvider, DataLoader
from ..core.analysis import RiskEngine
from ..core.optimization import OptimizationEngine
from ..core.simulation import MonteCarloEngine
from ..utils.config import Config


def get_config() -> Config:
    """Retorna instância compartilhada de Config."""
    return Config()


def get_provider() -> YFinanceProvider:
    """Retorna YFinanceProvider com cache e configurações de resiliência."""
    config = get_config()
    return YFinanceProvider(
        cache_dir='src/backend_projeto/cache',
        max_retries=config.YFINANCE_MAX_RETRIES,
        backoff_factor=config.YFINANCE_BACKOFF_FACTOR,
        timeout=config.YFINANCE_TIMEOUT,
    )


def get_loader() -> DataLoader:
    """Factory: retorna DataLoader configurado."""
    provider = get_provider()
    config = get_config()
    return DataLoader(provider=provider, config=config)


def get_risk_engine() -> RiskEngine:
    """Factory: retorna RiskEngine com loader e config."""
    loader = get_loader()
    config = get_config()
    return RiskEngine(loader=loader, config=config)


def get_optimization_engine() -> OptimizationEngine:
    """Factory: retorna OptimizationEngine."""
    loader = get_loader()
    config = get_config()
    return OptimizationEngine(loader=loader, config=config)


def get_montecarlo_engine() -> MonteCarloEngine:
    """Factory: retorna MonteCarloEngine."""
    loader = get_loader()
    config = get_config()
    return MonteCarloEngine(loader=loader, config=config)
