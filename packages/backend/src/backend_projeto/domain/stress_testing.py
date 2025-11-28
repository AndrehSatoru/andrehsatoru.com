"""
Stress testing and VaR backtesting module.

This module provides functions for:
- Stress testing portfolios under various scenarios
- Backtesting VaR models
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from scipy.stats import norm, chi2


def stress_test(returns_df: pd.DataFrame, assets: List[str], weights: Optional[List[float]], shocks_pct: float = -0.1) -> Dict:
    """
    Performs a stress test by applying a hypothetical shock to the latest returns of specified assets.

    This function simulates the impact of an immediate, adverse market movement on the portfolio's
    return by adjusting the last observed returns by a given percentage shock.

    Args:
        returns_df (pd.DataFrame): DataFrame of historical asset returns.
        assets (List[str]): List of asset tickers to include in the portfolio.
        weights (Optional[List[float]]): Weights of the assets in the portfolio. If None, equal weights are assumed.
        shocks_pct (float): The percentage shock to apply to the latest returns (e.g., -0.1 for a -10% shock).

    Returns:
        Dict: A dictionary containing:
              - "shock" (float): The applied shock percentage.
              - "portfolio_return" (float): The simulated portfolio return after the shock.
              - "asset_returns" (Dict[str, float]): The simulated returns for each asset after the shock.
    """
    if weights is None:
        weights = [1.0 / len(assets)] * len(assets)
    
    weights_arr = np.array(weights)
    latest_returns = returns_df[assets].iloc[-1].values
    stressed_returns = latest_returns + shocks_pct
    portfolio_return = float(np.dot(weights_arr, stressed_returns))
    asset_returns = {asset: float(stressed_returns[i]) for i, asset in enumerate(assets)}
    
    return {
        "shock": shocks_pct,
        "portfolio_return": portfolio_return,
        "asset_returns": asset_returns,
        "original_returns": {asset: float(latest_returns[i]) for i, asset in enumerate(assets)},
        "impact": portfolio_return - float(np.dot(weights_arr, latest_returns))
    }


def backtest_var(returns: pd.Series, alpha: float, method: str = 'historical', ewma_lambda: float = 0.94) -> Dict:
    """
    Performs a backtest of Value at Risk (VaR) using a rolling window.

    This function evaluates the accuracy of a VaR model by comparing predicted VaR values
    with actual portfolio losses over a historical period. It calculates the number of
    exceptions (times actual loss exceeded VaR) and performs Kupiec's POF test and
    Christoffersen's independence test. It also provides a Basel Traffic-Light zone.

    Args:
        returns (pd.Series): Series of portfolio returns.
        alpha (float): Confidence level for VaR calculation.
        method (str): VaR calculation method ('historical', 'std', 'ewma', 'garch', 'evt').
        ewma_lambda (float): Decay factor for the EWMA method.

    Returns:
        Dict: A dictionary containing backtest results, including:
              - "n" (int): Total number of observations in the backtest period.
              - "exceptions" (int): Number of times actual losses exceeded VaR.
              - "exception_rate" (float): The rate of exceptions.
              - "kupiec_lr" (float): Kupiec's Likelihood Ratio statistic.
              - "kupiec_pvalue" (float): P-value for Kupiec's test.
              - "christoffersen_lr_ind" (float): Christoffersen's independence LR statistic.
              - "christoffersen_pvalue" (float): P-value for Christoffersen's independence test.
              - "christoffersen_lr_cc" (float): Christoffersen's conditional coverage LR statistic.
              - "christoffersen_cc_pvalue" (float): P-value for Christoffersen's conditional coverage test.
              - "basel_zone" (str): Basel Traffic-Light zone ('green', 'amber', 'red').
              - "alpha" (float): The confidence level used.
              - "method" (str): The VaR method used for backtesting.

    Raises:
        ValueError: If an invalid VaR method is provided.
    """
    if len(returns) < 30:
        raise ValueError("Insufficient data for backtesting (need at least 30 observations)")
    
    window = min(250, len(returns) - 1)
    
    var_series = []
    for i in range(window, len(returns)):
        window_returns = returns.iloc[i-window:i]
        if method == 'historical':
            var_value = -np.percentile(window_returns, (1 - alpha) * 100)
        elif method == 'std':
            var_value = window_returns.std() * norm.ppf(alpha)
        elif method == 'ewma':
            var_value = window_returns.ewm(alpha=1-ewma_lambda).std().iloc[-1] * norm.ppf(alpha)
        else:
            raise ValueError(f"Unsupported VaR method: {method}")
        var_series.append(var_value)
    
    actual_losses = -returns.iloc[window:]
    exceptions = (actual_losses > var_series).sum()
    n = len(var_series)
    exception_rate = exceptions / n if n > 0 else 0
    
    # Kupiec test
    if exceptions == 0:
        kupiec_lr = 0
        kupiec_pvalue = 1.0
    else:
        p_hat = exception_rate
        p = 1 - alpha
        kupiec_lr = -2 * np.log(((1-p)**(n-exceptions) * p**exceptions) / ((1-p_hat)**(n-exceptions) * p_hat**exceptions))
        kupiec_pvalue = 1 - chi2.cdf(kupiec_lr, 1)
    
    # Christoffersen test
    exception_series = (actual_losses > var_series).astype(int)
    if exceptions > 1:
        autocorr = np.corrcoef(exception_series[:-1], exception_series[1:])[0, 1]
        christoffersen_lr_ind = n * autocorr**2
        christoffersen_pvalue = 1 - chi2.cdf(christoffersen_lr_ind, 1)
        christoffersen_lr_cc = kupiec_lr + christoffersen_lr_ind
        christoffersen_cc_pvalue = 1 - chi2.cdf(christoffersen_lr_cc, 2)
    else:
        christoffersen_lr_ind = 0
        christoffersen_pvalue = 1.0
        christoffersen_lr_cc = kupiec_lr
        christoffersen_cc_pvalue = kupiec_pvalue
    
    # Basel zones
    if exception_rate <= 0.01:
        basel_zone = "green"
    elif exception_rate <= 0.02:
        basel_zone = "amber"
    else:
        basel_zone = "red"
    
    return {
        "n": n,
        "exceptions": int(exceptions),
        "exception_rate": float(exception_rate),
        "kupiec_lr": float(kupiec_lr),
        "kupiec_pvalue": float(kupiec_pvalue),
        "christoffersen_lr_ind": float(christoffersen_lr_ind),
        "christoffersen_pvalue": float(christoffersen_pvalue),
        "christoffersen_lr_cc": float(christoffersen_lr_cc),
        "christoffersen_cc_pvalue": float(christoffersen_cc_pvalue),
        "basel_zone": basel_zone,
        "alpha": alpha,
        "method": method
    }
