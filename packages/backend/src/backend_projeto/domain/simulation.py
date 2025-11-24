"""
This module provides functionalities for financial simulations, particularly Monte Carlo simulations.

It includes the `MonteCarloEngine` for simulating asset price paths using Geometric Brownian Motion (GBM)
and estimating risk metrics like VaR and ES from these simulations.
It also contains a `PortfolioSimulator` class, which appears to be an older or incomplete
version of a transaction-based simulator, potentially superseded by `portfolio_simulation.py`.
"""
# simulation.py

import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.infrastructure.utils.config import Settings, settings

try:
    from arch import arch_model
except Exception:
    arch_model = None


def _ewma_vol(returns: np.ndarray, lam: float = 0.94) -> float:
    """
    Calculates Exponentially Weighted Moving Average (EWMA) volatility.

    Args:
        returns (np.ndarray): Array of asset returns.
        lam (float): Decay factor for EWMA. Defaults to 0.94.

    Returns:
        float: The EWMA volatility.
    """


@dataclass
class MonteCarloEngine:
    """Orquestra as simulações de Monte Carlo para análise de risco."""
    loader: YFinanceProvider
    config: Settings

    def _portfolio_returns(self, prices: pd.DataFrame, assets: List[str], weights: Optional[List[float]]) -> pd.Series:
        """
        Calculates the returns of a portfolio from asset prices and weights.

        Args:
            prices (pd.DataFrame): DataFrame of asset prices.
            assets (List[str]): List of asset tickers in the portfolio.
            weights (Optional[List[float]]): Weights of the assets in the portfolio.

        Returns:
            pd.Series: A Series containing the portfolio returns.
        """
        returns = prices[assets].pct_change().dropna()
        if weights is None:
            weights = [1/len(assets)] * len(assets)
        return (returns * weights).sum(axis=1)

    def _estimate_params(self, r: pd.Series, vol_method: str = 'std', ewma_lambda: float = 0.94) -> Dict:
        """
        Estimates the mean (mu) and volatility (sigma) parameters from a series of returns.

        Args:
            r (pd.Series): Series of asset returns.
            vol_method (str): Method to estimate volatility ('std', 'ewma', 'garch'). Defaults to 'std'.
            ewma_lambda (float): Decay factor for EWMA volatility. Defaults to 0.94.

        Returns:
            Dict: A dictionary containing the estimated mean ("mu") and volatility ("sigma").

        Raises:
            RuntimeError: If 'arch' package is not available for 'garch' method.
            ValueError: If an invalid volatility method is specified.
        """
        mu = r.mean()
        if vol_method == 'std':
            sigma = r.std()
        elif vol_method == 'ewma':
            sigma = r.ewm(alpha=ewma_lambda).std().iloc[-1]
        elif vol_method == 'garch':
            if arch_model is None:
                raise RuntimeError("Pacote 'arch' não disponível para método garch")
            am = arch_model(r * 100, vol='GARCH', p=1, q=1, dist='normal')
            res = am.fit(disp='off')
            sigma = res.conditional_volatility.iloc[-1] / 100.0
        else:
            raise ValueError(f"Método de volatilidade desconhecido: {vol_method}")
        return {'mu': mu, 'sigma': sigma}

    def simulate_gbm(self, assets: List[str], start_date: str, end_date: str, weights: Optional[List[float]], n_paths: int, n_days: int, vol_method: str = 'std', ewma_lambda: float = 0.94, seed: Optional[int] = None) -> Dict:
        """
        Simulates price trajectories using Geometric Brownian Motion (GBM).

        This method fetches historical data, estimates mean and volatility, and then
        generates multiple future price paths for a portfolio using GBM.
        It can also calculate VaR and ES from these simulations.

        Args:
            assets (List[str]): List of asset tickers.
            start_date (str): Start date for historical data to estimate parameters.
            end_date (str): End date for historical data to estimate parameters.
            weights (Optional[List[float]]): Portfolio weights. If None, equal weights are assumed.
            n_paths (int): Number of simulation paths (trajectories).
            n_days (int): Number of days to simulate into the future.
            vol_method (str): Method to estimate volatility ('std', 'ewma', 'garch'). Defaults to 'std'.
            ewma_lambda (float): Decay factor for EWMA volatility. Defaults to 0.94.
            seed (Optional[int]): Seed for the random number generator for reproducibility.

        Returns:
            Dict: A dictionary containing simulation results, typically including:
                  - 'paths' (np.ndarray): Simulated price paths.
                  - 'var' (float): Value at Risk from simulations.
                  - 'es' (float): Expected Shortfall from simulations.
                  - 'details' (Dict): Additional simulation details.
        """


class PortfolioSimulator:
    """
    (Potentially Deprecated/Incomplete) Class for simulating portfolio operations based on transactions.

    This class appears to be an older or incomplete implementation of a transaction-based
    portfolio simulator, possibly superseded by `portfolio_simulation.py`.
    It initializes with transaction data and configuration, setting up parameters
    for capital, slippage, and data loading.
    """
    def __init__(self, transactions_df: pd.DataFrame, data_loader: YFinanceProvider, config: Settings):
        """
        Initializes the PortfolioSimulator with transaction data and configuration.

        Args:
            transactions_df (pd.DataFrame): DataFrame containing transaction history.
            data_loader (YFinanceProvider): An instance of a data provider to fetch market data.
            config (Settings): Configuration object for the simulation parameters.
        """
        self.transactions = transactions_df.set_index('Data')
        self.start_date = self.transactions.index.min()
        self.end_date = pd.to_datetime(config.DATA_FINAL_SIMULACAO)
        self.assets = self.transactions['Ativo'].dropna().unique().tolist()
        self.data_loader = data_loader

        self.config = config
        self.initial_capital = config.CAPITAL_INICIAL
        self.slippage_percentual = config.SLIPPAGE_PERCENTUAL
        self.portfolio_history = pd.DataFrame()
        self.quotes_history = pd.DataFrame()
        self.cdi_data = pd.DataFrame()
        self.pending_settlements: Dict[pd.Timestamp, float] = {}
        logging.info(f"PortfolioSimulator inicializado com slippage de {self.slippage_percentual:.4%}.")

    # Pontos de extensão futuros para simulação de carteira baseadas em transações
