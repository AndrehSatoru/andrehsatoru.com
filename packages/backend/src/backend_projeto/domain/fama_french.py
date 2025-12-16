"""
Fama-French factor model metrics module.

This module provides functions for:
- Fama-French 3-factor model analysis
- Fama-French 5-factor model analysis
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm
import logging
from typing import Dict, List, Any


def _monthly_returns_from_prices(df_prices: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates monthly returns from a DataFrame of daily prices.

    Args:
        df_prices (pd.DataFrame): DataFrame where the index are daily dates
                                  and columns are asset prices.

    Returns:
        pd.DataFrame: DataFrame containing monthly percentage returns for each asset.
    """
    return df_prices.sort_index().resample('M').last().pct_change().dropna(how='all')


def ff3_metrics(
    prices: pd.DataFrame,
    ff3_factors: pd.DataFrame,
    rf_series: pd.Series,
    assets: List[str],
) -> Dict:
    """
    Calculates Fama-French 3-factor model metrics (monthly) per asset via OLS.

    Args:
        prices: DataFrame of daily prices. Will be converted to monthly returns.
        ff3_factors: Monthly DataFrame with columns ['MKT_RF','SMB','HML'] (in decimal).
        rf_series: Monthly series of risk-free rate in decimal.
        assets: List of assets to evaluate.

    Returns:
        Dict per asset: alpha, betas, tstats, pvalues, r2, n_obs.
    """
    rets_m = _monthly_returns_from_prices(prices[assets]).dropna(how='all')
    factors = ff3_factors[['MKT_RF', 'SMB', 'HML']].copy()
    rf_m = rf_series.copy()
    df = rets_m.join(factors, how='inner').join(rf_m.to_frame('RF'), how='inner')
    if df.empty:
        raise ValueError("Sem interseção temporal entre retornos, fatores e RF")

    X = df[['MKT_RF', 'SMB', 'HML']]
    X = sm.add_constant(X)

    results: Dict[str, Any] = {}
    for a in assets:
        if a not in df.columns:
            continue
        y = (df[a] - df['RF']).dropna()
        XA = X.loc[y.index]
        
        # 1. Increased threshold for FF3 (4 params) -> 24 obs recommended
        if len(y) < 24:
            logging.warning(f"Asset {a}: Insufficient data ({len(y)} < 24). Skipping.")
            continue
            
        # 2. Rank validation
        if np.linalg.matrix_rank(XA) < XA.shape[1]:
            logging.warning(f"Asset {a}: Singular design matrix (perfect collinearity). Skipping.")
            continue

        model = sm.OLS(y.values, XA.values)
        
        # 3. Secure fit using QR decomposition
        try:
            res = model.fit(method='qr')
        except Exception as e:
            logging.error(f"Asset {a}: OLS fit error: {e}")
            continue

        params = res.params.tolist()
        pvals = res.pvalues.tolist()
        tstats = res.tvalues.tolist()
        
        note = None
        if int(res.nobs) < 36:
            note = "Observation count < 36; estimates may be unstable."
            
        # 4. Condition Number validation
        if res.condition_number > 1000:
            cond_msg = f"High condition number ({res.condition_number:.1f})."
            note = f"{note} {cond_msg}" if note else cond_msg

        results[a] = {
            'alpha': float(params[0]),
            'beta_mkt': float(params[1]),
            'beta_smb': float(params[2]),
            'beta_hml': float(params[3]),
            'pvalues': pvals,
            'tstats': tstats,
            'r2': float(res.rsquared),
            'n_obs': int(res.nobs),
            'notes': note,
        }
    return {'frequency': 'M', 'model': 'FF3', 'results': results}


def ff5_metrics(
    prices: pd.DataFrame,
    ff5_factors: pd.DataFrame,
    rf_series: pd.Series,
    assets: List[str],
) -> Dict:
    """
    Calculates Fama-French 5-factor model metrics (monthly) per asset via OLS.

    Expects columns: ['MKT_RF','SMB','HML','RMW','CMA'] in decimal.

    Args:
        prices: DataFrame of daily prices. Will be converted to monthly returns.
        ff5_factors: Monthly DataFrame with columns ['MKT_RF','SMB','HML','RMW','CMA'].
        rf_series: Monthly series of risk-free rate in decimal.
        assets: List of assets to evaluate.

    Returns:
        Dict per asset: alpha, betas, tstats, pvalues, r2, n_obs.
    """
    rets_m = _monthly_returns_from_prices(prices[assets]).dropna(how='all')
    factors = ff5_factors[['MKT_RF', 'SMB', 'HML', 'RMW', 'CMA']].copy()
    rf_m = rf_series.copy()
    df = rets_m.join(factors, how='inner').join(rf_m.to_frame('RF'), how='inner')
    if df.empty:
        raise ValueError("Sem interseção temporal entre retornos, fatores e RF (FF5)")
    
    X = df[['MKT_RF', 'SMB', 'HML', 'RMW', 'CMA']]
    X = sm.add_constant(X)
    
    results: Dict[str, Any] = {}
    for a in assets:
        if a not in df.columns:
            continue
        y = (df[a] - df['RF']).dropna()
        XA = X.loc[y.index]
        
        # 1. Increased threshold for FF5 (6 params) -> 36 obs recommended
        if len(y) < 36:
            logging.warning(f"Asset {a}: Insufficient data ({len(y)} < 36). Skipping.")
            continue

        # 2. Rank validation
        if np.linalg.matrix_rank(XA) < XA.shape[1]:
            logging.warning(f"Asset {a}: Singular design matrix (perfect collinearity). Skipping.")
            continue

        model = sm.OLS(y.values, XA.values)
        
        # 3. Secure fit using QR decomposition
        try:
            res = model.fit(method='qr')
        except Exception as e:
            logging.error(f"Asset {a}: OLS fit error: {e}")
            continue

        params = res.params.tolist()
        pvals = res.pvalues.tolist()
        tstats = res.tvalues.tolist()
        
        note = None
        if int(res.nobs) < 48:
            note = "Observation count < 48; estimates may be unstable."

        # 4. Condition Number validation
        if res.condition_number > 1000:
            cond_msg = f"High condition number ({res.condition_number:.1f})."
            note = f"{note} {cond_msg}" if note else cond_msg

        results[a] = {
            'alpha': float(params[0]),
            'beta_mkt': float(params[1]),
            'beta_smb': float(params[2]),
            'beta_hml': float(params[3]),
            'beta_rmw': float(params[4]),
            'beta_cma': float(params[5]),
            'pvalues': pvals,
            'tstats': tstats,
            'r2': float(res.rsquared),
            'n_obs': int(res.nobs),
            'notes': note,
        }
    return {'frequency': 'M', 'model': 'FF5', 'results': results}
