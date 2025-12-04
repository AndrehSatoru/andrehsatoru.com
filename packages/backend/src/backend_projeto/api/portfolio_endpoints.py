"""
This module defines FastAPI endpoints related to portfolio management and analysis.

It provides a route for generating a time series of constant weights for a
buy-and-hold portfolio, useful for backtesting and performance attribution.
"""
# src/backend_projeto/api/portfolio_endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from backend_projeto.domain.models import (
    WeightsSeriesRequest, 
    WeightsSeriesResponse,
    MonthlyReturnsRequest,
    MonthlyReturnsResponse,
    MonthlyReturnRow,
)
from backend_projeto.domain.constants import CDI_PROXIES, MONTH_MAP
from .deps import get_loader
from backend_projeto.infrastructure.data_handling import YFinanceProvider
import pandas as pd
import numpy as np
import math
from datetime import datetime
from typing import Optional, List, Any
import logging


def _safe_float(value: Any) -> Optional[float]:
    """Convert value to float, returning None for NaN/Infinity."""
    if value is None:
        return None
    try:
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return None
        return round(f, 2)
    except (ValueError, TypeError):
        return None

router = APIRouter(
    tags=["Portfolio"],
    responses={404: {"description": "Not found"}},
)


def _calculate_monthly_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly returns from daily prices."""
    return prices.sort_index().resample('M').last().pct_change().dropna(how='all') * 100


def _get_cdi_monthly_returns(loader: YFinanceProvider, start_date: str, end_date: str) -> pd.Series:
    """Fetch CDI monthly returns. Uses a proxy if direct CDI is not available."""
    try:
        # Try to fetch IMAB11 or FIXA11 as CDI proxy
        for proxy in CDI_PROXIES:
            try:
                cdi_prices = loader.fetch_stock_prices([proxy], start_date, end_date)
                if not cdi_prices.empty:
                    cdi_monthly = cdi_prices.resample('M').last().pct_change().dropna() * 100
                    return cdi_monthly.iloc[:, 0] if isinstance(cdi_monthly, pd.DataFrame) else cdi_monthly
            except Exception:
                logging.warning(f"Failed to fetch data for CDI proxy: {proxy}", exc_info=False)
                continue
        return pd.Series(dtype=float)
    except Exception as e:
        logging.error(f"Critical error fetching CDI proxy: {e}", exc_info=True)
        return pd.Series(dtype=float)


@router.post("/portfolio/monthly-returns", response_model=MonthlyReturnsResponse)
def get_monthly_returns(
    req: MonthlyReturnsRequest,
    loader: YFinanceProvider = Depends(get_loader),
) -> MonthlyReturnsResponse:
    """
    Calculates monthly returns for a portfolio.

    Args:
        req (MonthlyReturnsRequest): Request body containing assets, start date, end date, and optional weights.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        MonthlyReturnsResponse: A Pydantic model containing monthly returns data by year and month.
    """
    try:
        # Fetch prices
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        if prices.empty:
            raise HTTPException(status_code=404, detail="No price data found for the specified assets and period")
        
        # Calculate weights
        n = len(req.assets)
        if req.weights is None:
            weights = np.array([1.0 / n] * n)
        else:
            weights = np.array(req.weights)
            weights = weights / weights.sum()
        
        # Calculate daily returns
        daily_returns = prices.pct_change().dropna()
        
        # Calculate portfolio daily returns
        portfolio_returns = (daily_returns * weights).sum(axis=1)
        
        # Convert to monthly returns
        portfolio_prices = (1 + portfolio_returns).cumprod()
        monthly_prices = portfolio_prices.resample('M').last()
        monthly_returns = monthly_prices.pct_change() * 100
        
        # Try to get CDI/benchmark returns
        cdi_returns = _get_cdi_monthly_returns(loader, req.start_date, req.end_date)
        
        # Build response data
        
        years = sorted(set(monthly_returns.dropna().index.year))
        result_data: List[MonthlyReturnRow] = []
        
        acum_fdo = 0.0
        acum_cdi = 0.0
        
        for year in years:
            year_data = monthly_returns[monthly_returns.index.year == year]
            year_cdi = cdi_returns[cdi_returns.index.year == year] if not cdi_returns.empty else pd.Series()
            
            row_dict = {'year': year}
            year_acum = 1.0
            year_cdi_acum = 1.0
            
            for month in range(1, 13):
                month_key = MONTH_MAP[month]
                if month_key == 'set':
                    month_key = 'set_'
                
                month_data = year_data[year_data.index.month == month]
                if not month_data.empty:
                    val = _safe_float(month_data.iloc[0])
                    row_dict[month_key] = val
                    if val is not None:
                        year_acum *= (1 + val / 100)
                else:
                    row_dict[month_key] = None
                
                # CDI for the month
                month_cdi = year_cdi[year_cdi.index.month == month] if not year_cdi.empty else pd.Series()
                if not month_cdi.empty:
                    cdi_val = _safe_float(month_cdi.iloc[0])
                    if cdi_val is not None:
                        year_cdi_acum *= (1 + cdi_val / 100)
            
            # Annual accumulation
            acum_ano = _safe_float((year_acum - 1) * 100)
            row_dict['acumAno'] = acum_ano
            
            # CDI annual
            cdi_ano = _safe_float((year_cdi_acum - 1) * 100) if not year_cdi.empty else None
            row_dict['cdi'] = cdi_ano
            
            # Cumulative fund
            acum_fdo = ((1 + acum_fdo / 100) * year_acum - 1) * 100
            row_dict['acumFdo'] = _safe_float(acum_fdo)
            
            # Cumulative CDI
            if cdi_ano is not None:
                acum_cdi = ((1 + acum_cdi / 100) * year_cdi_acum - 1) * 100
                row_dict['acumCdi'] = _safe_float(acum_cdi)
            else:
                row_dict['acumCdi'] = None
            
            result_data.append(MonthlyReturnRow(**row_dict))
        
        return MonthlyReturnsResponse(
            data=result_data,
            lastUpdate=datetime.now().strftime('%Y-%m-%d')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error calculating monthly returns: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating monthly returns: {str(e)}")

# Weights series (buy-and-hold constant weights over time)
@router.post("/portfolio/weights-series", response_model=WeightsSeriesResponse)
def portfolio_weights_series(
    req: WeightsSeriesRequest,
    loader: YFinanceProvider = Depends(get_loader),
) -> WeightsSeriesResponse:
    """
    Generates a series of constant weights for a buy-and-hold portfolio over time.

    Args:
        req (WeightsSeriesRequest): Request body containing assets, start date, end date, and optional weights.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        WeightsSeriesResponse: A Pydantic model containing the time series of portfolio weights.
    """
    df = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date).sort_index()
    idx = [idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx) for idx in df.index]
    n = len(req.assets)
    if req.weights is None:
        w = [1.0 / n] * n
    else:
        s = sum(req.weights)
        w = [wi / s for wi in req.weights]
    weights_series = {asset: [float(w[i])] * len(idx) for i, asset in enumerate(req.assets)}
    return WeightsSeriesResponse(index=idx, weights=weights_series)
