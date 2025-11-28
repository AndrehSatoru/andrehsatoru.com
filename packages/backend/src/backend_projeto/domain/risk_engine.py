"""
Risk Engine module - Orchestrates risk analysis computations.

This module provides the RiskEngine class which serves as a facade
for various risk calculations including VaR, ES, drawdown, stress testing, etc.
"""
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass

from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.infrastructure.utils.config import Settings, settings
from backend_projeto.domain.risk_metrics import (
    var_parametric,
    var_historical,
    es_parametric,
    es_historical,
    drawdown,
)
from backend_projeto.domain.stress_testing import stress_test, backtest_var
from backend_projeto.domain.covariance import covariance_ledoit_wolf, risk_attribution


def compute_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """Calcula os retornos diários percentuais a partir de um DataFrame de preços."""
    import numpy as np
    r = price_df.sort_index().pct_change().dropna(how='all')
    return r.replace([np.inf, -np.inf], np.nan).dropna(how='all')


def portfolio_returns(returns_df: pd.DataFrame, assets: List[str], weights: Optional[List[float]]) -> pd.Series:
    """Calcula os retornos de um portfólio a partir dos retornos de ativos individuais e seus pesos."""
    import numpy as np
    
    def _as_weights(assets: List[str], weights: Optional[List[float]]) -> np.ndarray:
        if not weights:
            return np.ones(len(assets)) / len(assets)
        w = np.array(weights, dtype=float)
        if len(w) != len(assets):
            raise ValueError("Tamanho de weights difere do número de assets")
        s = w.sum()
        if s == 0:
            raise ValueError("Soma dos pesos não pode ser zero")
        return w / s
    
    sel = [a for a in assets if a in returns_df.columns]
    if not sel:
        raise ValueError("Nenhum ativo encontrado em returns_df")
    w = _as_weights(sel, weights if weights and len(weights) == len(assets) else None)
    X = returns_df[sel].copy()
    w_series = pd.Series(w, index=sel)
    mask = X.notna()
    w_masked = mask.mul(w_series, axis=1)
    row_sum = w_masked.sum(axis=1).replace(0.0, np.nan)
    w_norm = w_masked.div(row_sum, axis=0).fillna(0.0)
    port = (X.fillna(0.0) * w_norm).sum(axis=1)
    port.name = 'portfolio'
    return port


@dataclass
class RiskEngine:
    """Orchestrates risk analysis, calculating metrics like VaR, ES, drawdown, etc."""
    loader: YFinanceProvider
    config: Settings
    
    def _load_prices(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Loads historical prices for a list of assets."""
        df = self.loader.fetch_stock_prices(assets, start_date, end_date)
        return df

    def _portfolio_series(self, df_prices: pd.DataFrame, assets: List[str], weights: Optional[List[float]]) -> pd.Series:
        """Calculates portfolio returns series."""
        rets = compute_returns(df_prices)
        return portfolio_returns(rets, assets, weights)

    def compute_var(self, assets: List[str], start_date: str, end_date: str, alpha: float, method: str, ewma_lambda: float, weights: Optional[List[float]]) -> Dict:
        """Calculates Value at Risk (VaR) for the portfolio."""
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        if method == 'historical':
            value, details = var_historical(r, alpha)
        else:
            value, details = var_parametric(r, alpha, method=method, ewma_lambda=ewma_lambda)
        return {"var": value, "alpha": alpha, "method": method, "details": details}

    def compute_es(self, assets: List[str], start_date: str, end_date: str, alpha: float, method: str, ewma_lambda: float, weights: Optional[List[float]]) -> Dict:
        """Calculates Expected Shortfall (ES) for the portfolio."""
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        if method == 'historical':
            value, details = es_historical(r, alpha)
        else:
            value, details = es_parametric(r, alpha, method=method, ewma_lambda=ewma_lambda)
        return {"es": value, "alpha": alpha, "method": method, "details": details}

    def compute_drawdown(self, assets: List[str], start_date: str, end_date: str, weights: Optional[List[float]]) -> Dict:
        """Calculates maximum drawdown of the portfolio."""
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        return drawdown(r)

    def compute_stress(self, assets: List[str], start_date: str, end_date: str, weights: Optional[List[float]], shock_pct: float) -> Dict:
        """Performs a stress test by applying a shock to returns."""
        prices = self._load_prices(assets, start_date, end_date)
        rets = compute_returns(prices)
        return stress_test(rets, assets, weights, shocks_pct=shock_pct)

    def backtest(self, assets: List[str], start_date: str, end_date: str, alpha: float, method: str, ewma_lambda: float, weights: Optional[List[float]]) -> Dict:
        """Performs VaR backtesting to evaluate model accuracy."""
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        return backtest_var(r, alpha=alpha, method=method, ewma_lambda=ewma_lambda)

    def compute_covariance(self, assets: List[str], start_date: str, end_date: str) -> Dict:
        """Calculates the covariance matrix of asset returns."""
        prices = self._load_prices(assets, start_date, end_date)
        rets = compute_returns(prices)
        return covariance_ledoit_wolf(rets[assets])

    def compute_attribution(self, assets: List[str], start_date: str, end_date: str, weights: Optional[List[float]], method: str, ewma_lambda: float) -> Dict:
        """Performs risk attribution for the portfolio."""
        prices = self._load_prices(assets, start_date, end_date)
        rets = compute_returns(prices)
        return risk_attribution(rets, assets, weights, method=method, ewma_lambda=ewma_lambda)

    def compare_methods(self, assets: List[str], start_date: str, end_date: str, alpha: float, methods: List[str], ewma_lambda: float, weights: Optional[List[float]]) -> Dict:
        """Compares different VaR and ES calculation methods."""
        comparison = {}
        for method in methods:
            var_result = self.compute_var(assets, start_date, end_date, alpha, method, ewma_lambda, weights)
            es_result = self.compute_es(assets, start_date, end_date, alpha, method, ewma_lambda, weights)
            comparison[method] = {
                "var": var_result.get("var"),
                "es": es_result.get("es"),
                "var_details": var_result.get("details"),
                "es_details": es_result.get("details"),
            }
        return {"comparison": comparison}
