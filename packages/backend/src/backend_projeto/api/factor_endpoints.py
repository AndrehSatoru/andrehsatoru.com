"""
This module defines FastAPI endpoints for various factor models in financial analysis.

It provides routes for calculating metrics based on:
- Fama-French 3-Factor Model
- Fama-French 5-Factor Model
- Capital Asset Pricing Model (CAPM)
- Arbitrage Pricing Theory (APT)
"""
# src/backend_projeto/api/factor_endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from backend_projeto.domain.models import (
    FF3Request, FF5Request, CAPMRequest, APTRequest, RiskResponse
)
from .deps import get_loader, get_optimization_engine
from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.domain.optimization import OptimizationEngine
from backend_projeto.domain.analysis import ff3_metrics, ff5_metrics
from .helpers import _normalize_benchmark_alias

router = APIRouter(
    tags=["Factor Models"],
    responses={404: {"description": "Not found"}},
)

# Fama-French 3 Factors (monthly)
@router.post("/factors/ff3", response_model=RiskResponse)
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
@router.post("/factors/ff5", response_model=RiskResponse)
def factors_ff5(req: FF5Request, loader: YFinanceProvider = Depends(get_loader)) -> RiskResponse:
    """
    Calculates Fama-French 5-factor metrics (monthly): MKT-RF, SMB, HML, RMW, CMA.

    Risk-free rate is selectable: SELIC (default) or US10Y.

    Args:
        req (FF5Request): Request body containing assets, start date, end date,
                          and the source for the risk-free rate ('ff', 'selic', or 'us10y').
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        RiskResponse: A Pydantic model containing the Fama-French 5-factor analysis results.

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
    return RiskResponse(result=result)# CAPM
@router.post("/factors/capm", response_model=RiskResponse)
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
@router.post("/factors/apt", response_model=RiskResponse)
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
