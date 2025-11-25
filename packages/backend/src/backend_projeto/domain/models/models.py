# models.py
# Modelos de dados para requests/responses (Pydantic)

from pydantic import BaseModel, Field, validator, model_validator
from typing import List, Optional, Literal, Dict, Any, Tuple


from datetime import date

class PricesRequest(BaseModel):
    assets: List[str] = Field(..., description="Lista de tickers, ex.: ['PETR4.SA','VALE3.SA']")
    start_date: str = Field(..., description="Data inicial no formato YYYY-MM-DD")
    end_date: str = Field(..., description="Data final no formato YYYY-MM-DD")

    @validator('assets')
    def assets_not_empty(cls, v):
        if not v:
            raise ValueError("assets não pode ser vazio")
        if len(v) > 100:
            raise ValueError("assets limitado a 100 tickers")
        return v

    @model_validator(mode='after')
    def validate_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("A data final deve ser posterior à data inicial")
        return self


# Factor visualization requests
class FFFactorsPlotRequest(BaseModel):
    model: Literal['ff3', 'ff5'] = 'ff3'
    start_date: str
    end_date: str


class FFBetaPlotRequest(BaseModel):
    model: Literal['ff3', 'ff5'] = 'ff3'
    asset: str
    start_date: str
    end_date: str
    rf_source: Literal['ff', 'selic', 'us10y'] = 'selic'
    convert_to_usd: bool = Field(False, description="Se verdadeiro, converte o preço do ativo para USD antes da regressão")

    @validator('asset')
    def asset_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("asset não pode ser vazio")
        return v


class RollingBetaRequest(BaseModel):
    asset: str = Field(..., description="Ticker do ativo principal")
    benchmark: str = Field(..., description="Ticker do benchmark (ex: '^BVSP')")
    start_date: str = Field(..., description="Data inicial no formato YYYY-MM-DD")
    end_date: str = Field(..., description="Data final no formato YYYY-MM-DD")
    window: int = Field(60, ge=20, description="Janela rolante em dias para o cálculo do beta")


class UnderwaterPlotRequest(PricesRequest):
    pass


# New response models for interactive charts
class TimeSeriesResponse(BaseModel):
    index: List[str]
    data: List[float]


class WeightsSeriesResponse(BaseModel):
    index: List[str]
    weights: Dict[str, List[float]]


class FrontierPoint(BaseModel):
    ret_annual: float
    vol_annual: float
    sharpe: float
    weights: Dict[str, float]


class FrontierDataResponse(BaseModel):
    points: List[FrontierPoint]


# Type definitions
MethodParametric = Literal['std', 'ewma', 'garch']
MethodAny = Literal['historical', 'std', 'ewma', 'garch', 'evt']

# Base class for risk requests
class BaseRiskRequest(BaseModel):
    assets: List[str]
    start_date: str
    end_date: str
    weights: Optional[List[float]] = None

    @validator('assets')
    def assets_not_empty(cls, v):
        if not v:
            raise ValueError("assets não pode ser vazio")
        if len(v) > 100:
            raise ValueError("assets limitado a 100 tickers")
        return v

# Base class for Black-Litterman requests
class BLRequest(BaseModel):
    assets: List[str]
    start_date: str
    end_date: str
    market_caps: Dict[str, float]
    tau: float = 0.05
    # views: lista de objetos { assets: [..], weights: [..], view: float }
    views: List[Dict[str, Any]] = []


class WeightsSeriesRequest(BaseRiskRequest):
    strategy: Literal['buy_and_hold'] = 'buy_and_hold'


class DrawdownSeriesRequest(BaseRiskRequest):
    pass


class MonteCarloSamplesRequest(BaseRiskRequest):
    n_paths: int = Field(10000, ge=100)
    n_days: int = Field(252, ge=1)
    vol_method: MethodParametric = 'std'
    ewma_lambda: float = Field(0.94, ge=0.5, le=0.999)
    seed: Optional[int] = None
    return_type: Literal['histogram', 'samples'] = 'histogram'
    bins: int = Field(50, ge=10, le=500)


class BLFrontierRequest(BLRequest):
    n_samples: int = Field(5000, ge=100)
    long_only: bool = True
    max_weight: Optional[float] = Field(None, description="Limite máximo por ativo (0-1)")
    rf: float = 0.0


class FF5Request(BaseModel):
    assets: List[str]
    start_date: str
    end_date: str
    frequency: Literal['M'] = 'M'
    market: Literal['US'] = 'US'
    rf_source: Literal['ff', 'selic', 'us10y'] = Field('selic', description="Fonte do RF: ff (do dataset FF), selic (Brasil) ou us10y (EUA)")
    convert_to_usd: bool = Field(False, description="Se verdadeiro, converte preços BRL para USD antes da regressão")

    @validator('assets')
    def assets_not_empty(cls, v):
        if not v:
            raise ValueError("assets não pode ser vazio")
        if len(v) > 100:
            raise ValueError("assets limitado a 100 tickers")
        return v


# Fama-French 3 factors
class FF3Request(BaseModel):
    assets: List[str]
    start_date: str
    end_date: str
    frequency: Literal['M'] = 'M'
    market: Literal['US'] = 'US'
    rf_source: Literal['ff', 'selic', 'us10y'] = Field('selic', description="Fonte do RF: ff (do dataset FF), selic (Brasil) ou us10y (EUA)")
    convert_to_usd: bool = Field(False, description="Se verdadeiro, converte preços BRL para USD antes da regressão")

    @validator('assets')
    def assets_not_empty(cls, v):
        if not v:
            raise ValueError("assets não pode ser vazio")
        if len(v) > 100:
            raise ValueError("assets limitado a 100 tickers")
        return v


class PricesResponse(BaseModel):
    columns: List[str]
    index: List[str]
    data: List[List[float]]



class VarRequest(BaseRiskRequest):
    alpha: float = Field(0.99, ge=0.5, le=0.999)
    method: MethodAny = 'historical'
    ewma_lambda: float = Field(0.94, ge=0.5, le=0.999)


class EsRequest(BaseRiskRequest):
    alpha: float = Field(0.99, ge=0.5, le=0.999)
    method: MethodAny = 'historical'
    ewma_lambda: float = Field(0.94, ge=0.5, le=0.999)


class DrawdownRequest(BaseRiskRequest):
    pass


class StressRequest(BaseRiskRequest):
    shock_pct: float = Field(-0.1, description="Choque percentual aplicado ao último retorno diário")


class BacktestRequest(BaseRiskRequest):
    alpha: float = Field(0.99, ge=0.5, le=0.999)
    method: MethodAny = 'historical'
    ewma_lambda: float = Field(0.94, ge=0.5, le=0.999)


class MonteCarloRequest(BaseRiskRequest):
    n_paths: int = Field(10000, ge=100)
    n_days: int = Field(252, ge=1)
    vol_method: MethodParametric = 'std'
    ewma_lambda: float = Field(0.94, ge=0.5, le=0.999)
    seed: Optional[int] = None


class RiskResponse(BaseModel):
    result: Dict[str, Any]


class OptimizeRequest(BaseModel):
    assets: List[str]
    start_date: str
    end_date: str
    objective: Literal['max_sharpe', 'min_var', 'max_return'] = 'max_sharpe'
    long_only: bool = True
    max_weight: Optional[float] = None
    bounds: Optional[List[Tuple[float, float]]] = None
    risk_free_rate: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Taxa livre de risco anualizada (ex: 0.05 para 5%). Se não especificada, usa o valor da configuração."
    )


class CAPMRequest(BaseModel):
    assets: List[str]
    start_date: str
    end_date: str
    benchmark: str = Field(
        ...,
        description=(
            "Ticker do benchmark ou alias. Aceita: '^GSPC', 'SPY', 'sp500', 's&p500' para S&P500; "
            "'URTH', 'ACWI', 'msci world' para MSCI World."
        ),
    )


class APTRequest(BaseModel):
    assets: List[str]
    start_date: str
    end_date: str
    factors: List[str]


class AttributionRequest(BaseRiskRequest):
    method: Literal['std', 'ewma'] = 'std'
    ewma_lambda: float = Field(0.94, ge=0.5, le=0.999)


class CompareRequest(BaseRiskRequest):
    alpha: float = Field(0.99, ge=0.5, le=0.999)
    methods: List[MethodAny] = Field(default_factory=lambda: ['historical','std','ewma'])
    ewma_lambda: float = Field(0.94, ge=0.5, le=0.999)


class FrontierRequest(BaseModel):
    assets: List[str]
    start_date: str
    end_date: str
    n_samples: int = Field(5000, ge=100)
    long_only: bool = True
    max_weight: Optional[float] = Field(None, description="Limite máximo por ativo (0-1)")
    rf: float = 0.0


# Technical Analysis requests
class TAMovingAveragesRequest(PricesRequest):
    method: Literal['sma', 'ema'] = 'sma'
    windows: List[int] = Field(default_factory=lambda: [5, 21])
    include_original: bool = True
    only_columns: Optional[List[str]] = None

    @validator('windows')
    def windows_positive_unique(cls, v):
        if not v:
            raise ValueError("windows não pode ser vazio")
        if any(w <= 0 for w in v):
            raise ValueError("windows devem ser positivos")
        if len(v) != len(set(v)):
            raise ValueError("windows devem ser únicos")
        return v


class TAMacdRequest(PricesRequest):
    fast: int = 12
    slow: int = 26
    signal: int = 9
    include_original: bool = True
    only_columns: Optional[List[str]] = None

    @model_validator(mode='after')
    def validate_macd_params(self):
        if self.fast >= self.slow:
            raise ValueError("fast deve ser menor que slow")
        return self


# Technical Analysis Plot Request
class TAPlotRequest(BaseModel):
    asset: str = Field(..., description="Ticker do ativo para gerar o gráfico")
    start_date: str = Field(..., description="Data inicial no formato YYYY-MM-DD")
    end_date: str = Field(..., description="Data final no formato YYYY-MM-DD")
    plot_type: Literal['ma', 'macd', 'combined'] = 'combined'
    ma_windows: List[int] = Field(default_factory=lambda: [5, 21])
    ma_method: Literal['sma', 'ema'] = 'sma'
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9

    @validator('asset')
    def asset_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("asset não pode ser vazio")
        return v

    @validator('ma_windows')
    def windows_positive_unique(cls, v):
        if not v:
            raise ValueError("ma_windows não pode ser vazio")
        if any(w <= 0 for w in v):
            raise ValueError("ma_windows devem ser positivos")
        if len(v) != len(set(v)):
            raise ValueError("ma_windows devem ser únicos")
        return v

    @model_validator(mode='after')
    def validate_macd_params(self):
        if self.macd_fast >= self.macd_slow:
            raise ValueError("macd_fast deve ser menor que macd_slow")
        return self


# Risk extensions: IVaR, MVaR, Relative VaR
class IVaRRequest(BaseRiskRequest):
    alpha: float = Field(0.99, ge=0.5, le=0.999)
    method: MethodAny = 'historical'
    ewma_lambda: float = Field(0.94, ge=0.5, le=0.999)
    delta: float = Field(0.01, gt=0.0, le=0.5)


class MVaRRequest(BaseRiskRequest):
    alpha: float = Field(0.99, ge=0.5, le=0.999)
    method: MethodAny = 'historical'
    ewma_lambda: float = Field(0.94, ge=0.5, le=0.999)


class RelVaRRequest(BaseRiskRequest):
    alpha: float = Field(0.99, ge=0.5, le=0.999)
    method: MethodAny = 'historical'
    ewma_lambda: float = Field(0.94, ge=0.5, le=0.999)
    benchmark: str = Field(
        ...,
        description=(
            "Ticker do benchmark ou alias (ex.: '^GSPC'/'SPY'/'sp500' para S&P500; 'URTH'/'ACWI'/'msci world' para MSCI World)."
        ),
    )

    @validator('benchmark')
    def benchmark_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("benchmark não pode ser vazio")
        return v


# Comprehensive visualization request
class ComprehensiveChartsRequest(BaseModel):
    assets: List[str] = Field(..., description="Lista de ativos para gerar gráficos")
    start_date: str = Field(..., description="Data inicial no formato YYYY-MM-DD")
    end_date: str = Field(..., description="Data final no formato YYYY-MM-DD")
    chart_types: List[Literal['technical_analysis', 'fama_french', 'efficient_frontier']] = Field(
        default_factory=lambda: ['technical_analysis', 'fama_french', 'efficient_frontier'],
        description="Tipos de gráficos a gerar"
    )
    output_dir: str = Field("generated_plots", description="Diretório onde salvar os gráficos")
    plot_configs: Optional[Dict[str, Any]] = Field(None, description="Configurações específicas para cada tipo de gráfico")

    @validator('assets')
    def assets_not_empty(cls, v):
        if not v:
            raise ValueError("assets não pode ser vazio")
        if len(v) > 100:
            raise ValueError("assets limitado a 100 tickers")
        return v

    @validator('chart_types')
    def chart_types_valid(cls, v):
        valid_types = ['technical_analysis', 'fama_french', 'efficient_frontier']
        for chart_type in v:
            if chart_type not in valid_types:
                raise ValueError(f"Tipo de gráfico inválido: {chart_type}. Deve ser um de: {valid_types}")
        return v


class ComprehensiveChartsResponse(BaseModel):
    generated_files: Dict[str, str] = Field(..., description="Dicionário com caminhos dos arquivos gerados")
    summary: Dict[str, Any] = Field(..., description="Resumo da geração de gráficos")


# Novos modelos para visualizações avançadas
class AdvancedChartRequest(BaseModel):
    assets: List[str] = Field(..., description="Lista de ativos para análise")
    start_date: str = Field(..., description="Data inicial no formato YYYY-MM-DD")
    end_date: str = Field(..., description="Data final no formato YYYY-MM-DD")
    chart_type: Literal['candlestick', 'price_comparison', 'risk_metrics', 'correlation_heatmap', 
                       'return_distribution', 'qq_plot', 'performance_metrics', 'efficient_frontier_advanced'] = Field(
        ..., description="Tipo de gráfico avançado"
    )
    normalize: bool = Field(True, description="Normalizar preços para base 100")
    benchmark: Optional[str] = Field(None, description="Ticker do benchmark para comparação")
    n_portfolios: int = Field(1000, ge=100, le=10000, description="Número de portfólios para fronteira eficiente")

    @validator('assets')
    def assets_not_empty(cls, v):
        if not v:
            raise ValueError("assets não pode ser vazio")
        if len(v) > 50:
            raise ValueError("assets limitado a 50 tickers para gráficos avançados")
        return v


class DashboardRequest(BaseModel):
    assets: List[str] = Field(..., description="Lista de ativos para dashboard")
    start_date: str = Field(..., description="Data inicial no formato YYYY-MM-DD")
    end_date: str = Field(..., description="Data final no formato YYYY-MM-DD")
    title: str = Field("Financial Dashboard", description="Título do dashboard")
    benchmark: Optional[str] = Field(None, description="Ticker do benchmark")
    dashboard_type: Literal['portfolio', 'risk', 'performance'] = Field(
        'portfolio', description="Tipo de dashboard"
    )

    @validator('assets')
    def assets_not_empty(cls, v):
        if not v:
            raise ValueError("assets não pode ser vazio")
        if len(v) > 20:
            raise ValueError("assets limitado a 20 tickers para dashboards")
        return v


class SectorAnalysisRequest(BaseRiskRequest):
    pass


class MonteCarloDashboardRequest(BaseRiskRequest):
    n_paths: int = Field(1000, ge=100, le=10000, description="Número de caminhos de simulação")
    n_days: int = Field(252, ge=30, le=1000, description="Número de dias para simulação")
    vol_method: MethodParametric = 'std'
    ewma_lambda: float = Field(0.94, ge=0.5, le=0.999)
    seed: Optional[int] = None


class InteractiveChartRequest(BaseModel):
    assets: List[str] = Field(..., description="Lista de ativos para análise interativa")
    start_date: str = Field(..., description="Data inicial no formato YYYY-MM-DD")
    end_date: str = Field(..., description="Data final no formato YYYY-MM-DD")
    chart_type: Literal['candlestick', 'portfolio_analysis', 'efficient_frontier', 
                       'risk_metrics', 'correlation_matrix', 'monte_carlo'] = Field(
        ..., description="Tipo de gráfico interativo"
    )
    benchmark: Optional[str] = Field(None, description="Ticker do benchmark")
    n_portfolios: int = Field(1000, ge=100, le=10000, description="Número de portfólios")
    n_simulations: int = Field(1000, ge=100, le=10000, description="Número de simulações Monte Carlo")
    n_days: int = Field(252, ge=30, le=1000, description="Número de dias para simulação")

    @validator('assets')
    def assets_not_empty(cls, v):
        if not v:
            raise ValueError("assets não pode ser vazio")
        if len(v) > 30:
            raise ValueError("assets limitado a 30 tickers para gráficos interativos")
        return v


class AssetAllocationRequest(BaseModel):
    weights: Dict[str, float] = Field(..., description="Dicionário de ativos e seus pesos no portfólio.")
    title: Optional[str] = Field("Alocação de Ativos", description="Título do gráfico.")


class CumulativePerformanceRequest(BaseModel):
    assets: List[str] = Field(..., description="Lista de tickers dos ativos/portfólio.")
    start_date: str = Field(..., description="Data inicial no formato YYYY-MM-DD.")
    end_date: str = Field(..., description="Data final no formato YYYY-MM-DD.")
    benchmarks: Optional[List[str]] = Field(None, description="Lista de tickers dos benchmarks para comparação.")
    title: Optional[str] = Field("Performance Acumulada", description="Título do gráfico.")

    @validator('assets')
    def assets_not_empty(cls, v):
        if not v:
            raise ValueError("assets não pode ser vazio")
        return v


class RiskContributionRequest(BaseRiskRequest):
    method: Literal['std', 'ewma'] = 'std'
    ewma_lambda: float = Field(0.94, ge=0.5, le=0.999)
    title: Optional[str] = Field("Contribuição de Risco por Ativo", description="Título do gráfico.")


class MonthlyReturnsRequest(BaseModel):
    assets: List[str] = Field(..., description="Lista de tickers para calcular retornos mensais")
    start_date: str = Field(..., description="Data inicial no formato YYYY-MM-DD")
    end_date: str = Field(..., description="Data final no formato YYYY-MM-DD")
    weights: Optional[List[float]] = Field(None, description="Pesos dos ativos no portfólio")
    benchmark: Optional[str] = Field(None, description="Ticker do benchmark (ex: CDI)")

    @validator('assets')
    def assets_not_empty(cls, v):
        if not v:
            raise ValueError("assets não pode ser vazio")
        return v


class MonthlyReturnRow(BaseModel):
    year: int
    jan: Optional[float] = None
    fev: Optional[float] = None
    mar: Optional[float] = None
    abr: Optional[float] = None
    mai: Optional[float] = None
    jun: Optional[float] = None
    jul: Optional[float] = None
    ago: Optional[float] = None
    set_: Optional[float] = Field(None, alias="set")
    out: Optional[float] = None
    nov: Optional[float] = None
    dez: Optional[float] = None
    acumAno: Optional[float] = None
    cdi: Optional[float] = None
    acumFdo: Optional[float] = None
    acumCdi: Optional[float] = None

    class Config:
        populate_by_name = True


class MonthlyReturnsResponse(BaseModel):
    data: List[MonthlyReturnRow]
    lastUpdate: str = Field(..., description="Data da última atualização")


class ApiErrorResponse(BaseModel):
    error: str = Field(..., description="Código de erro, ex: 'invalid_request', 'data_provider_error'")
    message: str = Field(..., description="Mensagem legível do erro")
    status_code: int = Field(..., description="Código de status HTTP do erro")
    details: Optional[Dict[str, Any]] = Field(None, description="Informações adicionais sobre o erro")
    request_id: Optional[str] = Field(None, description="ID da requisição para rastreamento")
