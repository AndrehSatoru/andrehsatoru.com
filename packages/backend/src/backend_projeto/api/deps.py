# api/deps.py
# Dependências reutilizáveis (Dependency Injection) para FastAPI
from fastapi import Depends
from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.domain.analysis import RiskEngine
from backend_projeto.domain.optimization import OptimizationEngine
from backend_projeto.domain.simulation import MonteCarloEngine
from backend_projeto.infrastructure.utils.config import Settings, settings
from typing import List

def get_config() -> Settings:
    """
    Dependency that provides the application's configuration settings.

    Returns:
        Settings: An instance of the Settings class containing application configurations.
    """
    return settings

def get_loader(config: Settings = Depends(get_config)) -> YFinanceProvider:
    """
    Dependency that provides a configured data loader (YFinanceProvider) with fallback options.

    The data loader is initialized with the application's configuration and
    can include fallback providers like Finnhub or AlphaVantage if their
    API keys are available in the configuration.

    Args:
        config (Settings): The application's configuration settings.

    Returns:
        YFinanceProvider: An instance of YFinanceProvider configured with potential fallback data providers.
    """
    # Import providers locally to avoid circular dependencies
    from backend_projeto.infrastructure.data_handling import YFinanceProvider, DataProvider
    from backend_projeto.infrastructure.data_providers.finnhub_provider import FinnhubProvider
    from backend_projeto.infrastructure.data_providers.alpha_vantage_provider import AlphaVantageProvider

    # Setup fallback providers
    fallback_providers: List[DataProvider] = []
    if config.FINNHUB_API_KEY:
        fallback_providers.append(FinnhubProvider(config=config))
    if config.ALPHA_VANTAGE_API_KEY:
        fallback_providers.append(AlphaVantageProvider(config=config))
    
    return YFinanceProvider(config=config, fallback_providers=fallback_providers)

def get_risk_engine(loader: YFinanceProvider = Depends(get_loader), config: Settings = Depends(get_config)) -> RiskEngine:
    """
    Dependency that provides a configured RiskEngine instance.

    The RiskEngine is initialized with a data loader and application configuration.

    Args:
        loader (YFinanceProvider): The data loader dependency.
        config (Settings): The application's configuration settings.

    Returns:
        RiskEngine: An instance of the RiskEngine.
    """
    return RiskEngine(loader=loader, config=config)

def get_optimization_engine(loader: YFinanceProvider = Depends(get_loader), config: Settings = Depends(get_config)) -> OptimizationEngine:
    """
    Dependency that provides a configured OptimizationEngine instance.

    The OptimizationEngine is initialized with a data loader and application configuration.

    Args:
        loader (YFinanceProvider): The data loader dependency.
        config (Settings): The application's configuration settings.

    Returns:
        OptimizationEngine: An instance of the OptimizationEngine.
    """
    return OptimizationEngine(loader=loader, config=config)

def get_montecarlo_engine(loader: YFinanceProvider = Depends(get_loader), config: Settings = Depends(get_config)) -> MonteCarloEngine:
    """
    Dependency that provides a configured MonteCarloEngine instance.

    The MonteCarloEngine is initialized with a data loader and application configuration.

    Args:
        loader (YFinanceProvider): The data loader dependency.
        config (Settings): The application's configuration settings.

    Returns:
        MonteCarloEngine: An instance of the MonteCarloEngine.
    """
    return MonteCarloEngine(loader=loader, config=config)
