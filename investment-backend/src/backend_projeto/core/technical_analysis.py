# core/technical_analysis.py
# Funções para médias móveis e MACD

import logging
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


def _ensure_sorted_index(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df = df.copy()
            df.index = pd.to_datetime(df.index)
        except Exception:
            pass
    return df.sort_index()


def sma(series: pd.Series, window: int) -> pd.Series:
    """SMA (média móvel simples)."""
    return series.rolling(window=window, min_periods=1).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    """EMA (média móvel exponencial)."""
    return series.ewm(span=window, adjust=False, min_periods=1).mean()


def moving_averages(
    prices: pd.DataFrame,
    windows: Iterable[int] = (5, 21),
    method: str = "sma",
    prefix: Optional[str] = None,
) -> pd.DataFrame:
    """Calcula médias móveis para cada coluna de `prices`.

    Parâmetros
    - prices: DataFrame com preços (cada coluna é um ativo)
    - windows: janelas, por padrão (5, 21)
    - method: "sma" ou "ema"
    - prefix: prefixo opcional para as novas colunas

    Retorna
    - DataFrame com as colunas originais + colunas das MMs calculadas
      no formato "{col}_{PREFIX}{method_upper}_{window}". Ex: PETR4.SA_SMA_5
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
    """Calcula MACD para uma série de preços.

    Retorna DataFrame com colunas: macd, signal, hist
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
    """Calcula MACD para cada coluna de `prices`.

    Retorna DataFrame com as colunas originais + 3 colunas por ativo:
    - {col}_{pre}MACD
    - {col}_{pre}MACD_SIGNAL
    - {col}_{pre}MACD_HIST
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
    """Atalho para calcular MM de 5 e 21 dias (SMA ou EMA)."""
    return moving_averages(prices, windows=(5, 21), method=method)


def macd_default(prices: pd.DataFrame) -> pd.DataFrame:
    """Atalho para MACD com parâmetros padrão (12, 26, 9)."""
    return macd(prices, fast=12, slow=26, signal=9)
