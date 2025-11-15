"""
This module defines FastAPI endpoints for portfolio optimization.

It provides routes for:
- Markowitz portfolio optimization (maximizing Sharpe ratio, minimizing variance, maximizing return).
- Black-Litterman optimization, incorporating investor views.
- Retrieving efficient frontier data points for both Markowitz and Black-Litterman models.
"""
# src/backend_projeto/api/optimization_endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from .models import (
    OptimizeRequest, BLRequest, FrontierRequest, BLFrontierRequest, RiskResponse, FrontierDataResponse, FrontierPoint
)
from .deps import get_loader, get_optimization_engine, get_config
from backend_projeto.core.data_handling import YFinanceProvider
from backend_projeto.core.optimization import OptimizationEngine
from backend_projeto.core.analysis import compute_returns
from backend_projeto.utils.config import Settings

router = APIRouter(
    tags=["Optimization"],
    responses={404: {"description": "Not found"}},
)

# Otimização Markowitz
@router.post("/opt/markowitz", response_model=RiskResponse)
def opt_markowitz(req: OptimizeRequest, opt: OptimizationEngine = Depends(get_optimization_engine)) -> RiskResponse:
    """
    Performs Markowitz portfolio optimization (max Sharpe, min variance, max return).

    Args:
        req (OptimizeRequest): Request body containing assets, start date, end date,
                               objective, optional bounds, long-only constraint, max weight,
                               and an optional risk-free rate.
        opt (OptimizationEngine): Dependency injection for the optimization engine.

    Returns:
        RiskResponse: A Pydantic model containing the optimization results.
    """
    result = opt.optimize_markowitz(
        assets=req.assets,
        start_date=req.start_date,
        end_date=req.end_date,
        objective=req.objective,
        bounds=req.bounds,
        long_only=req.long_only,
        max_weight=req.max_weight,
        risk_free_rate=req.risk_free_rate
    )
    return RiskResponse(result=result)

# Black-Litterman
@router.post("/opt/blacklitterman", response_model=RiskResponse)
def opt_blacklitterman(req: BLRequest, opt: OptimizationEngine = Depends(get_optimization_engine)) -> RiskResponse:
    """
    Performs Black-Litterman optimization with subjective views.

    Args:
        req (BLRequest): Request body containing assets, start date, end date,
                         market caps, investor views, and tau parameter.
        opt (OptimizationEngine): Dependency injection for the optimization engine.

    Returns:
        RiskResponse: A Pydantic model containing the Black-Litterman optimization results.
    """
    result = opt.black_litterman(req.assets, req.start_date, req.end_date, req.market_caps, req.views, req.tau)
    return RiskResponse(result=result)

# Markowitz efficient frontier data (points)
@router.post("/opt/markowitz/frontier-data", response_model=FrontierDataResponse)
def frontier_data(
    req: FrontierRequest,
    loader: YFinanceProvider = Depends(get_loader),
    config: Settings = Depends(get_config),
) -> FrontierDataResponse:
    """
    Generates Markowitz efficient frontier data points.

    This endpoint simulates random portfolios to plot the efficient frontier,
    returning data points (return, volatility, Sharpe ratio, weights) rather than an image.

    Args:
        req (FrontierRequest): Request body containing assets, start date, end date,
                               number of samples, long-only constraint, max weight, and risk-free rate.
        loader (YFinanceProvider): Dependency injection for the data loader.
        config (Settings): Dependency injection for application settings.

    Returns:
        FrontierDataResponse: A Pydantic model containing a list of efficient frontier data points.

    Raises:
        HTTPException: 422 if fewer than 2 assets are provided.
    """
    import numpy as np
    prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
    rets = compute_returns(prices)[req.assets].dropna()
    if rets.shape[1] < 2:
        raise HTTPException(status_code=422, detail="São necessários pelo menos 2 ativos")
    mu = (rets.mean() * config.DIAS_UTEIS_ANO).values
    cov = (rets.cov() * config.DIAS_UTEIS_ANO).values
    n = len(req.assets)
    points: list[FrontierPoint] = []
    i = 0
    maxw = 1.0 if req.max_weight is None else float(req.max_weight)
    while i < req.n_samples:
        w = np.random.dirichlet(np.ones(n))
        if req.long_only and req.max_weight is not None and w.max() > maxw:
            continue
        ret = float(w @ mu)
        vol = float(np.sqrt(max(w @ cov @ w, 0.0)))
        sharpe = (ret - req.rf) / (vol + 1e-12)
        weights_map = {req.assets[j]: float(w[j]) for j in range(n)}
        points.append(FrontierPoint(ret_annual=ret, vol_annual=vol, sharpe=sharpe, weights=weights_map))
        i += 1
    return FrontierDataResponse(points=points)


# Black-Litterman frontier data using BL expected returns
@router.post("/opt/blacklitterman/frontier-data", response_model=FrontierDataResponse)
def bl_frontier_data(
    req: BLFrontierRequest,
    loader: YFinanceProvider = Depends(get_loader),
    config: Settings = Depends(get_config),
) -> FrontierDataResponse:
    """
    Generates Black-Litterman efficient frontier data points using BL expected returns.

    This endpoint combines market-implied returns with investor views to generate
    adjusted expected returns, then simulates portfolios to plot the efficient frontier.

    Args:
        req (BLFrontierRequest): Request body containing assets, start date, end date,
                                 market caps, investor views, tau, number of samples,
                                 long-only constraint, max weight, and risk-free rate.
        loader (YFinanceProvider): Dependency injection for the data loader.
        config (Settings): Dependency injection for application settings.

    Returns:
        FrontierDataResponse: A Pydantic model containing a list of efficient frontier data points.

    Raises:
        HTTPException: 422 if fewer than 2 assets are provided.
    """
    import numpy as np
    import numpy.linalg as LA
    prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
    rets = compute_returns(prices)[req.assets].dropna()
    if rets.shape[1] < 2:
        raise HTTPException(status_code=422, detail="São necessários pelo menos 2 ativos")
    mu_hist = (rets.mean() * config.DIAS_UTEIS_ANO).values
    Sigma = (rets.cov() * config.DIAS_UTEIS_ANO).values
    idx_map = {a: i for i, a in enumerate(req.assets)}
    caps = np.array([float(req.market_caps.get(a, 0.0)) for a in req.assets])
    if caps.sum() <= 0:
        w_mkt = np.ones(len(req.assets)) / len(req.assets)
    else:
        w_mkt = caps / caps.sum()
    pi = Sigma @ w_mkt
    if not req.views:
        mu_bl = pi
    else:
        P_list = []
        Q_list = []
        for v in req.views:
            aset = v.get('assets', [])
            wv = np.array(v.get('weights', []), dtype=float)
            row = np.zeros(len(req.assets))
            for ai, aw in zip(aset, wv):
                if ai in idx_map:
                    row[idx_map[ai]] = aw
            P_list.append(row)
            Q_list.append(float(v.get('view', 0.0)))
        P = np.vstack(P_list)
        Q = np.array(Q_list)
        tau = float(req.tau)
        tauSigma_inv = LA.inv(tau * Sigma)
        Omega = np.diag(np.diag(P @ (tau * Sigma) @ P.T))
        middle = tauSigma_inv + P.T @ LA.inv(Omega) @ P
        mu_bl = LA.inv(middle) @ (tauSigma_inv @ pi + P.T @ LA.inv(Omega) @ Q)
    n = len(req.assets)
    points: list[FrontierPoint] = []
    i = 0
    maxw = 1.0 if req.max_weight is None else float(req.max_weight)
    while i < req.n_samples:
        w = np.random.dirichlet(np.ones(n))
        if req.long_only and req.max_weight is not None and w.max() > maxw:
            continue
        ret = float(w @ mu_bl)
        vol = float(np.sqrt(max(w @ Sigma @ w, 0.0)))
        sharpe = (ret - req.rf) / (vol + 1e-12)
        weights_map = {req.assets[j]: float(w[j]) for j in range(n)}
        points.append(FrontierPoint(ret_annual=ret, vol_annual=vol, sharpe=sharpe, weights=weights_map))
        i += 1
    return FrontierDataResponse(points=points)
