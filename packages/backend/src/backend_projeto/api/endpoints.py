"""
This module defines the main FastAPI endpoints for the Investment API.

It consolidates routes for:
- System status and configuration.
- Data fetching (prices).
- Technical analysis (moving averages, MACD).
- Risk analysis (VaR, ES, drawdown, stress testing, backtesting, Monte Carlo, covariance, attribution).
- Portfolio optimization (Markowitz, Black-Litterman).
- Factor models (CAPM, APT, Fama-French).
- Various visualization endpoints (efficient frontier, TA plots, comprehensive charts).
"""
# endpoints.py
# Aqui serão definidos os endpoints da API (rotas)

import time
import logging
from datetime import datetime
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import io
from typing import Dict, Any, List, Optional
import pandas as pd

from src.backend_projeto.core.exceptions import DataProviderError

from src.backend_projeto.core.visualizations.factor_visualization import plot_ff_factors, plot_ff_betas # Moved to top

from .models import (
    PricesRequest, PricesResponse,
    VarRequest, EsRequest, DrawdownRequest, StressRequest, BacktestRequest,
    MonteCarloRequest, MonteCarloSamplesRequest, RiskResponse, AttributionRequest, CompareRequest, # Added MonteCarloSamplesRequest
    OptimizeRequest, BLRequest, CAPMRequest, APTRequest, FrontierRequest, BLFrontierRequest, # Added BLFrontierRequest
    TAMovingAveragesRequest, TAMacdRequest,
    IVaRRequest, MVaRRequest, RelVaRRequest,
    TAPlotRequest,
    FF3Request,
    FF5Request,
    FFFactorsPlotRequest,
    FFBetaPlotRequest,
    WeightsSeriesRequest, WeightsSeriesResponse,
    DrawdownSeriesRequest, TimeSeriesResponse,
    FrontierDataResponse, FrontierPoint, # Added FrontierDataResponse, FrontierPoint
    ComprehensiveChartsRequest, ComprehensiveChartsResponse,
)
from .deps import get_loader, get_risk_engine, get_optimization_engine, get_montecarlo_engine, get_config
from backend_projeto.core.data_handling import YFinanceProvider
from backend_projeto.core.analysis import RiskEngine, incremental_var, marginal_var, relative_var, compute_returns, portfolio_returns, ff3_metrics, ff5_metrics
from backend_projeto.core.optimization import OptimizationEngine
from backend_projeto.core.simulation import MonteCarloEngine
from backend_projeto.core.visualizations.visualization import efficient_frontier_image
from backend_projeto.core.technical_analysis import moving_averages, macd
from backend_projeto.core.visualizations.ta_visualization import plot_price_with_ma, plot_macd, plot_combined_ta
from backend_projeto.core.visualizations.comprehensive_visualization import ComprehensiveVisualizer
from backend_projeto.utils.config import Settings

router = APIRouter(
    tags=["Investment API"],
    responses={404: {"description": "Not found"}},
)

def _normalize_benchmark_alias(benchmark: Optional[str]) -> str:
    """
    Helper function to normalize common benchmark aliases to concrete tickers.

    Args:
        benchmark (Optional[str]): The input benchmark string, which might be an alias.

    Returns:
        str: The normalized benchmark ticker.
    """
    alias_raw = (benchmark or '')
    alias = alias_raw.strip().lower()
    normalized = alias.replace(' ', '').replace('-', '').replace('_', '').replace('&', 'and')
    alias_map = {
        # S&P 500
        'sp500': '^GSPC',
        'sandp500': '^GSPC',
        'snp500': '^GSPC',
        '^gspc': '^GSPC',
        'spy': 'SPY',
        # MSCI World
        'msciworld': 'URTH',
        'msciworldindex': 'URTH',
        'msciworldetf': 'URTH',
        'urth': 'URTH',
        'acwi': 'ACWI',
    }
    return alias_map.get(normalized, benchmark)

# Helper: convert BRL-priced assets to USD using USDBRL FX
def _convert_prices_to_usd(prices_df: pd.DataFrame, assets: List[str], start_date: str, end_date: str, loader: YFinanceProvider) -> pd.DataFrame:
    """
    Helper function to convert BRL-priced assets to USD using USDBRL exchange rates.

    Args:
        prices_df (pd.DataFrame): DataFrame of asset prices, potentially including BRL assets.
        assets (List[str]): List of asset tickers.
        start_date (str): Start date for fetching exchange rates.
        end_date (str): End date for fetching exchange rates.
        loader (YFinanceProvider): Data loader to fetch asset info and exchange rates.

    Returns:
        pd.DataFrame: DataFrame with BRL-priced assets converted to USD.
    """
    try:
        # Descobrir moedas dos ativos
        asset_currencies = loader.provider.fetch_asset_info(assets)
    except Exception:
        asset_currencies = {a: ('BRL' if a.upper().endswith('.SA') else 'USD') for a in assets}
    brl_assets = [a for a in assets if asset_currencies.get(a, 'USD').upper() == 'BRL' and a in prices_df.columns]
    if not brl_assets:
        return prices_df
    # Buscar USDBRL e converter BRL -> USD
    fx = loader.fetch_exchange_rates(['USD'], start_date, end_date)  # coluna 'USD' = USDBRL
    fx = fx['USD'].reindex(prices_df.index).ffill().bfill()
    prices_conv = prices_df.copy()
    prices_conv[brl_assets] = prices_conv[brl_assets].div(fx, axis=0)
    return prices_conv

@router.get("/status", tags=["System"])
def status() -> Dict[str, str]:
    """
    Checks if the API is online and operational.

    Returns:
        Dict[str, str]: A dictionary with a "status" key, indicating "ok" if the API is running.
    """
    return {"status": "ok"}


@router.get("/config", tags=["System"])
def get_public_config(config: Settings = Depends(get_config)) -> Dict[str, Any]:
    """
    Returns public configuration settings of the API.

    Args:
        config (Settings): Dependency injection for application settings.

    Returns:
        Dict[str, Any]: A dictionary containing public configuration parameters.
    """
    return config.to_dict()


@router.options("/prices", status_code=200, tags=["Data"])
def options_prices() -> Dict[str, Any]:
    """
    Handles OPTIONS requests for the /prices endpoint.

    This endpoint is typically used by browsers for preflight requests in CORS.

    Returns:
        Dict[str, Any]: An empty dictionary, sufficient for preflight requests.
    """
    return {} # Empty response is sufficient for preflight


@router.post("/prices", response_model=PricesResponse, tags=["Data"])
def get_prices(payload: PricesRequest, loader: YFinanceProvider = Depends(get_loader)) -> PricesResponse:
    """
    Returns historical prices for the specified assets.

    Args:
        payload (PricesRequest): Request body containing asset tickers, start date, and end date.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        PricesResponse: A Pydantic model containing the historical price data.
    """
    df = loader.fetch_stock_prices(payload.assets, payload.start_date, payload.end_date)
    df = df.sort_index()
    return PricesResponse(
        columns=[str(c) for c in df.columns],
        index=[idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx) for idx in df.index],
        data=df.values.tolist(),
    )


# Technical Analysis: Moving Averages
@router.post("/ta/moving-averages", response_model=PricesResponse, tags=["Technical Analysis"])
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


# Technical Analysis: MACD
@router.post("/ta/macd", response_model=PricesResponse, tags=["Technical Analysis"])
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


# Fronteira eficiente (imagem PNG)
@router.post("/plots/efficient-frontier", tags=["Visualization"])
def plot_efficient_frontier(
    req: FrontierRequest,
    loader: YFinanceProvider = Depends(get_loader),
    config: Settings = Depends(get_config)
) -> StreamingResponse:
    """
    Generates a PNG image of the Markowitz efficient frontier.

    Args:
        req (FrontierRequest): Request body containing assets, start date, end date,
                               number of samples, long-only constraint, max weight, and risk-free rate.
        loader (YFinanceProvider): Dependency injection for the data loader.
        config (Settings): Dependency injection for application settings.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the efficient frontier.
    """
    img_bytes = efficient_frontier_image(
        loader=loader,
        config=config,
        assets=req.assets,
        start_date=req.start_date,
        end_date=req.end_date,
        n_samples=req.n_samples,
        long_only=req.long_only,
        max_weight=req.max_weight,
        rf=req.rf,
    )
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")


# New: weights series (buy-and-hold constant weights over time)
@router.post("/portfolio/weights-series", response_model=WeightsSeriesResponse, tags=["Portfolio"])
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


# New: drawdown underwater series for the portfolio
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


# New: Markowitz efficient frontier data (points)
@router.post("/opt/markowitz/frontier-data", response_model=FrontierDataResponse, tags=["Optimization"])
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


# New: Black-Litterman frontier data using BL expected returns
@router.post("/opt/blacklitterman/frontier-data", response_model=FrontierDataResponse, tags=["Optimization"])
def bl_frontier_data(
    req: BLFrontierRequest,
    loader: YFinanceProvider = Depends(get_loader),
    config: Settings = Depends(get_config),
) -> FrontierDataResponse:
    """
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


# New: Monte Carlo distribution data (samples or histogram)
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


# Fama-French 3 Factors (monthly)
@router.post("/factors/ff3", response_model=RiskResponse, tags=["Factor Models"])
def factors_ff3(req: FF3Request, loader: YFinanceProvider = Depends(get_loader)) -> RiskResponse:
    """
    Calculates Fama-French 3-factor metrics (monthly) with selectable risk-free rate.

    Args:
        req (FF3Request): Request body containing assets, start date, end date,
                          and the source for the risk-free rate ('ff', 'selic', or 'us10y').
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        RiskResponse: A Pydantic model containing the Fama-French 3-factor analysis results.

    Raises:
        HTTPException: 422 if an insufficient number of observations for regression is found.
    """
    # Preços diários dos ativos
    prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
    # Fatores US mensais (MKT_RF, SMB, HML, RF)
    ff3 = loader.fetch_ff3_us_monthly(req.start_date, req.end_date)
    # RF mensal
    if req.rf_source == 'ff':
        rf_m = ff3['RF']
    elif req.rf_source == 'selic':
        rf_m = loader.compute_monthly_rf_from_cdi(req.start_date, req.end_date)
    else:
        # US10Y anual (%) -> aproximar taxa mensal (decimal)
        us10y = loader.fetch_us10y_monthly_yield(req.start_date, req.end_date)  # percent annual
        rf_m = ((1.0 + (us10y / 100.0)) ** (1.0 / 12.0) - 1.0)
        rf_m.name = 'RF'
    # Combinar fatores (usar MKT_RF, SMB, HML) e RF escolhido
    factors = ff3[['MKT_RF', 'SMB', 'HML']]
    result = ff3_metrics(prices, factors, rf_m, req.assets)
    result['rf_source'] = req.rf_source
    if req.rf_source != 'ff':
        result['notes'] = "RF diferente do RF dos fatores FF; interpretabilidade de alpha pode ser afetada."
    # Validação de amostra mínima: exigir pelo menos 5 observações em pelo menos um ativo
    res_map = result.get('results', {})
    if not res_map:
        raise HTTPException(status_code=422, detail="FF3: insuficiente número de observações para regressão (nenhum ativo com dados suficientes)")
    insuf = [a for a, d in res_map.items() if d.get('n_obs', 0) < 5]
    if len(insuf) == len(res_map):
        raise HTTPException(status_code=422, detail="FF3: todos os ativos possuem menos de 5 observações")
    if insuf:
        result['warnings'] = {"min_obs": 5, "insufficient_assets": insuf}
    return RiskResponse(result=result)


# Fama-French 5 Factors (monthly)
@router.post("/factors/ff5", response_model=RiskResponse, tags=["Factor Models"])
def factors_ff5(req: FF5Request, loader: YFinanceProvider = Depends(get_loader)) -> RiskResponse:
    """
    Calculates Fama-French 5-factor metrics (monthly): MKT-RF, SMB, HML, RMW, CMA.

    Raises:
        HTTPException: 422 if an insufficient number of observations for regression is found.
    """
    prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
    ff5 = loader.fetch_ff5_us_monthly(req.start_date, req.end_date)
    if req.rf_source == 'ff':
        rf_m = ff5['RF']
    elif req.rf_source == 'selic':
        rf_m = loader.compute_monthly_rf_from_cdi(req.start_date, req.end_date)
    else:
        us10y = loader.fetch_us10y_monthly_yield(req.start_date, req.end_date)
        rf_m = ((1.0 + (us10y / 100.0)) ** (1.0 / 12.0) - 1.0)
        rf_m.name = 'RF'
    factors = ff5[['MKT_RF', 'SMB', 'HML', 'RMW', 'CMA']]
    result = ff5_metrics(prices, factors, rf_m, req.assets)
    result['rf_source'] = req.rf_source
    if req.rf_source != 'ff':
        result['notes'] = "RF diferente do RF dos fatores FF; interpretabilidade de alpha pode ser afetada."
    # Validação de amostra mínima (>=5 meses em pelo menos um ativo)
    res_map = result.get('results', {})
    if not res_map:
        raise HTTPException(status_code=422, detail="FF5: insuficiente número de observações para regressão (nenhum ativo com dados suficientes)")
    insuf = [a for a, d in res_map.items() if d.get('n_obs', 0) < 5]
    if len(insuf) == len(res_map):
        raise HTTPException(status_code=422, detail="FF5: todos os ativos possuem menos de 5 observações")
    if insuf:
        result['warnings'] = {"min_obs": 5, "insufficient_assets": insuf}
    return RiskResponse(result=result)


# Plots: Fama-French factors time series
@router.post("/plots/ff-factors", tags=["Visualization"])
def plot_ff_factors_endpoint(
    req: FFFactorsPlotRequest,
    loader: YFinanceProvider = Depends(get_loader),
) -> StreamingResponse:
    """
    Generates a plot of Fama-French factors time series.

    Args:
        req (FFFactorsPlotRequest): Request body containing the Fama-French model (FF3 or FF5),
                                    start date, and end date.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the Fama-French factors plot.
    """
    if req.model == 'ff3':
        ff = loader.fetch_ff3_us_monthly(req.start_date, req.end_date)
        factors = ff[['MKT_RF', 'SMB', 'HML']]
    else:
        ff = loader.fetch_ff5_us_monthly(req.start_date, req.end_date)
        factors = ff[['MKT_RF', 'SMB', 'HML', 'RMW', 'CMA']]
    img_bytes = plot_ff_factors(factors)
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")


# Plots: Betas de um ativo (FF3/FF5)
@router.post("/plots/ff-betas", tags=["Visualization"])
def plot_ff_betas_endpoint(
    req: FFBetaPlotRequest,
    loader: YFinanceProvider = Depends(get_loader),
) -> StreamingResponse:
    """
    Generates a plot of an asset's betas for Fama-French 3 or 5 factor models.

    Args:
        req (FFBetaPlotRequest): Request body containing the asset, Fama-French model (FF3 or FF5),
                                 start date, end date, and risk-free rate source.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the Fama-French betas plot.
    """
    # Baixar preços e fatores conforme modelo
    prices = loader.fetch_stock_prices([req.asset], req.start_date, req.end_date)
    if getattr(req, 'convert_to_usd', False):
        prices = _convert_prices_to_usd(prices, [req.asset], req.start_date, req.end_date, loader)
    if req.model == 'ff3':
        ff = loader.fetch_ff3_us_monthly(req.start_date, req.end_date)
        factors = ff[['MKT_RF', 'SMB', 'HML']]
        model = 'FF3'
    else:
        ff = loader.fetch_ff5_us_monthly(req.start_date, req.end_date)
        factors = ff[['MKT_RF', 'SMB', 'HML', 'RMW', 'CMA']]
        model = 'FF5'
    # RF
    if req.rf_source == 'ff':
        rf_m = ff['RF']
    elif req.rf_source == 'selic':
        rf_m = loader.compute_monthly_rf_from_cdi(req.start_date, req.end_date)
    else:
        us10y = loader.fetch_us10y_monthly_yield(req.start_date, req.end_date)
        rf_m = ((1.0 + (us10y / 100.0)) ** (1.0 / 12.0) - 1.0)
        rf_m.name = 'RF'
    # Calcular métricas
    if model == 'FF3':
        from backend_projeto.core.analysis import ff3_metrics
        res = ff3_metrics(prices, factors, rf_m, [req.asset])
        betas = res['results'].get(req.asset, {})
    else:
        from backend_projeto.core.analysis import ff5_metrics
        res = ff5_metrics(prices, factors, rf_m, [req.asset])
        betas = res['results'].get(req.asset, {})
    img_bytes = plot_ff_betas(betas, model=model, title=f"{req.asset} - {model} Betas")
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")


# Otimização Markowitz
@router.post("/opt/markowitz", response_model=RiskResponse, tags=["Optimization"])
def opt_markowitz(req: OptimizeRequest, opt: OptimizationEngine = Depends(get_optimization_engine)) -> RiskResponse:
    """
    Performs Markowitz portfolio optimization (max Sharpe, min variance, max return).

    Args:
        req (OptimizeRequest): Request body containing assets, start date, end date,
                               objective, optional bounds, long-only constraint, and max weight.
        opt (OptimizationEngine): Dependency injection for the optimization engine.

    Returns:
        RiskResponse: A Pydantic model containing the optimization results.
    """
    result = opt.optimize_markowitz(req.assets, req.start_date, req.end_date, req.objective, req.bounds, req.long_only, req.max_weight)
    return RiskResponse(result=result)


# CAPM
@router.post("/factors/capm", response_model=RiskResponse, tags=["Factor Models"])
def factors_capm(req: CAPMRequest, opt: OptimizationEngine = Depends(get_optimization_engine)) -> RiskResponse:
    """
    Calculates CAPM metrics (beta, alpha, Sharpe) against a benchmark.

    Args:
        req (CAPMRequest): Request body containing assets, start date, end date, and benchmark ticker.
        opt (OptimizationEngine): Dependency injection for the optimization engine.

    Returns:
        RiskResponse: A Pydantic model containing the CAPM metrics.
    """
    resolved_bench = _normalize_benchmark_alias(req.benchmark)
    result = opt.capm_metrics(req.assets, req.start_date, req.end_date, resolved_bench)
    return RiskResponse(result=result)


# APT
@router.post("/factors/apt", response_model=RiskResponse, tags=["Factor Models"])
def factors_apt(req: APTRequest, opt: OptimizationEngine = Depends(get_optimization_engine)) -> RiskResponse:
    """
    Performs Arbitrage Pricing Theory (APT) - multifactor regression.

    Args:
        req (APTRequest): Request body containing assets, start date, end date, and a list of factors.
        opt (OptimizationEngine): Dependency injection for the optimization engine.

    Returns:
        RiskResponse: A Pydantic model containing the APT metrics.
    """
    result = opt.apt_metrics(req.assets, req.start_date, req.end_date, req.factors)
    return RiskResponse(result=result)


# Black-Litterman
@router.post("/opt/blacklitterman", response_model=RiskResponse, tags=["Optimization"])
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


# Technical Analysis Plot
@router.post("/plots/ta", tags=["Visualization"])
def plot_technical_analysis(
    req: TAPlotRequest,
    loader: YFinanceProvider = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates a PNG image of technical analysis charts (prices + MAs + MACD).

    Args:
        req (TAPlotRequest): Request body containing asset, start date, end date,
                             plot type ('ma', 'macd', or 'combined'), and TA parameters.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the technical analysis plot.
    """
    prices = loader.fetch_stock_prices([req.asset], req.start_date, req.end_date)
    
    if req.plot_type == 'ma':
        img_bytes = plot_price_with_ma(
            prices, req.asset, windows=req.ma_windows, method=req.ma_method
        )
    elif req.plot_type == 'macd':
        img_bytes = plot_macd(
            prices, req.asset, fast=req.macd_fast, slow=req.macd_slow, signal=req.macd_signal
        )
    else:  # combined
        img_bytes = plot_combined_ta(
            prices, req.asset,
            ma_windows=req.ma_windows, ma_method=req.ma_method,
            macd_fast=req.macd_fast, macd_slow=req.macd_slow, macd_signal=req.macd_signal
        )

    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")


# Comprehensive Charts Generation
@router.post("/plots/comprehensive", response_model=ComprehensiveChartsResponse, tags=["Visualization"])
def generate_comprehensive_charts(
    req: ComprehensiveChartsRequest,
    loader: YFinanceProvider = Depends(get_loader),
    config: Settings = Depends(get_config)
) -> ComprehensiveChartsResponse:
    """
    Generates all available types of charts and saves them as PNG files.

    This functionality combines:
    - Technical analysis (moving averages, MACD)
    - Fama-French factors (FF3/FF5) and betas
    - Efficient frontier

    Args:
        req (ComprehensiveChartsRequest): Configuration for chart generation.
        loader (YFinanceProvider): YFinanceProvider to fetch financial data.
        config (Settings): Application settings.

    Returns:
        ComprehensiveChartsResponse: A response containing paths to the generated files and a summary.

    Raises:
        HTTPException: 422 for invalid input data,
                       500 for internal errors during chart generation,
                       503 if data fetching fails.
    """
    try:
        # Log da requisição
        logging.info(f"Gerando gráficos abrangentes para {len(req.assets)} ativos: {req.assets}")

        # Validar período de dados
        if req.start_date >= req.end_date:
            raise HTTPException(
                status_code=422,
                detail="start_date deve ser anterior a end_date"
            )

        # Inicializar visualizador
        visualizer = ComprehensiveVisualizer(config=config, output_dir=req.output_dir)

        # Preparar configurações de gráficos com validação
        plot_configs = req.plot_configs or {}

        # Validar configurações específicas
        for chart_type in req.chart_types:
            if chart_type == 'technical_analysis':
                ta_config = plot_configs.get('technical_analysis', {})
                ma_windows = ta_config.get('ma_windows', [5, 21])
                if not all(isinstance(w, int) and w > 0 for w in ma_windows):
                    raise HTTPException(
                        status_code=422,
                        detail="ma_windows deve conter apenas números inteiros positivos"
                    )

            elif chart_type == 'efficient_frontier':
                ef_config = plot_configs.get('efficient_frontier', {})
                n_samples = ef_config.get('n_samples', 5000)
                if not isinstance(n_samples, int) or n_samples < 100:
                    raise HTTPException(
                        status_code=422,
                        detail="n_samples deve ser um número inteiro >= 100"
                    )

        # Gerar gráficos com timeout implícito
        generated_files = visualizer.generate_all_charts(
            assets=req.assets,
            start_date=req.start_date,
            end_date=req.end_date,
            loader=loader,
            plot_configs=plot_configs
        )

        # Verificar se pelo menos alguns gráficos foram gerados
        if not generated_files:
            logging.warning("Nenhum gráfico foi gerado - pode indicar problema com os dados")
            # Não é erro fatal, apenas warning

        # Preparar resposta detalhada
        summary = {
            "total_files": len(generated_files),
            "assets_processed": len(req.assets),
            "chart_types": req.chart_types,
            "output_directory": req.output_dir,
            "date_range": f"{req.start_date} to {req.end_date}",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }

        # Log de sucesso
        logging.info(f"Gráficos gerados com sucesso: {len(generated_files)} arquivos em {req.output_dir}")

        return ComprehensiveChartsResponse(
            generated_files=generated_files,
            summary=summary
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except DataProviderError as e:
        logging.error(f"Erro ao buscar dados para gráficos abrangentes: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Erro ao buscar dados",
                "message": str(e),
                "suggestion": "Verifique a disponibilidade dos dados e sua conexão com a internet."
            }
        )
    except ValueError as e:
        logging.error(f"Erro de validação ou processamento de dados para gráficos abrangentes: {e}", exc_info=True)
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Erro nos dados fornecidos ou processamento",
                "message": str(e),
                "suggestion": "Verifique os parâmetros de entrada (ativos, datas, etc.) e tente novamente."
            }
        )
    except Exception as e:
        # Log detalhado do erro
        logging.error(f"Erro interno na geração de gráficos: {e}", exc_info=True)

        # Retornar erro HTTP apropriado
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Erro interno na geração de gráficos",
                "message": str(e),
                "suggestion": "Verifique os parâmetros e tente novamente. Se o problema persistir, contate o suporte."
            }
        )