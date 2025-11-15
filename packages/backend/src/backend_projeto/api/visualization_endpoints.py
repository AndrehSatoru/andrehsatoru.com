# src/backend_projeto/api/visualization_endpoints.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import io
from datetime import datetime
from .models import (
    FrontierRequest, TAPlotRequest, FFFactorsPlotRequest, FFBetaPlotRequest, ComprehensiveChartsRequest, ComprehensiveChartsResponse
)
from .deps import get_loader, get_config
from backend_projeto.core.data_handling import YFinanceProvider
from backend_projeto.core.visualizations.visualization import efficient_frontier_image
from backend_projeto.core.visualizations.ta_visualization import plot_price_with_ma, plot_macd, plot_combined_ta
from backend_projeto.core.visualizations.factor_visualization import plot_ff_factors, plot_ff_betas
from backend_projeto.core.visualizations.comprehensive_visualization import ComprehensiveVisualizer
from backend_projeto.utils.config import Settings
from backend_projeto.api.helpers import _convert_prices_to_usd, _normalize_benchmark_alias
from backend_projeto.core.exceptions import DataProviderError
import logging

router = APIRouter(
    tags=["Visualization"],
    responses={404: {"description": "Not found"}},
)

# Fronteira eficiente (imagem PNG)
@router.post("/plots/efficient-frontier")
def plot_efficient_frontier(
    req: FrontierRequest,
    loader: YFinanceProvider = Depends(get_loader),
    config: Settings = Depends(get_config)
):
    """Gera gráfico PNG da fronteira eficiente de Markowitz."""
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

# Plots: Fama-French factors time series
@router.post("/plots/ff-factors")
def plot_ff_factors_endpoint(
    req: FFFactorsPlotRequest,
    loader: YFinanceProvider = Depends(get_loader),
):
    if req.model == 'ff3':
        ff = loader.fetch_ff3_us_monthly(req.start_date, req.end_date)
        factors = ff[['MKT_RF', 'SMB', 'HML']]
    else:
        ff = loader.fetch_ff5_us_monthly(req.start_date, req.end_date)
        factors = ff[['MKT_RF', 'SMB', 'HML', 'RMW', 'CMA']]
    img_bytes = plot_ff_factors(factors)
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")


# Plots: Betas de um ativo (FF3/FF5)
@router.post("/plots/ff-betas")
def plot_ff_betas_endpoint(
    req: FFBetaPlotRequest,
    loader: YFinanceProvider = Depends(get_loader),
):
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

# Technical Analysis Plot
@router.post("/plots/ta")
def plot_technical_analysis(
    req: TAPlotRequest,
    loader: YFinanceProvider = Depends(get_loader)
):
    """Gera gráfico PNG de análise técnica (preços + MAs + MACD)."""
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
@router.post("/plots/comprehensive", response_model=ComprehensiveChartsResponse)
def generate_comprehensive_charts(
    req: ComprehensiveChartsRequest,
    loader: YFinanceProvider = Depends(get_loader),
    config: Settings = Depends(get_config)
):
    """Gera todos os tipos de gráficos disponíveis e salva como arquivos PNG.

    Esta funcionalidade combina:
    - Análise técnica (médias móveis, MACD)
    - Fatores Fama-French (FF3/FF5) e betas
    - Fronteira eficiente

    Parâmetros:
        req: Configurações para geração de gráficos
        loader: YFinanceProvider para buscar dados financeiros
        config: Configurações da aplicação

    Retorna:
        ComprehensiveChartsResponse com caminhos dos arquivos gerados

    Erros possíveis:
        - 422: Dados de entrada inválidos
        - 500: Erro interno na geração de gráficos
        - 503: Serviço temporariamente indisponível
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
