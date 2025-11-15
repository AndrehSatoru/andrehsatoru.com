"""
This module provides core utility functions used across various financial analysis components.

It includes functions for:
- Calculating daily percentage returns from price data.
- Annualizing mean returns and covariance matrices.
"""
import pandas as pd
import numpy as np
from typing import Tuple

def _returns_from_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Calcula os retornos diários percentuais a partir de um DataFrame de preços.

    Parâmetros:
        prices (pd.DataFrame): DataFrame de preços.

    Retorna:
        pd.DataFrame: DataFrame de retornos.
    """
    return prices.sort_index().pct_change().dropna(how='all')

def _annualize_mean_cov(rets: pd.DataFrame, dias_uteis: int) -> Tuple[np.ndarray, np.ndarray]:
    """Anualiza a média e a matriz de covariância dos retornos.

    Parâmetros:
        rets (pd.DataFrame): DataFrame de retornos.
        dias_uteis (int): Número de dias úteis no ano.

    Retorna:
        Tuple[np.ndarray, np.ndarray]: Tupla contendo a média anualizada e a matriz de covariância anualizada.
    """
    mu = rets.mean().values * dias_uteis
    cov = rets.cov().values * dias_uteis
    return mu, cov
