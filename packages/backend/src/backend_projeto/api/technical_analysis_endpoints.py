"""
This module defines FastAPI endpoints for technical analysis calculations.

It provides routes for:
- Calculating Simple Moving Averages (SMA) and Exponential Moving Averages (EMA).
- Calculating Moving Average Convergence Divergence (MACD).
"""
# src/backend_projeto/api/technical_analysis_endpoints.py
from fastapi import APIRouter, Depends
from backend_projeto.domain.models import TAMovingAveragesRequest, TAMacdRequest, PricesResponse
from .deps import get_loader
from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.domain.technical_analysis import moving_averages, macd
from backend_projeto.api.helpers import _convert_prices_to_usd

router = APIRouter(
    tags=["Technical Analysis"],
    responses={404: {"description": "Not found"}},
)

@router.post("/ta/moving-averages", response_model=PricesResponse)
def ta_moving_averages(req: TAMovingAveragesRequest, loader: YFinanceProvider = Depends(get_loader)) -> PricesResponse:
    """
    Calculates moving averages (SMA or EMA) for the specified assets.

    Args:
        req (TAMovingAveragesRequest): Request body containing assets, start date, end date,
                                       moving average windows, method, and optional filters.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        PricesResponse: A Pydantic model containing the calculated moving average data.
    """
    prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
    if getattr(req, 'convert_to_usd', False):
        prices = _convert_prices_to_usd(prices, req.assets, req.start_date, req.end_date, loader)
    ta_df = moving_averages(prices, windows=req.windows, method=req.method)
    
    # Aplicar filtros opcionais
    if not req.include_original:
        # Remove colunas originais de preços
        ta_df = ta_df[[c for c in ta_df.columns if c not in req.assets]]
    if req.only_columns:
        # Filtra apenas colunas especificadas
        available = [c for c in req.only_columns if c in ta_df.columns]
        ta_df = ta_df[available]
    
    ta_df = ta_df.sort_index()
    return PricesResponse(
        columns=[str(c) for c in ta_df.columns],
        index=[idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx) for idx in ta_df.index],
        data=ta_df.values.tolist(),
    )

@router.post("/ta/macd", response_model=PricesResponse)
def ta_macd(req: TAMacdRequest, loader: YFinanceProvider = Depends(get_loader)) -> PricesResponse:
    """
    Calculates MACD (Moving Average Convergence Divergence) for the specified assets.

    Args:
        req (TAMacdRequest): Request body containing assets, start date, end date,
                             and MACD parameters (fast, slow, signal periods).
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        PricesResponse: A Pydantic model containing the calculated MACD data.
    """
    prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
    ta_df = macd(prices, fast=req.fast, slow=req.slow, signal=req.signal)
    
    # Aplicar filtros opcionais
    if not req.include_original:
        ta_df = ta_df[[c for c in ta_df.columns if c not in req.assets]]
    if req.only_columns:
        available = [c for c in ta_df.columns if c in ta_df.columns]
        ta_df = ta_df[available]
    
    ta_df = ta_df.sort_index()
    return PricesResponse(
        columns=[str(c) for c in ta_df.columns],
        index=[idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx) for idx in ta_df.index],
        data=ta_df.values.tolist(),
    )
