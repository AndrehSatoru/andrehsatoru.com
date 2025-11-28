"""
Covariance and risk attribution module.

This module provides functions for:
- Covariance matrix estimation (Ledoit-Wolf shrinkage)
- Risk attribution analysis
- Incremental, Marginal, and Relative VaR calculations
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional

from backend_projeto.domain.risk_metrics import (
    var_parametric,
    var_historical,
    var_evt,
)


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


def covariance_ledoit_wolf(returns_df: pd.DataFrame) -> Dict:
    """
    Calculates the Ledoit-Wolf shrunk covariance matrix for asset returns.

    The Ledoit-Wolf estimator is a shrinkage estimator for the covariance matrix,
    which can be more robust than the sample covariance matrix, especially
    when the number of assets is large relative to the number of observations.

    Args:
        returns_df (pd.DataFrame): DataFrame of historical asset returns.

    Returns:
        Dict: A dictionary containing:
              - "cov" (List[List[float]]): The shrunk covariance matrix as a list of lists.
              - "shrinkage" (float): The shrinkage intensity applied by the Ledoit-Wolf estimator.
              - "columns" (List[str]): The list of asset columns in the covariance matrix.
    """
    try:
        from sklearn.covariance import LedoitWolf
    except ImportError:
        cov_matrix = returns_df.cov()
        return {
            "cov": cov_matrix.values.tolist(),
            "shrinkage": 0.0,
            "columns": returns_df.columns.tolist()
        }
    
    lw = LedoitWolf()
    lw.fit(returns_df.values)
    
    return {
        "cov": lw.covariance_.tolist(),
        "shrinkage": lw.shrinkage_,
        "columns": returns_df.columns.tolist()
    }


def risk_attribution(returns_df: pd.DataFrame, assets: List[str], weights: Optional[List[float]], method: str = 'std', ewma_lambda: float = 0.94) -> Dict:
    """
    Performs risk attribution for a portfolio, calculating each asset's contribution to total portfolio risk.

    Args:
        returns_df (pd.DataFrame): DataFrame of historical asset returns.
        assets (List[str]): List of asset tickers in the portfolio.
        weights (Optional[List[float]]): Weights of the assets in the portfolio. If None, equal weights are assumed.
        method (str): Method for VaR calculation if marginal VaR is to be computed ('std', 'ewma').
        ewma_lambda (float): Decay factor for the EWMA method.

    Returns:
        Dict: A dictionary containing:
              - "assets" (List[str]): List of asset tickers.
              - "weights" (List[float]): Normalized weights of the assets.
              - "portfolio_vol" (float): Total portfolio volatility.
              - "contribution_vol" (List[float]): Each asset's contribution to portfolio volatility.
              - "contribution_var" (List[float]): Each asset's contribution to portfolio VaR (if applicable).
    """
    if not all(asset in returns_df.columns for asset in assets):
        raise ValueError(f"Some assets not found in returns data: {assets}")
    
    asset_returns = returns_df[assets].dropna()
    
    if len(asset_returns) == 0:
        raise ValueError("No valid returns data found for attribution")
    
    if weights is None:
        weights = [1.0 / len(assets)] * len(assets)
    else:
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
    
    cov_matrix = covariance_ledoit_wolf(asset_returns)["cov"]
    portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
    
    contribution_vol = []
    for i, asset in enumerate(assets):
        marginal_vol = np.dot(cov_matrix[i], weights) / portfolio_vol
        contribution_vol.append(weights[i] * marginal_vol)
    
    contribution_var = []
    
    return {
        "assets": assets,
        "weights": weights,
        "portfolio_vol": float(portfolio_vol),
        "contribution_vol": [float(c) for c in contribution_vol],
        "contribution_var": contribution_var
    }


def incremental_var(
    returns_df: pd.DataFrame,
    assets: List[str],
    weights: Optional[List[float]],
    alpha: float = 0.99,
    method: str = 'historical',
    ewma_lambda: float = 0.94,
    delta: float = 0.01,
) -> Dict:
    """
    Incremental VaR (IVaR): impact on VaR when slightly increasing the weight of each asset.

    Args:
        returns_df: DataFrame with daily returns per asset.
        assets: List of tickers to consider.
        weights: Portfolio weights (None = equal-weighted).
        alpha: Confidence level (e.g., 0.99 for 99%).
        method: 'historical' | 'std' | 'ewma' | 'garch' | 'evt'.
        ewma_lambda: Decay parameter for EWMA.
        delta: Increment applied to weight (default 0.01 = 1%).

    Returns:
        Dict with 'alpha', 'method', 'delta', 'base_var', 'base_weights', 'ivar', 'assets'.
    """
    sel = [a for a in assets if a in returns_df.columns]
    if not sel:
        raise ValueError("Nenhum ativo válido em returns_df")
    base_w = _as_weights(sel, weights)
    X = returns_df[sel].dropna(how='all').fillna(0.0)
    port_base = pd.Series(X.values @ base_w, index=X.index)
    
    if method == 'historical':
        base_var, _ = var_historical(port_base, alpha)
    elif method in ('std', 'ewma', 'garch'):
        base_var, _ = var_parametric(port_base, alpha, method=method, ewma_lambda=ewma_lambda)
    elif method == 'evt':
        base_var, _ = var_evt(port_base, alpha)
    else:
        raise ValueError("método inválido para IVaR")

    ivar: Dict[str, float] = {}
    for i, a in enumerate(sel):
        w = base_w.copy()
        w[i] = max(w[i] + delta, 0.0)
        w = w / w.sum()
        port_new = pd.Series(X.values @ w, index=X.index)
        if method == 'historical':
            v, _ = var_historical(port_new, alpha)
        elif method in ('std', 'ewma', 'garch'):
            v, _ = var_parametric(port_new, alpha, method=method, ewma_lambda=ewma_lambda)
        else:
            v, _ = var_evt(port_new, alpha)
        ivar[a] = float(v - base_var)
    
    return {
        "alpha": alpha,
        "method": method,
        "delta": float(delta),
        "base_var": float(base_var),
        "base_weights": base_w.tolist(),
        "ivar": ivar,
        "assets": sel,
    }


def marginal_var(
    returns_df: pd.DataFrame,
    assets: List[str],
    weights: Optional[List[float]],
    alpha: float = 0.99,
    method: str = 'historical',
    ewma_lambda: float = 0.94,
) -> Dict:
    """
    Marginal VaR (MVaR): impact on VaR when completely removing each asset from the portfolio.

    Args:
        returns_df: DataFrame with daily returns per asset.
        assets: List of tickers.
        weights: Portfolio weights (None = equal-weighted).
        alpha: Confidence level.
        method: 'historical' | 'std' | 'ewma' | 'garch' | 'evt'.
        ewma_lambda: EWMA parameter.

    Returns:
        Dict with 'alpha', 'method', 'base_var', 'base_weights', 'mvar', 'assets'.
    """
    sel = [a for a in assets if a in returns_df.columns]
    if not sel:
        raise ValueError("Nenhum ativo válido em returns_df")
    base_w = _as_weights(sel, weights)
    X = returns_df[sel].dropna(how='all').fillna(0.0)
    port_base = pd.Series(X.values @ base_w, index=X.index)
    
    if method == 'historical':
        base_var, _ = var_historical(port_base, alpha)
    elif method in ('std', 'ewma', 'garch'):
        base_var, _ = var_parametric(port_base, alpha, method=method, ewma_lambda=ewma_lambda)
    elif method == 'evt':
        base_var, _ = var_evt(port_base, alpha)
    else:
        raise ValueError("método inválido para MVaR")

    mvar: Dict[str, float] = {}
    for i, a in enumerate(sel):
        keep_idx = [j for j in range(len(sel)) if j != i]
        if not keep_idx:
            mvar[a] = float('nan')
            continue
        w = base_w[keep_idx]
        w = w / w.sum()
        Xsub = X.iloc[:, keep_idx]
        port_new = pd.Series(Xsub.values @ w, index=Xsub.index)
        if method == 'historical':
            v, _ = var_historical(port_new, alpha)
        elif method in ('std', 'ewma', 'garch'):
            v, _ = var_parametric(port_new, alpha, method=method, ewma_lambda=ewma_lambda)
        else:
            v, _ = var_evt(port_new, alpha)
        mvar[a] = float(v - base_var)
    
    return {
        "alpha": alpha,
        "method": method,
        "base_var": float(base_var),
        "base_weights": base_w.tolist(),
        "mvar": mvar,
        "assets": sel,
    }


def relative_var(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    alpha: float = 0.99,
    method: str = 'historical',
    ewma_lambda: float = 0.94,
) -> Dict:
    """
    Relative VaR: VaR of portfolio underperformance relative to a benchmark.

    Args:
        portfolio_returns: Time series of portfolio returns.
        benchmark_returns: Time series of benchmark returns.
        alpha: Confidence level.
        method: 'historical' | 'std' | 'ewma' | 'garch' | 'evt'.
        ewma_lambda: EWMA parameter.

    Returns:
        Dict with 'relative_var', 'alpha', 'method', 'details'.
    """
    rP, rB = portfolio_returns.align(benchmark_returns, join='inner')
    rel = (rP - rB).dropna()
    if rel.empty:
        raise ValueError("Séries sem interseção para VaR relativo")
    
    if method == 'historical':
        v, d = var_historical(rel, alpha)
    elif method in ('std', 'ewma', 'garch'):
        v, d = var_parametric(rel, alpha, method=method, ewma_lambda=ewma_lambda)
    elif method == 'evt':
        v, d = var_evt(rel, alpha)
    else:
        raise ValueError("método inválido para VaR relativo")
    
    return {"relative_var": float(v), "alpha": alpha, "method": method, "details": d}
