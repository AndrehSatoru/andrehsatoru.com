"""
This module provides helper functions used by various API endpoints.

These utilities include:
- Normalizing benchmark aliases to standardized tickers.
- Converting asset prices from BRL to USD using exchange rates.
"""
# src/backend_projeto/api/helpers.py
from typing import Optional, List
import pandas as pd
from backend_projeto.core.data_handling import YFinanceProvider

def _normalize_benchmark_alias(benchmark: Optional[str]) -> str:
    """
    Helper function to normalize common benchmark aliases to concrete tickers.

    Args:
        benchmark (Optional[str]): The input benchmark string, which might be an alias.

    Returns:
        str: The normalized benchmark ticker.
    """
    alias_raw = (benchmark or '')
    alias = alias_raw.strip().lower()
    normalized = alias.replace(' ', '').replace('-', '').replace('_', '').replace('&', 'and')
    alias_map = {
        # S&P 500
        'sp500': '^GSPC',
        'sandp500': '^GSPC',
        'snp500': '^GSPC',
        '^gspc': '^GSPC',
        'spy': 'SPY',
        # MSCI World
        'msciworld': 'URTH',
        'msciworldindex': 'URTH',
        'msciworldetf': 'URTH',
        'urth': 'URTH',
        'acwi': 'ACWI',
    }
    return alias_map.get(normalized, benchmark)

def _convert_prices_to_usd(prices_df: pd.DataFrame, assets: List[str], start_date: str, end_date: str, loader: YFinanceProvider) -> pd.DataFrame:
    """
    Helper function to convert BRL-priced assets to USD using USDBRL exchange rates.

    Args:
        prices_df (pd.DataFrame): DataFrame of asset prices, potentially including BRL assets.
        assets (List[str]): List of asset tickers.
        start_date (str): Start date for fetching exchange rates.
        end_date (str): End date for fetching exchange rates.
        loader (YFinanceProvider): Data loader to fetch asset info and exchange rates.

    Returns:
        pd.DataFrame: DataFrame with BRL-priced assets converted to USD.
    """
    try:
        # Descobrir moedas dos ativos
        asset_currencies = loader.provider.fetch_asset_info(assets)
    except Exception:
        asset_currencies = {a: ('BRL' if a.upper().endswith('.SA') else 'USD') for a in assets}
    brl_assets = [a for a in assets if asset_currencies.get(a, 'USD').upper() == 'BRL' and a in prices_df.columns]
    if not brl_assets:
        return prices_df
    # Buscar USDBRL e converter BRL -> USD
    fx = loader.fetch_exchange_rates(['USD'], start_date, end_date)  # coluna 'USD' = USDBRL
    fx = fx['USD'].reindex(prices_df.index).ffill().bfill()
    prices_conv = prices_df.copy()
    prices_conv[brl_assets] = prices_conv[brl_assets].div(fx, axis=0)
    return prices_conv
