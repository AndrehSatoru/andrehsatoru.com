"""
This module defines FastAPI endpoints for fetching financial data.

It provides routes for:
- Retrieving a list of available assets.
- Fetching historical price data for specified assets and date ranges.
- Includes caching mechanisms for frequently accessed data.
"""
# src/backend_projeto/api/data_endpoints.py
from datetime import date
import logging
from functools import lru_cache
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from typing import List, Optional
from .models import PricesRequest, PricesResponse
from .deps import get_loader
from src.backend_projeto.core.data_handling import YFinanceProvider

router = APIRouter(
    tags=["Data"],
    responses={404: {"description": "Not found"}},
)

@router.options("/prices", status_code=200)
def options_prices() -> Response:
    """
    Handles OPTIONS requests for the /prices endpoint.

    This endpoint is typically used by browsers for preflight requests in CORS.

    Returns:
        Response: An empty FastAPI Response with a 200 status code.
    """
    return {}

@lru_cache(maxsize=1)
def get_cached_assets() -> List[str]:
    """
    Returns a cached list of available assets.

    This function uses `lru_cache` to store the list of assets in memory,
    reducing the need to re-generate it on subsequent calls.

    Returns:
        List[str]: A list of asset tickers.
    """
    return [
        "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "B3SA3.SA",
        "RENT3.SA", "WEGE3.SA", "BBAS3.SA", "ITSA4.SA", "MGLU3.SA",
        "ABEV3.SA", "EGIE3.SA", "ELET3.SA", "BRFS3.SA", "RAIL3.SA",
        "RADL3.SA", "SUZB3.SA", "TOTS3.SA", "UGPA3.SA", "VBBR3.SA"
    ]

@router.get("/assets", response_class=JSONResponse)
async def get_available_assets(response: Response) -> List[str]:
    """
    Returns a list of available assets with HTTP caching headers.

    The response includes `Cache-Control` and `Vary` headers to optimize caching
    by clients and proxies.
    """
    assets = get_cached_assets()
    
    # Configurar headers de cache
    response.headers["Cache-Control"] = "public, max-age=3600"  # Cache por 1 hora
    response.headers["Vary"] = "Accept-Encoding"
    
    return assets

@router.post("/prices", response_model=PricesResponse)
@router.get("/prices", response_model=PricesResponse)
async def get_prices(
    assets: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    payload: Optional[PricesRequest] = None,
    loader: YFinanceProvider = Depends(get_loader)
) -> PricesResponse:
    """
    Returns historical prices for the specified assets.

    This endpoint supports both GET and POST requests. For GET requests, parameters
    are passed as query parameters. For POST requests, parameters are passed in the
    request body as a PricesRequest object.

    Args:
        assets (Optional[str]): Comma-separated string of asset tickers (for GET requests).
        start_date (Optional[str]): Start date in 'YYYY-MM-DD' format (for GET requests).
        end_date (Optional[str]): End date in 'YYYY-MM-DD' format (for GET requests).
        payload (Optional[PricesRequest]): Request body containing assets, start date, and end date (for POST requests).
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        PricesResponse: A Pydantic model containing the historical price data.

    Raises:
        HTTPException: 400 if invalid parameters are provided,
                       404 if no data is found for the specified assets and period.
    """
    # Se receber via GET, converter os parâmetros
    if assets and start_date and end_date:
        asset_list = assets.split(',')
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    # Se receber via POST, usar o payload
    elif payload:
        asset_list = payload.assets
        start = date.fromisoformat(payload.start_date)
        end = date.fromisoformat(payload.end_date)
    else:
        raise HTTPException(status_code=400, detail="Parâmetros inválidos")

    df = loader.fetch_stock_prices(asset_list, start, end)
    if df.empty:
        raise HTTPException(status_code=404, detail="Nenhum dado encontrado para os ativos no período especificado.")
    df = df.sort_index()
    return PricesResponse(
        columns=[str(c) for c in df.columns],
        index=[idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx) for idx in df.index],
        data=df.values.tolist(),
    )
