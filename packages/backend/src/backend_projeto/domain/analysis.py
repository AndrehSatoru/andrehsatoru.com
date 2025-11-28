"""
Financial analysis module - Main entry point for analysis functionality.

This module serves as the main entry point and re-exports all analysis functions
from their respective submodules for backward compatibility.

Submodules:
- risk_metrics: VaR, ES, drawdown calculations
- stress_testing: Stress tests and VaR backtesting
- covariance: Covariance matrix and risk attribution
- fama_french: Fama-French factor model metrics
- risk_engine: RiskEngine class for orchestrating risk analysis
- portfolio_analyzer: PortfolioAnalyzer class (defined in this file)
"""
import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# Re-export from risk_metrics
from backend_projeto.domain.risk_metrics import (
    var_parametric,
    es_parametric,
    var_historical,
    es_historical,
    var_evt,
    es_evt,
    drawdown,
)

# Re-export from stress_testing
from backend_projeto.domain.stress_testing import (
    stress_test,
    backtest_var,
)

# Re-export from covariance
from backend_projeto.domain.covariance import (
    covariance_ledoit_wolf,
    risk_attribution,
    incremental_var,
    marginal_var,
    relative_var,
)

# Re-export from fama_french
from backend_projeto.domain.fama_french import (
    ff3_metrics,
    ff5_metrics,
    _monthly_returns_from_prices,
)

# Re-export RiskEngine
from backend_projeto.domain.risk_engine import RiskEngine

# Import financial_math utilities
from backend_projeto.domain.financial_math import _returns_from_prices, _annualize_mean_cov


def _as_weights(assets: List[str], weights: Optional[List[float]]) -> np.ndarray:
    """Normalizes weights for assets."""
    if not weights:
        return np.ones(len(assets)) / len(assets)
    w = np.array(weights, dtype=float)
    if len(w) != len(assets):
        raise ValueError("Tamanho de weights difere do número de assets")
    s = w.sum()
    if s == 0:
        raise ValueError("Soma dos pesos não pode ser zero")
    return w / s


def compute_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    """Calcula os retornos diários percentuais a partir de um DataFrame de preços."""
    r = price_df.sort_index().pct_change().dropna(how='all')
    return r.replace([np.inf, -np.inf], np.nan).dropna(how='all')


def portfolio_returns(returns_df: pd.DataFrame, assets: List[str], weights: Optional[List[float]]) -> pd.Series:
    """Calcula os retornos de um portfólio a partir dos retornos de ativos individuais e seus pesos."""
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


def calculate_rolling_beta(asset_returns: pd.Series, benchmark_returns: pd.Series, window: int = 60) -> pd.Series:
    """Calculates the rolling beta of an asset's returns against a benchmark's returns."""
    asset_returns, benchmark_returns = asset_returns.align(benchmark_returns, join='inner')
    rolling_cov = asset_returns.rolling(window=window).cov(benchmark_returns)
    rolling_var = benchmark_returns.rolling(window=window).var()
    rolling_beta = rolling_cov / rolling_var
    return rolling_beta.dropna()


# Import PortfolioAnalyzer from the dedicated module
from backend_projeto.domain.portfolio_analyzer import PortfolioAnalyzer


# Define exports
__all__ = [
    # Utility functions
    "_as_weights",
    "compute_returns",
    "portfolio_returns",
    "calculate_rolling_beta",
    
    # Risk metrics
    "var_parametric",
    "es_parametric",
    "var_historical",
    "es_historical",
    "var_evt",
    "es_evt",
    "drawdown",
    
    # Stress testing
    "stress_test",
    "backtest_var",
    
    # Covariance and attribution
    "covariance_ledoit_wolf",
    "risk_attribution",
    "incremental_var",
    "marginal_var",
    "relative_var",
    
    # Fama-French
    "ff3_metrics",
    "ff5_metrics",
    "_monthly_returns_from_prices",
    
    # Classes
    "RiskEngine",
    "PortfolioAnalyzer",
]
