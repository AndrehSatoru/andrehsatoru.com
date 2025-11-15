"""
This module provides functionalities for portfolio optimization and factor model analysis.

It includes the `OptimizationEngine` class which orchestrates:
- Markowitz portfolio optimization (maximizing Sharpe ratio, minimizing variance).
- Capital Asset Pricing Model (CAPM) metrics calculation.
- Arbitrage Pricing Theory (APT) metrics calculation.
- Black-Litterman model implementation for adjusting expected returns.
"""
# optimization.py

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
from backend_projeto.utils.config import Settings, settings
from backend_projeto.core.data_handling import YFinanceProvider
from numpy.linalg import lstsq
from scipy.optimize import minimize


from backend_projeto.core.utils import _returns_from_prices, _annualize_mean_cov

@dataclass
class OptimizationEngine:
    """Orquestra as otimizações de portfólio e análises de modelos de fatores."""
    loader: YFinanceProvider
    config: Settings

    def load_prices(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Carrega os preços históricos para uma lista de ativos."""
        return self.loader.fetch_stock_prices(assets, start_date, end_date)

    def optimize_markowitz(self, assets: List[str], start_date: str, end_date: str, objective: str = 'max_sharpe', bounds: Optional[List[Tuple[float,float]]] = None, long_only: bool = True, max_weight: Optional[float] = None, risk_free_rate: Optional[float] = None) -> Dict:
        """
        Optimizes a portfolio using the Markowitz model for a specific objective.

        This function calculates the optimal asset weights based on historical returns
        and a chosen objective (e.g., maximize Sharpe ratio, minimize variance).

        Args:
            assets (List[str]): List of asset tickers.
            start_date (str): Start date for historical data.
            end_date (str): End date for historical data.
            objective (str): Optimization objective ('max_sharpe', 'min_var', 'max_return').
                             Defaults to 'max_sharpe'.
            bounds (Optional[List[Tuple[float,float]]]): Weight bounds for each asset.
                                                          If None, default bounds are applied.
            long_only (bool): If True, restricts weights to be non-negative (no short selling).
                              Defaults to True.
            max_weight (Optional[float]): Maximum weight allowed for any single asset.
                                          If None, no upper limit other than 1.0.
            risk_free_rate (Optional[float]): The risk-free rate to use for Sharpe ratio calculation.
                                              If None, uses the configured risk-free rate.

        Returns:
            Dict: A dictionary containing the optimal weights and portfolio statistics:
                  - 'weights' (Dict[str, float]): Optimal weight for each asset.
                  - 'ret_annual' (float): Annualized expected return of the optimal portfolio.
                  - 'vol_annual' (float): Annualized volatility of the optimal portfolio.
                  - 'sharpe' (float): Sharpe ratio of the optimal portfolio.
                  - 'risk_free_rate' (float): The risk-free rate used in the calculation.
                  - 'objective' (str): The optimization objective used.
                  - 'success' (bool): True if optimization was successful, False otherwise.
                  - 'message' (str): Message from the optimization solver.
        """
        prices = self.load_prices(assets, start_date, end_date)
        rets = _returns_from_prices(prices)[assets].dropna()
        if rets.shape[1] < 2:
            raise ValueError("São necessários pelo menos 2 ativos para otimização")
        mu, cov = _annualize_mean_cov(rets, self.config.DIAS_UTEIS_ANO)
        n = len(assets)
        if bounds is None:
            if long_only:
                lower = 0.0
            else:
                lower = -1.0
            upper = 1.0 if max_weight is None else max_weight
            bounds = [(lower, upper) for _ in range(n)]
        # Use provided risk-free rate or fall back to config value
        rf = risk_free_rate if risk_free_rate is not None else self.config.RISK_FREE_RATE

        def portfolio_stats(w):
            w = np.array(w)
            ret = w @ mu
            vol = float(np.sqrt(max(w @ cov @ w, 0)))
            sharpe = (ret - rf) / (vol + 1e-12)
            return ret, vol, sharpe

        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},)
        x0 = np.ones(n) / n

        if objective == 'min_var':
            fun = lambda w: w @ cov @ w
        elif objective == 'max_return':
            fun = lambda w: -(w @ mu)
        else:  # max_sharpe
            fun = lambda w: -((w @ mu - rf) / (np.sqrt(max(w @ cov @ w, 0)) + 1e-12))

        res = minimize(fun, x0, bounds=bounds, constraints=cons, method='SLSQP', options={'maxiter': 100})
        w_opt = res.x
        ret, vol, sharpe = portfolio_stats(w_opt)
        return {
            'weights': {assets[i]: float(w_opt[i]) for i in range(n)},
            'ret_annual': float(ret),
            'vol_annual': float(vol),
            'sharpe': float(sharpe),
            'risk_free_rate': float(rf),  # Include the used risk-free rate in the response
            'objective': objective,
            'success': bool(res.success),
            'message': res.message,
        }

    def capm_metrics(self, assets: List[str], start_date: str, end_date: str, benchmark_ticker: str) -> Dict:
        """
        Calculates Capital Asset Pricing Model (CAPM) metrics (alpha, beta, R-squared)
        for a list of assets relative to a specified benchmark.

        Args:
            assets (List[str]): List of asset tickers.
            start_date (str): Start date for historical data.
            end_date (str): End date for historical data.
            benchmark_ticker (str): Ticker of the benchmark (e.g., '^BVSP', '^GSPC').

        Returns:
            Dict: A dictionary containing the benchmark ticker and a dictionary of metrics
                  (alpha, beta, R-squared) for each asset.

        Raises:
            ValueError: If benchmark data cannot be fetched.
        """
        prices = self.load_prices(assets, start_date, end_date)
        bench_series = self.loader.fetch_benchmark_data(benchmark_ticker, start_date, end_date)
        if bench_series is None:
            raise ValueError("Benchmark sem dados")
        df = prices.join(bench_series.rename('BENCH'), how='inner')
        rets = _returns_from_prices(df)
        results = {}
        rb = rets['BENCH'].values.reshape(-1, 1)
        X = np.column_stack([np.ones(rb.shape[0]), rb])
        for a in assets:
            if a not in rets.columns:
                continue
            y = rets[a].values
            beta_params, *_ = lstsq(X, y, rcond=None)
            alpha, beta = beta_params[0], beta_params[1]
            # estatísticas simples
            y_hat = X @ beta_params
            resid = y - y_hat
            ss_res = float(np.sum(resid**2))
            ss_tot = float(np.sum((y - np.mean(y))**2))
            r2 = 0.0 if ss_tot == 0 else 1 - ss_res/ss_tot
            results[a] = {'alpha': float(alpha), 'beta': float(beta), 'r2': float(r2)}
        return {'benchmark': benchmark_ticker, 'metrics': results}

    def apt_metrics(self, assets: List[str], start_date: str, end_date: str, factors: List[str]) -> Dict:
        """
        Calculates Arbitrage Pricing Theory (APT) metrics using multifactor regression.

        This function estimates the sensitivity (betas) of asset returns to various
        economic factors, along with the asset's alpha and R-squared.

        Args:
            assets (List[str]): List of asset tickers.
            start_date (str): Start date for historical data.
            end_date (str): End date for historical data.
            factors (List[str]): List of tickers for the risk factors.

        Returns:
            Dict: A dictionary containing the metrics for each asset, including alpha,
                  betas for each factor, the list of factors used, and R-squared.
        """
        prices_assets = self.load_prices(assets, start_date, end_date)
        prices_factors = self.load_prices(factors, start_date, end_date)
        df = prices_assets.join(prices_factors, how='inner', lsuffix='', rsuffix='_F')
        rets = _returns_from_prices(df)
        # separa colunas
        factor_cols = [c for c in rets.columns if c in factors]
        X = rets[factor_cols].values
        X = np.column_stack([np.ones(X.shape[0]), X])
        results = {}
        for a in assets:
            if a not in rets.columns:
                continue
            y = rets[a].values
            coeffs, *_ = lstsq(X, y, rcond=None)
            alpha = coeffs[0]
            betas = coeffs[1:].tolist()
            y_hat = X @ coeffs
            resid = y - y_hat
            ss_res = float(np.sum(resid**2))
            ss_tot = float(np.sum((y - np.mean(y))**2))
            r2 = 0.0 if ss_tot == 0 else 1 - ss_res/ss_tot
            results[a] = {'alpha': float(alpha), 'betas': betas, 'factors': factor_cols, 'r2': float(r2)}
        return {'metrics': results}

    def black_litterman(self, assets: List[str], start_date: str, end_date: str, market_caps: Dict[str, float], views: List[Dict], tau: float = 0.05) -> Dict:
        """
        Implements the Black-Litterman model to adjust expected returns based on investor views.

        The Black-Litterman model combines a market-implied equilibrium return with
        an investor's subjective views about asset returns to produce a new set
        of expected returns, which are then used in portfolio optimization.

        Args:
            assets (List[str]): List of asset tickers.
            start_date (str): Start date for historical data.
            end_date (str): End date for historical data.
            market_caps (Dict[str, float]): Dictionary with market capitalizations for each asset.
            views (List[Dict]): List of investor views. Each view is a dictionary
                                specifying the assets involved, the view's return, and confidence.
            tau (float): Uncertainty parameter of the model. Defaults to 0.05.

        Returns:
            Dict: A dictionary containing the adjusted portfolio weights and expected returns.
        """
