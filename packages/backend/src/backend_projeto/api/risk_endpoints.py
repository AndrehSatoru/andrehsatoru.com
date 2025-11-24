"""
This module defines FastAPI endpoints for various risk analysis functionalities.

It provides routes for calculating:
- Value at Risk (VaR) and Expected Shortfall (ES).
- Incremental VaR (IVaR), Marginal VaR (MVaR), and Relative VaR.
- Maximum Drawdown and Drawdown Series.
- Stress Testing and VaR Backtesting.
- Monte Carlo simulations and their distributions.
- Covariance matrices and Risk Attribution.
"""
# src/backend_projeto/api/risk_endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from backend_projeto.domain.models import (
    VarRequest, EsRequest, DrawdownRequest, StressRequest, BacktestRequest,
    MonteCarloRequest, RiskResponse, AttributionRequest, CompareRequest,
    IVaRRequest, MVaRRequest, RelVaRRequest, PricesRequest, TimeSeriesResponse,
    DrawdownSeriesRequest, MonteCarloSamplesRequest
)
from .deps import get_loader, get_risk_engine, get_montecarlo_engine, get_config
from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.domain.analysis import RiskEngine, incremental_var, marginal_var, relative_var, compute_returns, portfolio_returns
from backend_projeto.domain.simulation import MonteCarloEngine
from backend_projeto.domain.exceptions import DataProviderError
from .helpers import _normalize_benchmark_alias
from backend_projeto.infrastructure.utils.config import Settings
import logging

router = APIRouter(
    tags=["Risk"],
    responses={404: {"description": "Not found"}},
)

# Risk: IVaR
@router.post("/risk/ivar", response_model=RiskResponse, tags=["Risk - Advanced"])
def risk_ivar(req: IVaRRequest, loader: YFinanceProvider = Depends(get_loader)) -> RiskResponse:
    """
    Calculates Incremental VaR (IVaR) - the sensitivity of VaR to changes in portfolio weights.

    Args:
        req (IVaRRequest): Request body containing assets, start date, end date,
                           alpha, VaR method, EWMA lambda, and delta for incremental change.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        RiskResponse: A Pydantic model containing the IVaR calculation results.
    """
    prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
    rets = compute_returns(prices)
    weights = req.weights if req.weights is not None else [1.0/len(req.assets)]*len(req.assets)
    result = incremental_var(rets, req.assets, weights, alpha=req.alpha, method=req.method, ewma_lambda=req.ewma_lambda, delta=req.delta)
    return RiskResponse(result=result)


# Risk: MVaR
@router.post("/risk/mvar", response_model=RiskResponse, tags=["Risk - Advanced"])
def risk_mvar(req: MVaRRequest, loader: YFinanceProvider = Depends(get_loader)) -> RiskResponse:
    """
    Calculates Marginal VaR (MVaR) - the impact of removing each asset from the portfolio.

    Args:
        req (MVaRRequest): Request body containing assets, start date, end date,
                           alpha, VaR method, and EWMA lambda.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        RiskResponse: A Pydantic model containing the MVaR calculation results.
    """
    prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
    rets = compute_returns(prices)
    weights = req.weights if req.weights is not None else [1.0/len(req.assets)]*len(req.assets)
    result = marginal_var(rets, req.assets, weights, alpha=req.alpha, method=req.method, ewma_lambda=req.ewma_lambda)
    return RiskResponse(result=result)


# Risk: Relative VaR
@router.post("/risk/relvar", response_model=RiskResponse, tags=["Risk - Advanced"])
def risk_relative_var(req: RelVaRRequest, loader: YFinanceProvider = Depends(get_loader)) -> RiskResponse:
    """
    Calculates Relative VaR - the risk of underperformance against a benchmark.

    Args:
        req (RelVaRRequest): Request body containing assets, start date, end date,
                             benchmark, alpha, VaR method, and EWMA lambda.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        RiskResponse: A Pydantic model containing the Relative VaR calculation results.

    Raises:
        HTTPException: 422 if the benchmark is not available or has no data.
    """
    # carteira
    prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
    weights = req.weights if req.weights is not None else [1.0/len(req.assets)]*len(req.assets)
    port_rets = portfolio_returns(compute_returns(prices), req.assets, weights)
    # benchmark
    resolved_bench = _normalize_benchmark_alias(req.benchmark)
    bench_series = loader.fetch_benchmark_data(resolved_bench, req.start_date, req.end_date)
    if bench_series is None:
        raise HTTPException(status_code=422, detail=f"Benchmark '{req.benchmark}' não disponível ou sem dados no período")
    bench_rets = bench_series.sort_index().pct_change().dropna()
    result = relative_var(port_rets, bench_rets, alpha=req.alpha, method=req.method, ewma_lambda=req.ewma_lambda)
    return RiskResponse(result=result)

# Risco: VaR
@router.post("/risk/var", response_model=RiskResponse, tags=["Risk - Core"])
def risk_var(req: VarRequest, engine: RiskEngine = Depends(get_risk_engine)) -> RiskResponse:
    """
    Calculates Value at Risk (VaR) - a metric for the maximum expected loss.

    Args:
        req (VarRequest): Request body containing assets, start date, end date,
                          alpha, VaR method, EWMA lambda, and optional weights.
        engine (RiskEngine): Dependency injection for the risk engine.

    Returns:
        RiskResponse: A Pydantic model containing the VaR calculation results.
    """
    weights = req.weights if req.weights is not None else [1.0/len(req.assets)]*len(req.assets)
    result = engine.compute_var(req.assets, req.start_date, req.end_date, req.alpha, req.method, req.ewma_lambda, weights)
    return RiskResponse(result=result)


# Risco: ES
@router.post("/risk/es", response_model=RiskResponse, tags=["Risk - Core"])
def risk_es(req: EsRequest, engine: RiskEngine = Depends(get_risk_engine)) -> RiskResponse:
    """
    Calculates Expected Shortfall (ES/CVaR) - the average loss beyond VaR.

    Args:
        req (EsRequest): Request body containing assets, start date, end date,
                         alpha, ES method, EWMA lambda, and optional weights.
        engine (RiskEngine): Dependency injection for the risk engine.

    Returns:
        RiskResponse: A Pydantic model containing the ES calculation results.
    """
    weights = req.weights if req.weights is not None else [1.0/len(req.assets)]*len(req.assets)
    result = engine.compute_es(req.assets, req.start_date, req.end_date, req.alpha, req.method, req.ewma_lambda, weights)
    return RiskResponse(result=result)


# Risco: Drawdown
@router.post("/risk/drawdown", response_model=RiskResponse, tags=["Risk - Core"])
def risk_drawdown(req: DrawdownRequest, engine: RiskEngine = Depends(get_risk_engine)) -> RiskResponse:
    """
    Calculates Maximum Drawdown - the largest peak-to-trough decline in a portfolio.

    Args:
        req (DrawdownRequest): Request body containing assets, start date, end date, and optional weights.
        engine (RiskEngine): Dependency injection for the risk engine.

    Returns:
        RiskResponse: A Pydantic model containing the drawdown calculation results.
    """
    weights = req.weights if req.weights is not None else [1.0/len(req.assets)]*len(req.assets)
    result = engine.compute_drawdown(req.assets, req.start_date, req.end_date, weights)
    return RiskResponse(result=result)


# Risco: Stress Testing
@router.post("/risk/stress", response_model=RiskResponse, tags=["Risk - Scenario"])
def risk_stress(req: StressRequest, engine: RiskEngine = Depends(get_risk_engine)) -> RiskResponse:
    """
    Simulates a stress scenario by applying a shock to asset returns.

    Args:
        req (StressRequest): Request body containing assets, start date, end date,
                             optional weights, and the percentage shock to apply.
        engine (RiskEngine): Dependency injection for the risk engine.

    Returns:
        RiskResponse: A Pydantic model containing the stress test results.
    """
    weights = req.weights if req.weights is not None else [1.0/len(req.assets)]*len(req.assets)
    result = engine.compute_stress(req.assets, req.start_date, req.end_date, weights, req.shock_pct)
    return RiskResponse(result=result)


# Backtesting do VaR
@router.post("/risk/backtest", response_model=RiskResponse, tags=["Risk - Validation"])
def risk_backtest(req: BacktestRequest, engine: RiskEngine = Depends(get_risk_engine)) -> RiskResponse:
    """
    Performs VaR backtesting using Kupiec, Christoffersen tests, and Basel zones.

    Args:
        req (BacktestRequest): Request body containing assets, start date, end date,
                               alpha, VaR method, EWMA lambda, and optional weights.
        engine (RiskEngine): Dependency injection for the risk engine.

    Returns:
        RiskResponse: A Pydantic model containing the backtesting results.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if validation or processing errors occur,
                       500 for unexpected internal errors.
    """
    weights = req.weights if req.weights is not None else [1.0/len(req.assets)]*len(req.assets)
    try:
        result = engine.backtest(req.assets, req.start_date, req.end_date, req.alpha, req.method, req.ewma_lambda, weights)
        return RiskResponse(result=result)
    except DataProviderError as e:
        logging.error(f"Erro ao buscar dados para backtest: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados para backtest: {str(e)}")
    except ValueError as e:
        logging.error(f"Erro de validação ou processamento no backtest: {e}", exc_info=True)
        raise HTTPException(status_code=422, detail=f"Erro de validação ou processamento no backtest: {str(e)}")
    except Exception as e:
        logging.error(f"Erro inesperado no backtest: {e}", exc_info=True)
        minimal = {"n": 0, "exceptions": 0, "basel_zone": "red", "note": f"Erro inesperado: {e}"}
        return RiskResponse(result=minimal)


# Monte Carlo (GBM)
@router.post("/risk/montecarlo", response_model=RiskResponse, tags=["Risk - Simulation"])
def risk_montecarlo(req: MonteCarloRequest, mc: MonteCarloEngine = Depends(get_montecarlo_engine)) -> RiskResponse:
    """
    Performs Monte Carlo simulation using Geometric Brownian Motion (GBM).

    Args:
        req (MonteCarloRequest): Request body containing assets, start date, end date,
                                 optional weights, number of paths, number of days,
                                 volatility method, EWMA lambda, and random seed.
        mc (MonteCarloEngine): Dependency injection for the Monte Carlo engine.

    Returns:
        RiskResponse: A Pydantic model containing the Monte Carlo simulation results.
    """
    weights = req.weights if req.weights is not None else [1.0/len(req.assets)]*len(req.assets)
    result = mc.simulate_gbm(req.assets, req.start_date, req.end_date, weights, req.n_paths, req.n_days, req.vol_method, req.ewma_lambda, req.seed)
    return RiskResponse(result=result)


# Covariância (Ledoit-Wolf)
@router.post("/risk/covariance", response_model=RiskResponse, tags=["Risk - Analytics"])
def risk_covariance(req: PricesRequest, engine: RiskEngine = Depends(get_risk_engine)) -> RiskResponse:
    """
    Calculates the covariance matrix with Ledoit-Wolf shrinkage.

    Args:
        req (PricesRequest): Request body containing assets, start date, and end date.
        engine (RiskEngine): Dependency injection for the risk engine.

    Returns:
        RiskResponse: A Pydantic model containing the covariance matrix calculation results.
    """
    result = engine.compute_covariance(req.assets, req.start_date, req.end_date)
    return RiskResponse(result=result)


# Atribuição de risco
@router.post("/risk/attribution", response_model=RiskResponse, tags=["Risk - Analytics"])
def risk_attribution(req: AttributionRequest, engine: RiskEngine = Depends(get_risk_engine)) -> RiskResponse:
    """
    Performs risk attribution by asset (contribution to volatility and VaR).

    Args:
        req (AttributionRequest): Request body containing assets, start date, end date,
                                  optional weights, attribution method, and EWMA lambda.
        engine (RiskEngine): Dependency injection for the risk engine.

    Returns:
        RiskResponse: A Pydantic model containing the risk attribution results.
    """
    weights = req.weights if req.weights is not None else [1.0/len(req.assets)]*len(req.assets)
    result = engine.compute_attribution(req.assets, req.start_date, req.end_date, weights, req.method, req.ewma_lambda)
    return RiskResponse(result=result)


# Comparação entre métodos
@router.post("/risk/compare", response_model=RiskResponse, tags=["Risk - Validation"])
def risk_compare(req: CompareRequest, engine: RiskEngine = Depends(get_risk_engine)) -> RiskResponse:
    """
    Compares VaR and ES across different methods (historical, std, ewma, garch, evt).

    Args:
        req (CompareRequest): Request body containing assets, start date, end date,
                              alpha, a list of methods to compare, EWMA lambda, and optional weights.
        engine (RiskEngine): Dependency injection for the risk engine.

    Returns:
        RiskResponse: A Pydantic model containing the comparison results.
    """
    weights = req.weights if req.weights is not None else [1.0/len(req.assets)]*len(req.assets)
    result = engine.compare_methods(req.assets, req.start_date, req.end_date, req.alpha, req.methods, req.ewma_lambda, weights)
    return RiskResponse(result=result)

# drawdown underwater series for the portfolio
@router.post("/risk/drawdown-series", response_model=TimeSeriesResponse, tags=["Risk - Core"])
def risk_drawdown_series(
    req: DrawdownSeriesRequest,
    loader: YFinanceProvider = Depends(get_loader),
) -> TimeSeriesResponse:
    """
    Calculates and returns the drawdown series for a portfolio.

    Args:
        req (DrawdownSeriesRequest): Request body containing assets, start date, end date, and weights.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        TimeSeriesResponse: A Pydantic model containing the time series of drawdown values.
    """
    prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
    rets = compute_returns(prices)
    port = portfolio_returns(rets, req.assets, req.weights)
    equity = (1 + port.fillna(0.0)).cumprod()
    peak = equity.cummax()
    underwater = (equity / peak) - 1.0
    idx = [idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx) for idx in underwater.index]
    return TimeSeriesResponse(index=idx, data=[float(x) for x in underwater.values])

# Monte Carlo distribution data (samples or histogram)
@router.post("/risk/montecarlo/distribution", response_model=RiskResponse, tags=["Risk - Simulation"])
def risk_montecarlo_distribution(
    req: MonteCarloSamplesRequest,
    loader: YFinanceProvider = Depends(get_loader),
    config: Settings = Depends(get_config),
) -> RiskResponse:
    """
    Generates Monte Carlo simulation distribution data (samples or histogram).

    Args:
        req (MonteCarloSamplesRequest): Request body containing assets, start date, end date,
                                        weights, volatility method, EWMA lambda, random seed,
                                        return type ('samples' or 'histogram'), and number of bins.
        loader (YFinanceProvider): Dependency injection for the data loader.
        config (Settings): Dependency injection for application settings.

    Returns:
        RiskResponse: A Pydantic model containing the Monte Carlo distribution data.

    Raises:
        HTTPException: 422 if an invalid volatility method is specified.
    """
    import numpy as np
    prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
    rets = compute_returns(prices)
    port = portfolio_returns(rets, req.assets, req.weights)
    mu = float(port.mean())
    if req.vol_method == 'std':
        sigma = float(port.std(ddof=1))
    elif req.vol_method == 'ewma':
        x = port.fillna(0.0).values
        var = np.var(x)
        lam = req.ewma_lambda
        for xi in x:
            var = lam * var + (1 - lam) * (xi ** 2)
        sigma = float(np.sqrt(var))
    else:
        raise HTTPException(status_code=422, detail="vol_method deve ser std|ewma")
    if req.seed is not None:
        np.random.seed(req.seed)
    dt = 1.0 / config.DIAS_UTEIS_ANO
    shocks = np.random.normal((mu - 0.5 * sigma ** 2) * dt, sigma * np.sqrt(dt), size=(req.n_days, req.n_paths))
    prices_paths = np.exp(np.cumsum(shocks, axis=0))
    terminal = prices_paths[-1, :]
    pnl = terminal - 1.0
    out: Dict[str, Any] = {
        "params": {"mu": mu, "sigma": sigma, "vol_method": req.vol_method},
        "confidence": config.VAR_CONFIDENCE_LEVEL,
        "n_paths": req.n_paths,
        "n_days": req.n_days,
        "quantiles": {"1%": float(np.quantile(pnl, 0.01)), "5%": float(np.quantile(pnl, 0.05)), "50%": float(np.quantile(pnl, 0.5)), "95%": float(np.quantile(pnl, 0.95)), "99%": float(np.quantile(pnl, 0.99))},
    }
    if req.return_type == 'samples':
        out["samples"] = pnl.tolist()
    else:
        counts, edges = np.histogram(pnl, bins=int(req.bins))
        out["histogram"] = {"bins": edges.tolist(), "counts": counts.tolist()}
    return RiskResponse(result=out)
