"""
This module defines FastAPI endpoints related to dashboard functionalities.

It includes an endpoint for testing investment performance based on user-defined
assets, weights, and time periods, and calculates various performance metrics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
import pandas as pd
from typing import List, Dict, Any, Optional
import numpy as np
from pydantic import BaseModel
import datetime

from src.backend_projeto.core.dashboard_generator import DashboardGenerator
from src.backend_projeto.core.data_handling import YFinanceProvider
from src.backend_projeto.core.exceptions import DataProviderError
from src.backend_projeto.core.analysis import compute_returns, portfolio_returns, drawdown
from src.backend_projeto.utils.config import settings
from .deps import get_loader, get_config

router = APIRouter()

class InvestmentRequest(BaseModel):
    """
    Pydantic model for investment request data.

    Attributes:
        assets (List[str]): List of asset tickers.
        weights (List[float]): List of weights corresponding to each asset.
        period (str): The investment period (e.g., "365" for 365 days).
    """

def calculate_performance(returns_series: pd.Series) -> Dict[str, float]:
    """
    Calculates various performance metrics for a given series of returns.

    Args:
        returns_series (pd.Series): A pandas Series of returns.

    Returns:
        Dict[str, float]: A dictionary containing calculated performance metrics:
                          - "cumulative_returns"
                          - "annualized_returns"
                          - "annualized_volatility"
                          - "sharpe_ratio"
                          - "max_drawdown"
    """
    cumulative_returns = (1 + returns_series).cumprod() - 1
    annualized_returns = returns_series.mean() * 252
    annualized_volatility = returns_series.std() * np.sqrt(252)
    sharpe_ratio = annualized_returns / annualized_volatility if annualized_volatility != 0 else 0
    drawdown_info = drawdown(returns_series)

    return {
        "cumulative_returns": cumulative_returns.iloc[-1],
        "annualized_returns": annualized_returns,
        "annualized_volatility": annualized_volatility,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": drawdown_info['max_drawdown'],
    }

@router.post("/test-investment")
async def test_investment(
    request: InvestmentRequest,
    loader: YFinanceProvider = Depends(get_loader),
) -> Dict[str, float]:
    """
    Tests an investment portfolio's performance based on specified assets, weights, and period.

    Args:
        request (InvestmentRequest): Request body containing assets, weights, and the period for analysis.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        Dict[str, float]: A dictionary containing various performance metrics for the simulated portfolio.

    Raises:
        HTTPException: 404 if no price data is found for the given assets and date range,
                       503 if there's a data provider error,
                       500 for other internal server errors.
    """
    try:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=int(request.period))

        prices_df = loader.fetch_stock_prices(request.assets, start_date.isoformat(), end_date.isoformat())

        if prices_df.empty:
            raise HTTPException(status_code=404, detail="No price data found for the given assets and date range.")

        returns_df = compute_returns(prices_df)
        port_returns = portfolio_returns(returns_df, request.assets, request.weights)

        performance = calculate_performance(port_returns)

        return performance
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Data provider error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
