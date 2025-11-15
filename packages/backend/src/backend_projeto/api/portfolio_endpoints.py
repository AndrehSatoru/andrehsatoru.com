"""
This module defines FastAPI endpoints related to portfolio management and analysis.

It provides a route for generating a time series of constant weights for a
buy-and-hold portfolio, useful for backtesting and performance attribution.
"""
# src/backend_projeto/api/portfolio_endpoints.py
from fastapi import APIRouter, Depends
from .models import WeightsSeriesRequest, WeightsSeriesResponse
from .deps import get_loader
from backend_projeto.core.data_handling import YFinanceProvider

router = APIRouter(
    tags=["Portfolio"],
    responses={404: {"description": "Not found"}},
)

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
