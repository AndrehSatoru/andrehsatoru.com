# models.py
# Modelos de dados para requests/responses (Pydantic)

from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Literal, Dict, Any, Tuple


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

MethodParametric = Literal['std', 'ewma', 'garch']
MethodAny = Literal['historical', 'std', 'ewma', 'garch', 'evt']


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

    @root_validator(skip_on_failure=True)
    def validate_weights(cls, values):
        assets = values.get('assets', [])
        weights = values.get('weights')
        if weights is not None:
            if len(weights) != len(assets):
                raise ValueError(f"weights deve ter mesmo tamanho que assets ({len(assets)})")
            if sum(weights) <= 0:
                raise ValueError("soma de weights deve ser > 0")
        return values


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
    # bounds opcionais: lista de tuplas [ [low, high], ... ]
    bounds: Optional[List[Tuple[float, float]]] = None


class BLRequest(BaseModel):
    assets: List[str]
    start_date: str
    end_date: str
    market_caps: Dict[str, float]
    tau: float = 0.05
    # views: lista de objetos { assets: [..], weights: [..], view: float }
    views: List[Dict[str, Any]] = []


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

    @root_validator(skip_on_failure=True)
    def validate_macd_params(cls, values):
        fast = values.get('fast', 12)
        slow = values.get('slow', 26)
        if fast >= slow:
            raise ValueError("fast deve ser menor que slow")
        return values


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


# Visualization requests
class TAPlotRequest(BaseModel):
    asset: str = Field(..., description="Ticker do ativo a plotar")
    start_date: str
    end_date: str
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
