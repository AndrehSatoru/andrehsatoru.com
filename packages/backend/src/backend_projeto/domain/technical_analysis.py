"""
This module provides functions for calculating common technical analysis indicators.

It includes implementations for:
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)
- Moving Average Convergence Divergence (MACD)

These functions operate on pandas DataFrames and Series, providing flexibility
for various financial data analysis tasks.
"""
# core/technical_analysis.py
# Funções para médias móveis e MACD

import logging
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


def _ensure_sorted_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures that the DataFrame's index is a sorted DatetimeIndex.

    If the index is not already a DatetimeIndex, it attempts to convert it.
    The DataFrame is then sorted by its index.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with a sorted DatetimeIndex.
    """
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    res = df.sort_index()
    # print(f"DEBUG: _ensure_sorted_index returning type {type(res)}")
    return res


def sma(series: pd.Series, window: int) -> pd.Series:
    """
    Calculates the Simple Moving Average (SMA) for a given series.

    Args:
        series (pd.Series): The input time series data.
        window (int): The number of periods over which to calculate the SMA.

    Returns:
        pd.Series: A Series containing the SMA values.
    """
    return series.rolling(window=window).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    """
    Calculates the Exponential Moving Average (EMA) for a given series.

    Args:
        series (pd.Series): The input time series data.
        window (int): The number of periods over which to calculate the EMA.

    Returns:
        pd.Series: A Series containing the EMA values.
    """
    return series.ewm(span=window, adjust=False).mean()


def moving_averages(
    prices: pd.DataFrame,
    windows: Iterable[int] = (5, 21),
    method: str = "sma",
    prefix: Optional[str] = None,
) -> pd.DataFrame:
    """
    Calculates moving averages for each column in a DataFrame of prices.

    Args:
        prices (pd.DataFrame): DataFrame containing prices (each column is an asset).
        windows (Iterable[int]): A collection of window sizes for the moving averages. Defaults to (5, 21).
        method (str): The method to use for calculating moving averages ("sma" or "ema"). Defaults to "sma".
        prefix (Optional[str]): An optional prefix for the new moving average column names.

    Returns:
        pd.DataFrame: A DataFrame with the original price columns plus new columns for the calculated
                      moving averages, named in the format "{col}_{PREFIX}{METHOD_UPPER}_{window}".
                      Example: PETR4.SA_SMA_5.

    Raises:
        ValueError: If an invalid method is specified.
    """
    prices = _ensure_sorted_index(prices)
    windows = list(int(w) for w in windows)
    method = method.lower().strip()
    if method not in ("sma", "ema"):
        raise ValueError("method deve ser 'sma' ou 'ema'")

    out = prices.copy()
    pre = "" if prefix is None else str(prefix)
    for col in prices.columns:
        s = prices[col].astype(float)
        for w in windows:
            if method == "sma":
                ma = sma(s, w)
                name = f"{col}_{pre}SMA_{w}" if pre else f"{col}_SMA_{w}"
            else:
                ma = ema(s, w)
                name = f"{col}_{pre}EMA_{w}" if pre else f"{col}_EMA_{w}"
            out[name] = ma
    return out


def macd_series(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """
    Calculates the Moving Average Convergence Divergence (MACD) for a single price series.

    Args:
        series (pd.Series): The input price series.
        fast (int): The fast period for EMA calculation. Defaults to 12.
        slow (int): The slow period for EMA calculation. Defaults to 26.
        signal (int): The signal period for EMA calculation on the MACD line. Defaults to 9.

    Returns:
        pd.DataFrame: A DataFrame with 'macd', 'signal', and 'hist' columns.
    """
    s = series.astype(float)
    ema_fast = s.ewm(span=int(fast), adjust=False, min_periods=1).mean()
    ema_slow = s.ewm(span=int(slow), adjust=False, min_periods=1).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=int(signal), adjust=False, min_periods=1).mean()
    hist = macd - macd_signal
    return pd.DataFrame({"macd": macd, "signal": macd_signal, "hist": hist}, index=s.index)


def macd(
    prices: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    prefix: Optional[str] = None,
) -> pd.DataFrame:
    """
    Calculates MACD for each column in a DataFrame of prices.

    Args:
        prices (pd.DataFrame): DataFrame containing prices.
        fast (int): The fast period for EMA calculation. Defaults to 12.
        slow (int): The slow period for EMA calculation. Defaults to 26.
        signal (int): The signal period for EMA calculation on the MACD line. Defaults to 9.
        prefix (Optional[str]): An optional prefix for the new MACD column names.

    Returns:
        pd.DataFrame: A DataFrame with the original price columns plus three new columns per asset:
                      - {col}_{PREFIX}MACD
                      - {col}_{PREFIX}MACD_SIGNAL
                      - {col}_{PREFIX}MACD_HIST
    """
    prices = _ensure_sorted_index(prices)
    out = prices.copy()
    pre = "" if prefix is None else str(prefix)
    for col in prices.columns:
        macd_df = macd_series(prices[col], fast=fast, slow=slow, signal=signal)
        out[f"{col}_{pre}MACD" if pre else f"{col}_MACD"] = macd_df["macd"]
        out[f"{col}_{pre}MACD_SIGNAL" if pre else f"{col}_MACD_SIGNAL"] = macd_df["signal"]
        out[f"{col}_{pre}MACD_HIST" if pre else f"{col}_MACD_HIST"] = macd_df["hist"]
    return out


# Utilidades prontas para 5 e 21 dias

def moving_averages_5_21(prices: pd.DataFrame, method: str = "sma") -> pd.DataFrame:
    """
    Shortcut to calculate 5 and 21-period moving averages (SMA or EMA).

    Args:
        prices (pd.DataFrame): DataFrame containing prices.
        method (str): The method to use for calculating moving averages ("sma" or "ema"). Defaults to "sma".

    Returns:
        pd.DataFrame: A DataFrame with the original price columns plus new columns for the 5 and 21-period MAs.
    """


def macd_default(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Shortcut for MACD calculation with default parameters (12, 26, 9).

    Args:
        prices (pd.DataFrame): DataFrame containing prices.

    Returns:
        pd.DataFrame: A DataFrame with the original price columns plus MACD, Signal, and Histogram columns.
    """
