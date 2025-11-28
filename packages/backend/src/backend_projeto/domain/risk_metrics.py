"""
Risk metrics module for calculating VaR, ES, drawdown, and related risk measures.

This module provides various methods for calculating:
- Value at Risk (VaR): Parametric, Historical, EVT
- Expected Shortfall (ES): Parametric, Historical, EVT  
- Drawdown analysis
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple
from scipy.stats import norm

try:
    from arch import arch_model
except Exception:
    arch_model = None


def var_parametric(returns: pd.Series, alpha: float = 0.99, method: str = 'std', ewma_lambda: float = 0.94) -> Tuple[float, Dict]:
    """
    Calculates Parametric Value at Risk (VaR) assuming a normal distribution (or conditional GARCH).

    IMPORTANT: Assumes normality of returns. For distributions with heavy tails,
    consider using the EVT method.

    Methods:
        - 'std': Historical volatility (sample standard deviation).
        - 'ewma': EWMA (Exponentially Weighted Moving Average) volatility.
        - 'garch': Conditional volatility via GARCH(1,1).

    Args:
        returns (pd.Series): Series of asset returns.
        alpha (float): Confidence level (e.g., 0.99 for 99% VaR).
        method (str): Calculation method: 'std', 'ewma', or 'garch'.
        ewma_lambda (float): EWMA decay factor (default 0.94, RiskMetrics uses 0.94).

    Returns:
        Tuple[float, Dict]: A tuple containing the VaR value and a dictionary of details
                            (e.g., {'mu', 'sigma', 'z', 'method', 'ewma_lambda'}).

    Raises:
        RuntimeError: If 'arch' package is not available for 'garch' method.
        ValueError: If an invalid method is specified.
    """
    mu = float(returns.mean())
    if method == 'std':
        sigma = float(returns.std(ddof=1))
    elif method == 'ewma':
        lam = ewma_lambda
        x = returns.fillna(0.0).values
        var = np.var(x) if len(x) > 1 else 0.0
        for xi in x:
            var = lam * var + (1 - lam) * (xi ** 2)
        sigma = float(np.sqrt(var))
    elif method == 'garch':
        if arch_model is None:
            raise RuntimeError("Pacote 'arch' não disponível para método garch")
        am = arch_model(returns.dropna() * 100, vol='GARCH', p=1, q=1, dist='normal')
        res = am.fit(disp='off')
        sigma = float(res.conditional_volatility.iloc[-1] / 100.0)
    else:
        raise ValueError("method deve ser std|ewma|garch")
    
    z = float(norm.ppf(1 - alpha))
    var_value = -(mu + z * sigma)
    details = {"mu": mu, "sigma": sigma, "z": z, "method": method}
    if method == 'ewma':
        details["ewma_lambda"] = ewma_lambda
    return float(var_value), details


def es_parametric(returns: pd.Series, alpha: float = 0.99, method: str = 'std', ewma_lambda: float = 0.94) -> Tuple[float, Dict]:
    """
    Calculates Parametric Expected Shortfall (ES) or Conditional Value at Risk (CVaR).

    IMPORTANT: Assumes normality of returns. ES is the average of losses beyond the VaR.

    Formula (normal distribution):
        ES = μ - σ * φ(z) / (1 - α)
        where φ is the PDF of the standard normal distribution and z = Φ^(-1)(1 - α).

    Args:
        returns (pd.Series): Series of asset returns.
        alpha (float): Confidence level.
        method (str): Calculation method: 'std', 'ewma', or 'garch'.
        ewma_lambda (float): EWMA decay factor.

    Returns:
        Tuple[float, Dict]: A tuple containing the ES value and a dictionary of details.

    Raises:
        ValueError: If an invalid method is specified.
    """
    mu = float(returns.mean())
    if method in ('std', 'ewma', 'garch'):
        v, d = var_parametric(returns, alpha=alpha, method=method, ewma_lambda=ewma_lambda)
        sigma = d["sigma"]
        z = float(norm.ppf(1 - alpha))
        es = -(mu - sigma * norm.pdf(z) / (1 - alpha))
        d.update({"z": z})
        return float(es), d
    raise ValueError("method deve ser std|ewma|garch")


def var_historical(returns: pd.Series, alpha: float = 0.99) -> Tuple[float, Dict]:
    """
    Calculates Historical Value at Risk (VaR).

    The historical VaR is determined by finding the (1-alpha) quantile of the
    historical returns distribution.

    Args:
        returns (pd.Series): Series of asset returns.
        alpha (float): Confidence level (e.g., 0.99 for 99% VaR).

    Returns:
        Tuple[float, Dict]: A tuple containing the VaR value and a dictionary of details
                            (e.g., {'quantile': q}).
    """
    q = returns.quantile(1 - alpha)
    return float(-q), {"quantile": q}


def es_historical(returns: pd.Series, alpha: float = 0.99) -> Tuple[float, Dict]:
    """
    Calculates Historical Expected Shortfall (ES) or Conditional Value at Risk (CVaR).

    ES is the average of losses that exceed the historical VaR at a given confidence level.

    Args:
        returns (pd.Series): Series of asset returns.
        alpha (float): Confidence level (e.g., 0.99 for 99% ES).

    Returns:
        Tuple[float, Dict]: A tuple containing the ES value and a dictionary of details
                            (e.g., {'threshold': q, 'n_tail': count}).
    """
    q = returns.quantile(1 - alpha)
    tail = returns[returns < q]
    es = tail.mean()
    return float(-es), {"threshold": q, "n_tail": len(tail)}


def var_evt(returns: pd.Series, alpha: float = 0.99, threshold_quantile: float = 0.9) -> Tuple[float, Dict]:
    """
    Calculates Value at Risk (VaR) using Extreme Value Theory (EVT) with a Generalized Pareto Distribution (GPD).

    This method models the tail of the loss distribution, providing a more robust VaR estimate
    for distributions with heavy tails compared to parametric methods assuming normality.
    It works with losses (L = -R).

    Args:
        returns (pd.Series): Series of asset returns.
        alpha (float): Confidence level (e.g., 0.99 for 99% VaR).
        threshold_quantile (float): Quantile used to define the threshold for extreme losses.
                                    Losses above this threshold are fitted to a GPD.

    Returns:
        Tuple[float, Dict]: A tuple containing the VaR value (as a positive loss) and a dictionary of details
                            (e.g., {'xi', 'beta', 'u', 'p_tail'}).

    Notes:
        - If the number of observations or excess values is too small, it falls back to historical VaR.
    """
    # Fallback to historical VaR if insufficient data
    losses = -returns
    n = len(losses)
    if n < 100:
        return var_historical(returns, alpha)
    
    u = losses.quantile(threshold_quantile)
    excesses = losses[losses > u] - u
    
    if len(excesses) < 10:
        return var_historical(returns, alpha)
    
    # Fit GPD using MLE (simplified)
    try:
        from scipy.stats import genpareto
        xi, loc, beta = genpareto.fit(excesses, floc=0)
        
        p_tail = len(excesses) / n
        var_loss = u + (beta / xi) * ((p_tail / (1 - alpha)) ** (-xi) - 1) if xi != 0 else u + beta * np.log(p_tail / (1 - alpha))
        
        return float(var_loss), {"xi": xi, "beta": beta, "u": u, "p_tail": p_tail}
    except Exception:
        return var_historical(returns, alpha)


def es_evt(returns: pd.Series, alpha: float = 0.99, threshold_quantile: float = 0.9) -> Tuple[float, Dict]:
    """
    Calculates Expected Shortfall (ES) using Extreme Value Theory (EVT) with a Generalized Pareto Distribution (GPD).

    ES for EVT is derived from the GPD parameters and the VaR calculated using EVT.
    It represents the expected loss given that the loss exceeds the VaR.

    Args:
        returns (pd.Series): Series of asset returns.
        alpha (float): Confidence level (e.g., 0.99 for 99% ES).
        threshold_quantile (float): Quantile used to define the threshold for extreme losses.

    Returns:
        Tuple[float, Dict]: A tuple containing the ES value (as a positive loss) and a dictionary of details
                            (e.g., {'xi', 'beta', 'u', 'p_tail', 'var_loss'}).

    Notes:
        - If the number of observations or excess values is too small, it falls back to historical ES.
    """
    var_loss, details = var_evt(returns, alpha, threshold_quantile)
    
    if 'xi' not in details:  # Fallback was used
        return es_historical(returns, alpha)
    
    xi = details['xi']
    beta = details['beta']
    
    if xi >= 1:
        return es_historical(returns, alpha)
    
    es = var_loss / (1 - xi) + (beta - xi * details['u']) / (1 - xi)
    details['var_loss'] = var_loss
    
    return float(es), details


def drawdown(returns: pd.Series) -> Dict:
    """
    Calculates the maximum drawdown and its start/end dates for a series of returns.

    Drawdown measures the peak-to-trough decline during a specific period for an investment,
    portfolio, or fund.

    Args:
        returns (pd.Series): Series of asset or portfolio returns.

    Returns:
        Dict: A dictionary containing:
              - "max_drawdown" (float): The maximum drawdown as a negative percentage.
              - "start" (str): The start date of the maximum drawdown period.
              - "end" (str): The end date of the maximum drawdown period.
    """
    cum_returns = (1 + returns).cumprod()
    running_max = cum_returns.cummax()
    drawdown_series = (cum_returns - running_max) / running_max
    
    max_drawdown = drawdown_series.min()
    end_date = drawdown_series.idxmin()
    
    end_idx = cum_returns.index.get_loc(end_date)
    target_value = running_max.iloc[end_idx]
    
    start_idx = 0
    for i in range(end_idx, -1, -1):
        if cum_returns.iloc[i] >= target_value * 0.9999:
            start_idx = i
            break
    
    start_date = cum_returns.index[start_idx]
    
    # Format dates based on index type
    def format_date(d):
        if hasattr(d, 'strftime'):
            return d.strftime('%Y-%m-%d')
        return str(d)
    
    return {
        "max_drawdown": max_drawdown,
        "start": format_date(start_date),
        "end": format_date(end_date)
    }
