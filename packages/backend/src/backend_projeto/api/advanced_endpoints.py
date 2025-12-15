"""
This module defines FastAPI endpoints for advanced financial visualizations.

It includes routes for generating various static and interactive charts,
as well as comprehensive dashboards for portfolio analysis, risk, performance,
and Monte Carlo simulations.
"""
# api/advanced_endpoints.py
# Novos endpoints para visualizações avançadas

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
import io

from backend_projeto.domain.exceptions import DataProviderError

from backend_projeto.domain.models import (
    PricesRequest, RiskResponse,
    AdvancedChartRequest, DashboardRequest, InteractiveChartRequest, RollingBetaRequest, UnderwaterPlotRequest, SectorAnalysisRequest, MonteCarloDashboardRequest,
    AssetAllocationRequest, # Existing import
    CumulativePerformanceRequest, # Existing import
    RiskContributionRequest # New import
)
from .deps import get_loader, get_config, get_risk_engine
from backend_projeto.domain.analysis import calculate_rolling_beta, RiskEngine, compute_returns
from backend_projeto.domain.simulation import MonteCarloEngine
from backend_projeto.infrastructure.visualization.advanced_visualization import AdvancedVisualizer
from backend_projeto.infrastructure.visualization.interactive_visualization import InteractiveVisualizer
from backend_projeto.application.dashboard_generator import DashboardGenerator

router = APIRouter(
    tags=["Advanced Visualization"],
    responses={404: {"description": "Not found"}},
)

# ==================== GRÁFICOS AVANÇADOS ====================

@router.post("/plots/advanced/candlestick", tags=["Advanced Charts"])
def plot_advanced_candlestick(
    req: PricesRequest,
    loader: Any = Depends(get_loader),
    config: Any = Depends(get_config)
) -> StreamingResponse:
    """
    Generates an advanced candlestick chart with volume for a specified asset.

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        loader (Any): Dependency injection for data loader.
        config (Any): Dependency injection for configuration settings.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the candlestick chart.

    Raises:
        HTTPException: 422 if no asset is specified or data processing error,
                       503 if data fetching fails,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        visualizer = AdvancedVisualizer()
        
        # Gerar gráfico para o primeiro ativo
        asset = req.assets[0] if req.assets else None
        if not asset:
            raise HTTPException(status_code=422, detail="Pelo menos um ativo deve ser especificado")
        
        chart_bytes = visualizer.plot_candlestick(prices, asset) # Assuming visualizer has this method
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
        
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico: {str(e)}")

@router.post("/plots/advanced/price-comparison", tags=["Advanced Charts"])
def plot_price_comparison(
    req: PricesRequest,
    normalize: bool = True,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates a price comparison chart for multiple assets.

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        normalize (bool): If True, normalizes prices to start at 1. Defaults to True.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the price comparison chart.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_price_comparison(prices, req.assets, normalize)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
        
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar gráfico: {str(e)}")

@router.post("/plots/advanced/risk-metrics", tags=["Advanced Charts"])
def plot_risk_metrics(
    req: PricesRequest,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates a comparative risk metrics chart for multiple assets.

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the risk metrics chart.

    Raises:
        HTTPException: 500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_risk_metrics(returns, req.assets)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar gráfico: {str(e)}")

@router.post("/plots/advanced/correlation-heatmap", tags=["Advanced Charts"])
def plot_correlation_heatmap(
    req: PricesRequest,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates a correlation heatmap between multiple assets.

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the correlation heatmap.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_correlation_heatmap(returns, req.assets)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico: {str(e)}")

@router.post("/plots/advanced/return-distribution", tags=["Advanced Charts"])
def plot_return_distribution(
    req: PricesRequest,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates a return distribution chart for multiple assets.

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the return distribution chart.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_return_distribution(returns, req.assets)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico: {str(e)}")

@router.post("/plots/advanced/qq-plot", tags=["Advanced Charts"])
def plot_qq_plot(
    req: PricesRequest,
    asset: str,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates a Q-Q plot to check for normality of asset returns.

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        asset (str): The specific asset ticker for which to generate the Q-Q plot.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the Q-Q plot.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices([asset], req.start_date, req.end_date)
        returns = prices[asset].pct_change().dropna()
        
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_qq_plot(returns, asset)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico: {str(e)}")
    try:
        prices = loader.fetch_stock_prices([asset], req.start_date, req.end_date)
        returns = prices[asset].pct_change().dropna()
        
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_qq_plot(returns, asset)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico: {str(e)}")

@router.post("/plots/advanced/performance-metrics", tags=["Advanced Charts"])
def plot_performance_metrics(
    req: PricesRequest,
    benchmark: Optional[str] = None,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates a comparative performance metrics chart for assets, optionally against a benchmark.

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        benchmark (Optional[str]): Ticker of the benchmark asset. Defaults to None.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the performance metrics chart.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        benchmark_series = None
        if benchmark:
            benchmark_prices = loader.fetch_stock_prices([benchmark], req.start_date, req.end_date)
            benchmark_series = benchmark_prices[benchmark].pct_change().dropna()
        
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_performance_metrics(returns, req.assets, benchmark_series)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico: {str(e)}")
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        benchmark_series = None
        if benchmark:
            benchmark_prices = loader.fetch_stock_prices([benchmark], req.start_date, req.end_date)
            benchmark_series = benchmark_prices[benchmark].pct_change().dropna()
        
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_performance_metrics(returns, req.assets, benchmark_series)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico: {str(e)}")

@router.post("/plots/advanced/efficient-frontier-advanced", tags=["Advanced Charts"])
def plot_efficient_frontier_advanced(
    req: PricesRequest,
    n_portfolios: int = 1000,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates an advanced efficient frontier chart.

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        n_portfolios (int): Number of random portfolios to simulate for the efficient frontier. Defaults to 1000.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the efficient frontier chart.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_efficient_frontier_advanced(returns, req.assets, n_portfolios)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico: {str(e)}")
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_efficient_frontier_advanced(returns, req.assets, n_portfolios)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico: {str(e)}")

@router.post("/plots/advanced/rolling-beta", tags=["Advanced Charts"])
def plot_rolling_beta_endpoint(
    req: RollingBetaRequest,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Plots the rolling beta of an asset against a benchmark.

    Args:
        req (RollingBetaRequest): Request body containing asset, benchmark, start date, end date, and window.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the rolling beta chart.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        # Buscar preços do ativo e do benchmark
        prices = loader.fetch_stock_prices([req.asset, req.benchmark], req.start_date, req.end_date)
        
        # Calcular retornos
        returns = prices.pct_change().dropna()
        
        asset_returns = returns[req.asset]
        benchmark_returns = returns[req.benchmark]
        
        # Calcular beta rolante
        rolling_beta = calculate_rolling_beta(asset_returns, benchmark_returns, window=req.window)
        
        # Gerar gráfico
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_rolling_beta(rolling_beta, req.asset, req.benchmark, window=req.window)
        
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico de beta rolante: {str(e)}")

@router.post("/plots/advanced/underwater", tags=["Advanced Charts"])
def plot_underwater_endpoint(
    req: UnderwaterPlotRequest,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Plots the drawdown chart (underwater plot) for an asset.

    Args:
        req (UnderwaterPlotRequest): Request body containing asset tickers, start date, and end date.
                                     Assumes a single asset for the underwater plot.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the underwater plot.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        # Buscar preços do ativo
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        
        # Calcular retornos
        returns = prices[req.assets[0]].pct_change().dropna() # Assume single asset for underwater plot
        
        # Gerar gráfico
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_underwater(returns, req.assets[0])
        
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico underwater: {str(e)}")

@router.post("/plots/advanced/asset-allocation", tags=["Advanced Charts"])
def plot_asset_allocation_endpoint(
    req: AssetAllocationRequest,
) -> StreamingResponse:
    """
    Generates a pie chart of asset allocation.

    Args:
        req (AssetAllocationRequest): Request body containing asset weights and an optional title.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the asset allocation chart.

    Raises:
        HTTPException: 422 if data processing error,
                       500 for internal server errors.
    """
    try:
        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_asset_allocation(req.weights, req.title)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico de alocação de ativos: {str(e)}")

@router.post("/plots/advanced/cumulative-performance", tags=["Advanced Charts"])
def plot_cumulative_performance_endpoint(
    req: CumulativePerformanceRequest,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates a line chart of cumulative performance for assets/portfolio against benchmarks.

    Args:
        req (CumulativePerformanceRequest): Request body containing assets, optional benchmarks,
                                            start date, end date, and an optional title.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the cumulative performance chart.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        # Fetch prices for all assets and benchmarks
        all_assets = list(set(req.assets + (req.benchmarks if req.benchmarks else [])))
        prices = loader.fetch_stock_prices(all_assets, req.start_date, req.end_date)

        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_cumulative_performance(prices, req.assets, req.benchmarks, req.title)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico de performance acumulada: {str(e)}")

@router.post("/plots/advanced/risk-contribution", tags=["Advanced Charts"])
def plot_risk_contribution_endpoint(
    req: RiskContributionRequest,
    loader: Any = Depends(get_loader),
    risk_engine: RiskEngine = Depends(get_risk_engine)
) -> StreamingResponse:
    """
    Generates a bar chart of each asset's risk contribution to the portfolio.

    Args:
        req (RiskContributionRequest): Request body containing assets, start date, end date,
                                       weights, risk attribution method, and EWMA lambda.
        loader (Any): Dependency injection for data loader.
        risk_engine (RiskEngine): Dependency injection for the risk engine.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the risk contribution chart.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        # Fetch prices and calculate risk attribution
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = compute_returns(prices)
        
        risk_attribution_data = risk_engine.compute_attribution(
            req.assets, req.start_date, req.end_date, req.weights, req.method, req.ewma_lambda
        )

        visualizer = AdvancedVisualizer()
        chart_bytes = visualizer.plot_risk_contribution(risk_attribution_data, req.title)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico de contribuição de risco: {str(e)}")

@router.post("/plots/dashboard/sector-analysis", tags=["Dashboards"])
def generate_sector_analysis_dashboard(
    req: SectorAnalysisRequest,
    loader: Any = Depends(get_loader),
    config: Any = Depends(get_config)
) -> StreamingResponse:
    """
    Generates a dashboard for sector analysis.

    Args:
        req (SectorAnalysisRequest): Request body containing assets, start date, and end date.
        loader (Any): Dependency injection for data loader.
        config (Any): Dependency injection for configuration settings.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the sector analysis dashboard.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        # Buscar preços e informações dos ativos
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        asset_info = loader.fetch_asset_info(req.assets)
        
        # Gerar dashboard
        generator = DashboardGenerator(config=config)
        chart_bytes = generator.generate_sector_dashboard(prices, asset_info)
        
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar dashboard de setores: {str(e)}")

# ==================== DASHBOARDS ====================

@router.post("/plots/dashboard/portfolio", tags=["Dashboards"])
def generate_portfolio_dashboard(
    req: DashboardRequest,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates a comprehensive portfolio dashboard.

    Args:
        req (DashboardRequest): Request body containing assets, start date, end date, and optional benchmark.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the portfolio dashboard.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        benchmark_series = None
        if req.benchmark:
            benchmark_prices = loader.fetch_stock_prices([req.benchmark], req.start_date, req.end_date)
            benchmark_series = benchmark_prices[req.benchmark].pct_change().dropna()
        
        generator = DashboardGenerator()
        chart_bytes = generator.generate_portfolio_dashboard(returns, req.assets, benchmark_series)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar dashboard: {str(e)}")
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        benchmark_series = None
        if req.benchmark:
            benchmark_prices = loader.fetch_stock_prices([req.benchmark], req.start_date, req.end_date)
            benchmark_series = benchmark_prices[req.benchmark].pct_change().dropna()
        
        generator = DashboardGenerator()
        chart_bytes = generator.generate_portfolio_dashboard(returns, req.assets, benchmark_series)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar dashboard: {str(e)}")

@router.post("/plots/dashboard/risk", tags=["Dashboards"])
def generate_risk_dashboard(
    req: DashboardRequest,
    var_alpha: float = 0.95,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates a dashboard focused on risk analysis.

    Args:
        req (DashboardRequest): Request body containing assets, start date, and end date.
        var_alpha (float): Alpha level for Value at Risk (VaR) calculation. Defaults to 0.95.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the risk dashboard.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        generator = DashboardGenerator()
        chart_bytes = generator.generate_risk_dashboard(returns, req.assets, var_alpha)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar dashboard: {str(e)}")

@router.post("/plots/dashboard/performance", tags=["Dashboards"])
def generate_performance_dashboard(
    req: DashboardRequest,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates a dashboard focused on portfolio performance.

    Args:
        req (DashboardRequest): Request body containing assets, start date, end date, and optional benchmark.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the performance dashboard.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        benchmark_series = None
        if req.benchmark:
            benchmark_prices = loader.fetch_stock_prices([req.benchmark], req.start_date, req.end_date)
            benchmark_series = benchmark_prices[req.benchmark].pct_change().dropna()
        
        generator = DashboardGenerator()
        chart_bytes = generator.generate_performance_dashboard(returns, req.assets, benchmark_series)
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar dashboard: {str(e)}")

@router.post("/plots/dashboard/monte-carlo", tags=["Dashboards"])
def generate_monte_carlo_dashboard(
    req: MonteCarloDashboardRequest,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates a Monte Carlo simulation dashboard for a portfolio.

    Args:
        req (MonteCarloDashboardRequest): Request body containing assets, start date, end date,
                                          weights, number of paths, number of days,
                                          volatility method, EWMA lambda, and random seed.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the PNG image of the Monte Carlo dashboard.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        # Simular Monte Carlo
        engine = MonteCarloEngine(loader=loader, config=get_config())
        simulation_results = engine.simulate_gbm(
            assets=req.assets,
            start_date=req.start_date,
            end_date=req.end_date,
            weights=req.weights,
            n_paths=req.n_paths,
            n_days=req.n_days,
            vol_method=req.vol_method,
            ewma_lambda=req.ewma_lambda,
            seed=req.seed
        )
        
        # Gerar dashboard
        generator = DashboardGenerator(config=get_config())
        chart_bytes = generator.generate_monte_carlo_dashboard(simulation_results)
        
        return StreamingResponse(io.BytesIO(chart_bytes), media_type="image/png")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar dashboard de Monte Carlo: {str(e)}")

# ==================== GRÁFICOS INTERATIVOS ====================

@router.post("/plots/interactive/candlestick", tags=["Interactive Charts"])
def plot_interactive_candlestick(
    req: PricesRequest,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates an interactive candlestick chart (JSON format).

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the JSON representation of the interactive candlestick chart.

    Raises:
        HTTPException: 422 if no asset is specified or data processing error,
                       503 if data fetching fails,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        visualizer = InteractiveVisualizer()
        
        asset = req.assets[0] if req.assets else None
        if not asset:
            raise HTTPException(status_code=422, detail="Pelo menos um ativo deve ser especificado")
        
        chart_json = visualizer.plot_interactive_candlestick(prices, asset)
        return StreamingResponse(io.BytesIO(chart_json), media_type="application/json")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar gráfico interativo: {str(e)}")

@router.post("/plots/interactive/portfolio-analysis", tags=["Interactive Charts"])
def plot_interactive_portfolio_analysis(
    req: PricesRequest,
    benchmark: Optional[str] = None,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates an interactive portfolio analysis chart (JSON format).

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        benchmark (Optional[str]): Ticker of the benchmark asset. Defaults to None.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the JSON representation of the interactive portfolio analysis.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        benchmark_series = None
        if benchmark:
            benchmark_prices = loader.fetch_stock_prices([benchmark], req.start_date, req.end_date)
            benchmark_series = benchmark_prices[benchmark].pct_change().dropna()
        
        visualizer = InteractiveVisualizer()
        chart_json = visualizer.plot_interactive_portfolio_analysis(returns, req.assets, benchmark_series)
        return StreamingResponse(io.BytesIO(chart_json), media_type="application/json")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar análise interativa: {str(e)}")

@router.post("/plots/interactive/efficient-frontier", tags=["Interactive Charts"])
def plot_interactive_efficient_frontier(
    req: PricesRequest,
    n_portfolios: int = 1000,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates an interactive efficient frontier chart (JSON format).

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        n_portfolios (int): Number of random portfolios to simulate for the efficient frontier. Defaults to 1000.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the JSON representation of the interactive efficient frontier.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        visualizer = InteractiveVisualizer()
        chart_json = visualizer.plot_interactive_efficient_frontier(returns, req.assets, n_portfolios)
        return StreamingResponse(io.BytesIO(chart_json), media_type="application/json")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar fronteira interativa: {str(e)}")

@router.post("/plots/interactive/risk-metrics", tags=["Interactive Charts"])
def plot_interactive_risk_metrics(
    req: PricesRequest,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates interactive risk metrics (JSON format).

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the JSON representation of the interactive risk metrics.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        visualizer = InteractiveVisualizer()
        chart_json = visualizer.plot_interactive_risk_metrics(returns, req.assets)
        return StreamingResponse(io.BytesIO(chart_json), media_type="application/json")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar métricas interativas: {str(e)}")

@router.post("/plots/interactive/correlation-matrix", tags=["Interactive Charts"])
def plot_interactive_correlation_matrix(
    req: PricesRequest,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates an interactive correlation matrix (JSON format).

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the JSON representation of the interactive correlation matrix.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices(req.assets, req.start_date, req.end_date)
        returns = prices.pct_change().dropna()
        
        visualizer = InteractiveVisualizer()
        chart_json = visualizer.plot_interactive_correlation_matrix(returns, req.assets)
        return StreamingResponse(io.BytesIO(chart_json), media_type="application/json")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar correlação interativa: {str(e)}")

@router.post("/plots/interactive/monte-carlo", tags=["Interactive Charts"])
def plot_interactive_monte_carlo(
    req: PricesRequest,
    asset: str,
    n_simulations: int = 1000,
    n_days: int = 252,
    loader: Any = Depends(get_loader)
) -> StreamingResponse:
    """
    Generates an interactive Monte Carlo simulation chart (JSON format).

    Args:
        req (PricesRequest): Request body containing asset tickers, start date, and end date.
        asset (str): The specific asset ticker for which to run the Monte Carlo simulation.
        n_simulations (int): Number of Monte Carlo simulations to run. Defaults to 1000.
        n_days (int): Number of days to simulate into the future. Defaults to 252.
        loader (Any): Dependency injection for data loader.

    Returns:
        StreamingResponse: A streaming response containing the JSON representation of the interactive Monte Carlo simulation.

    Raises:
        HTTPException: 503 if data fetching fails,
                       422 if data processing error,
                       500 for internal server errors.
    """
    try:
        prices = loader.fetch_stock_prices([asset], req.start_date, req.end_date)
        returns = prices[asset].pct_change().dropna()
        
        visualizer = InteractiveVisualizer()
        chart_json = visualizer.plot_interactive_monte_carlo(returns, n_simulations, n_days)
        return StreamingResponse(io.BytesIO(chart_json), media_type="application/json")
    
    except DataProviderError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao buscar dados: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Erro nos dados fornecidos ou processamento: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao gerar simulação interativa: {str(e)}")
