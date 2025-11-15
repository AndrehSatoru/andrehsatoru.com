"""
This module provides functions for generating various financial visualizations.

It primarily focuses on creating static image plots (PNG) for concepts like
the efficient frontier, using `matplotlib`.
"""
# visualization.py

import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend não interativo para geração de imagens
import matplotlib.pyplot as plt
from typing import List, Optional, Tuple

from ..utils.config import Settings
from .data_handling import DataLoader


def efficient_frontier_image(
    loader: DataLoader,
    config: Settings,
    assets: List[str],
    start_date: str,
    end_date: str,
    n_samples: int = 5000,
    long_only: bool = True,
    max_weight: Optional[float] = None,
    rf: float = 0.0,
) -> bytes:
    """
    Generates a PNG image of the efficient frontier by randomly sampling portfolios.

    Args:
        loader (DataLoader): An instance of a data loader to fetch asset prices.
        config (Settings): Configuration object containing application settings.
        assets (List[str]): List of asset tickers to include in the portfolio.
        start_date (str): Start date for historical data (YYYY-MM-DD).
        end_date (str): End date for historical data (YYYY-MM-DD).
        n_samples (int): Number of random portfolios to sample. Defaults to 5000.
        long_only (bool): If True, restricts portfolio weights to be non-negative. Defaults to True.
        max_weight (Optional[float]): Maximum weight allowed for any single asset. If None, no upper limit.
        rf (float): Risk-free rate for Sharpe ratio calculation. Defaults to 0.0.

    Returns:
        bytes: PNG image of the efficient frontier plot in bytes format.

    Raises:
        ValueError: If `long_only` is False (not supported by current visualization),
                    or if fewer than 2 assets are provided for optimization.
    """
