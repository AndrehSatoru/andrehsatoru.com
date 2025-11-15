import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

const PricesRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
  })
  .passthrough();
const PricesResponse = z
  .object({
    columns: z.array(z.string()),
    index: z.array(z.string()),
    data: z.array(z.array(z.number())),
  })
  .passthrough();
const ValidationError = z
  .object({
    loc: z.array(z.union([z.string(), z.number()])),
    msg: z.string(),
    type: z.string(),
  })
  .passthrough();
const HTTPValidationError = z
  .object({ detail: z.array(ValidationError) })
  .partial()
  .passthrough();
const TAMovingAveragesRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    method: z.enum(["sma", "ema"]).optional().default("sma"),
    windows: z.array(z.number().int()).optional(),
    include_original: z.boolean().optional().default(true),
    only_columns: z.union([z.array(z.string()), z.null()]).optional(),
  })
  .passthrough();
const TAMacdRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    fast: z.number().int().optional().default(12),
    slow: z.number().int().optional().default(26),
    signal: z.number().int().optional().default(9),
    include_original: z.boolean().optional().default(true),
    only_columns: z.union([z.array(z.string()), z.null()]).optional(),
  })
  .passthrough();
const IVaRRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    alpha: z.number().gte(0.5).lte(0.999).optional().default(0.99),
    method: z
      .enum(["historical", "std", "ewma", "garch", "evt"])
      .optional()
      .default("historical"),
    ewma_lambda: z.number().gte(0.5).lte(0.999).optional().default(0.94),
    delta: z.number().gt(0).lte(0.5).optional().default(0.01),
  })
  .passthrough();
const RiskResponse = z
  .object({ result: z.object({}).partial().passthrough() })
  .passthrough();
const MVaRRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    alpha: z.number().gte(0.5).lte(0.999).optional().default(0.99),
    method: z
      .enum(["historical", "std", "ewma", "garch", "evt"])
      .optional()
      .default("historical"),
    ewma_lambda: z.number().gte(0.5).lte(0.999).optional().default(0.94),
  })
  .passthrough();
const RelVaRRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    alpha: z.number().gte(0.5).lte(0.999).optional().default(0.99),
    method: z
      .enum(["historical", "std", "ewma", "garch", "evt"])
      .optional()
      .default("historical"),
    ewma_lambda: z.number().gte(0.5).lte(0.999).optional().default(0.94),
    benchmark: z.string(),
  })
  .passthrough();
const VarRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    alpha: z.number().gte(0.5).lte(0.999).optional().default(0.99),
    method: z
      .enum(["historical", "std", "ewma", "garch", "evt"])
      .optional()
      .default("historical"),
    ewma_lambda: z.number().gte(0.5).lte(0.999).optional().default(0.94),
  })
  .passthrough();
const EsRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    alpha: z.number().gte(0.5).lte(0.999).optional().default(0.99),
    method: z
      .enum(["historical", "std", "ewma", "garch", "evt"])
      .optional()
      .default("historical"),
    ewma_lambda: z.number().gte(0.5).lte(0.999).optional().default(0.94),
  })
  .passthrough();
const DrawdownRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
  })
  .passthrough();
const StressRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    shock_pct: z.number().optional().default(-0.1),
  })
  .passthrough();
const BacktestRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    alpha: z.number().gte(0.5).lte(0.999).optional().default(0.99),
    method: z
      .enum(["historical", "std", "ewma", "garch", "evt"])
      .optional()
      .default("historical"),
    ewma_lambda: z.number().gte(0.5).lte(0.999).optional().default(0.94),
  })
  .passthrough();
const MonteCarloRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    n_paths: z.number().int().gte(100).optional().default(10000),
    n_days: z.number().int().gte(1).optional().default(252),
    vol_method: z.enum(["std", "ewma", "garch"]).optional().default("std"),
    ewma_lambda: z.number().gte(0.5).lte(0.999).optional().default(0.94),
    seed: z.union([z.number(), z.null()]).optional(),
  })
  .passthrough();
const AttributionRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    method: z.enum(["std", "ewma"]).optional().default("std"),
    ewma_lambda: z.number().gte(0.5).lte(0.999).optional().default(0.94),
  })
  .passthrough();
const CompareRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    alpha: z.number().gte(0.5).lte(0.999).optional().default(0.99),
    methods: z
      .array(z.enum(["historical", "std", "ewma", "garch", "evt"]))
      .optional(),
    ewma_lambda: z.number().gte(0.5).lte(0.999).optional().default(0.94),
  })
  .passthrough();
const DrawdownSeriesRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
  })
  .passthrough();
const TimeSeriesResponse = z
  .object({ index: z.array(z.string()), data: z.array(z.number()) })
  .passthrough();
const MonteCarloSamplesRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    n_paths: z.number().int().gte(100).optional().default(10000),
    n_days: z.number().int().gte(1).optional().default(252),
    vol_method: z.enum(["std", "ewma", "garch"]).optional().default("std"),
    ewma_lambda: z.number().gte(0.5).lte(0.999).optional().default(0.94),
    seed: z.union([z.number(), z.null()]).optional(),
    return_type: z
      .enum(["histogram", "samples"])
      .optional()
      .default("histogram"),
    bins: z.number().int().gte(10).lte(500).optional().default(50),
  })
  .passthrough();
const OptimizeRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    objective: z
      .enum(["max_sharpe", "min_var", "max_return"])
      .optional()
      .default("max_sharpe"),
    long_only: z.boolean().optional().default(true),
    max_weight: z.union([z.number(), z.null()]).optional(),
    bounds: z
      .union([z.array(z.array(z.any()).min(2).max(2)), z.null()])
      .optional(),
    risk_free_rate: z.union([z.number(), z.null()]).optional(),
  })
  .passthrough();
const BLRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    market_caps: z.record(z.number()),
    tau: z.number().optional().default(0.05),
    views: z.array(z.object({}).partial().passthrough()).optional().default([]),
  })
  .passthrough();
const FrontierRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    n_samples: z.number().int().gte(100).optional().default(5000),
    long_only: z.boolean().optional().default(true),
    max_weight: z.union([z.number(), z.null()]).optional(),
    rf: z.number().optional().default(0),
  })
  .passthrough();
const FrontierPoint = z
  .object({
    ret_annual: z.number(),
    vol_annual: z.number(),
    sharpe: z.number(),
    weights: z.record(z.number()),
  })
  .passthrough();
const FrontierDataResponse = z
  .object({ points: z.array(FrontierPoint) })
  .passthrough();
const BLFrontierRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    market_caps: z.record(z.number()),
    tau: z.number().optional().default(0.05),
    views: z.array(z.object({}).partial().passthrough()).optional().default([]),
    n_samples: z.number().int().gte(100).optional().default(5000),
    long_only: z.boolean().optional().default(true),
    max_weight: z.union([z.number(), z.null()]).optional(),
    rf: z.number().optional().default(0),
  })
  .passthrough();
const FFFactorsPlotRequest = z
  .object({
    model: z.enum(["ff3", "ff5"]).optional().default("ff3"),
    start_date: z.string(),
    end_date: z.string(),
  })
  .passthrough();
const FFBetaPlotRequest = z
  .object({
    model: z.enum(["ff3", "ff5"]).optional().default("ff3"),
    asset: z.string(),
    start_date: z.string(),
    end_date: z.string(),
    rf_source: z.enum(["ff", "selic", "us10y"]).optional().default("selic"),
    convert_to_usd: z.boolean().optional().default(false),
  })
  .passthrough();
const TAPlotRequest = z
  .object({
    asset: z.string(),
    start_date: z.string(),
    end_date: z.string(),
    plot_type: z
      .enum(["ma", "macd", "combined"])
      .optional()
      .default("combined"),
    ma_windows: z.array(z.number().int()).optional(),
    ma_method: z.enum(["sma", "ema"]).optional().default("sma"),
    macd_fast: z.number().int().optional().default(12),
    macd_slow: z.number().int().optional().default(26),
    macd_signal: z.number().int().optional().default(9),
  })
  .passthrough();
const ComprehensiveChartsRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    chart_types: z
      .array(
        z.enum(["technical_analysis", "fama_french", "efficient_frontier"])
      )
      .optional(),
    output_dir: z.string().optional().default("generated_plots"),
    plot_configs: z
      .union([z.object({}).partial().passthrough(), z.null()])
      .optional(),
  })
  .passthrough();
const ComprehensiveChartsResponse = z
  .object({
    generated_files: z.record(z.string()),
    summary: z.object({}).partial().passthrough(),
  })
  .passthrough();
const FF3Request = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    frequency: z.string().optional().default("M"),
    market: z.string().optional().default("US"),
    rf_source: z.enum(["ff", "selic", "us10y"]).optional().default("selic"),
    convert_to_usd: z.boolean().optional().default(false),
  })
  .passthrough();
const FF5Request = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    frequency: z.string().optional().default("M"),
    market: z.string().optional().default("US"),
    rf_source: z.enum(["ff", "selic", "us10y"]).optional().default("selic"),
    convert_to_usd: z.boolean().optional().default(false),
  })
  .passthrough();
const CAPMRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    benchmark: z.string(),
  })
  .passthrough();
const APTRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    factors: z.array(z.string()),
  })
  .passthrough();
const WeightsSeriesRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    strategy: z.string().optional().default("buy_and_hold"),
  })
  .passthrough();
const WeightsSeriesResponse = z
  .object({
    index: z.array(z.string()),
    weights: z.record(z.array(z.number())),
  })
  .passthrough();
const OrderType = z.enum(["BUY", "SELL"]);
const TradeOrder = z
  .object({
    asset: z.string(),
    type: OrderType,
    quantity: z.number(),
    date: z.string(),
    price: z.union([z.number(), z.null()]).optional(),
  })
  .passthrough();
const PortfolioSimulationRequest = z
  .object({
    initialInvestment: z.number(),
    startDate: z.string(),
    endDate: z.string(),
    orders: z.array(TradeOrder),
  })
  .passthrough();
const PortfolioValue = z
  .object({ date: z.string(), value: z.number() })
  .passthrough();
const PortfolioPerformance = z
  .object({
    totalReturn: z.number(),
    annualizedReturn: z.number(),
    maxDrawdown: z.number(),
    volatility: z.number(),
    sharpeRatio: z.number(),
  })
  .passthrough();
const HoldingInfo = z
  .object({
    asset: z.string(),
    quantity: z.number(),
    currentValue: z.number(),
    weight: z.number(),
    return_: z.number(),
  })
  .passthrough();
const PortfolioSimulationResponse = z
  .object({
    portfolioValue: z.array(PortfolioValue),
    performance: PortfolioPerformance,
    holdings: z.array(HoldingInfo),
    transactions: z.array(TradeOrder),
  })
  .passthrough();
const InvestmentRequest = z
  .object({
    assets: z.array(z.string()),
    weights: z.array(z.number()),
    period: z.string(),
  })
  .passthrough();
const benchmark = z.union([z.string(), z.null()]).optional();
const RollingBetaRequest = z
  .object({
    asset: z.string(),
    benchmark: z.string(),
    start_date: z.string(),
    end_date: z.string(),
    window: z.number().int().gte(20).optional().default(60),
  })
  .passthrough();
const UnderwaterPlotRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
  })
  .passthrough();
const AssetAllocationRequest = z
  .object({
    weights: z.record(z.number()),
    title: z
      .union([z.string(), z.null()])
      .optional()
      .default("Alocação de Ativos"),
  })
  .passthrough();
const CumulativePerformanceRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    benchmarks: z.union([z.array(z.string()), z.null()]).optional(),
    title: z
      .union([z.string(), z.null()])
      .optional()
      .default("Performance Acumulada"),
  })
  .passthrough();
const RiskContributionRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    method: z.enum(["std", "ewma"]).optional().default("std"),
    ewma_lambda: z.number().gte(0.5).lte(0.999).optional().default(0.94),
    title: z
      .union([z.string(), z.null()])
      .optional()
      .default("Contribuição de Risco por Ativo"),
  })
  .passthrough();
const SectorAnalysisRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
  })
  .passthrough();
const DashboardRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    title: z.string().optional().default("Financial Dashboard"),
    benchmark: z.union([z.string(), z.null()]).optional(),
    dashboard_type: z
      .enum(["portfolio", "risk", "performance"])
      .optional()
      .default("portfolio"),
  })
  .passthrough();
const MonteCarloDashboardRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    n_paths: z.number().int().gte(100).lte(10000).optional().default(1000),
    n_days: z.number().int().gte(30).lte(1000).optional().default(252),
    vol_method: z.enum(["std", "ewma", "garch"]).optional().default("std"),
    ewma_lambda: z.number().gte(0.5).lte(0.999).optional().default(0.94),
    seed: z.union([z.number(), z.null()]).optional(),
  })
  .passthrough();
const Body_run_analysis_api_v1_analysis_run_post = z
  .object({ transactions_file: z.union([z.instanceof(File), z.null()]) })
  .partial()
  .passthrough();
const Operacao = z
  .object({
    data: z.string(),
    ticker: z.string(),
    tipo: z.string(),
    valor: z.number(),
  })
  .passthrough();
const Body = z
  .object({
    valorInicial: z.number(),
    dataInicial: z.string(),
    operacoes: z.array(Operacao),
  })
  .passthrough();
const Body_login_for_access_token_api_v1_auth_token_post = z
  .object({
    grant_type: z.union([z.string(), z.null()]).optional(),
    username: z.string(),
    password: z.string(),
    scope: z.string().optional().default(""),
    client_id: z.union([z.string(), z.null()]).optional(),
    client_secret: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const Token = z
  .object({
    access_token: z.string(),
    token_type: z.string(),
    refresh_token: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();

export const schemas = {
  PricesRequest,
  PricesResponse,
  ValidationError,
  HTTPValidationError,
  TAMovingAveragesRequest,
  TAMacdRequest,
  IVaRRequest,
  RiskResponse,
  MVaRRequest,
  RelVaRRequest,
  VarRequest,
  EsRequest,
  DrawdownRequest,
  StressRequest,
  BacktestRequest,
  MonteCarloRequest,
  AttributionRequest,
  CompareRequest,
  DrawdownSeriesRequest,
  TimeSeriesResponse,
  MonteCarloSamplesRequest,
  OptimizeRequest,
  BLRequest,
  FrontierRequest,
  FrontierPoint,
  FrontierDataResponse,
  BLFrontierRequest,
  FFFactorsPlotRequest,
  FFBetaPlotRequest,
  TAPlotRequest,
  ComprehensiveChartsRequest,
  ComprehensiveChartsResponse,
  FF3Request,
  FF5Request,
  CAPMRequest,
  APTRequest,
  WeightsSeriesRequest,
  WeightsSeriesResponse,
  OrderType,
  TradeOrder,
  PortfolioSimulationRequest,
  PortfolioValue,
  PortfolioPerformance,
  HoldingInfo,
  PortfolioSimulationResponse,
  InvestmentRequest,
  benchmark,
  RollingBetaRequest,
  UnderwaterPlotRequest,
  AssetAllocationRequest,
  CumulativePerformanceRequest,
  RiskContributionRequest,
  SectorAnalysisRequest,
  DashboardRequest,
  MonteCarloDashboardRequest,
  Body_run_analysis_api_v1_analysis_run_post,
  Operacao,
  Body,
  Body_login_for_access_token_api_v1_auth_token_post,
  Token,
};

const endpoints = makeApi([
  {
    method: "post",
    path: "/api/v1/analysis/run",
    alias: "run_analysis_api_v1_analysis_run_post",
    requestFormat: "form-data",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: Body_run_analysis_api_v1_analysis_run_post,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/assets",
    alias: "get_available_assets_api_v1_assets_get",
    description: `Retorna a lista de ativos disponíveis com cache HTTP.`,
    requestFormat: "json",
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/auth/refresh",
    alias: "refresh_access_token_api_v1_auth_refresh_post",
    requestFormat: "json",
    parameters: [
      {
        name: "refresh_token",
        type: "Query",
        schema: z.string(),
      },
    ],
    response: Token,
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/auth/token",
    alias: "login_for_access_token_api_v1_auth_token_post",
    requestFormat: "form-url",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: Body_login_for_access_token_api_v1_auth_token_post,
      },
    ],
    response: Token,
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/config",
    alias: "get_public_config_api_v1_config_get",
    description: `Retorna configurações públicas da API.`,
    requestFormat: "json",
    response: z.object({}).partial().passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/factors/apt",
    alias: "factors_apt_api_v1_factors_apt_post",
    description: `Arbitrage Pricing Theory (APT) - regressão multifatorial.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: APTRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/factors/capm",
    alias: "factors_capm_api_v1_factors_capm_post",
    description: `Calcula métricas CAPM (beta, alpha, Sharpe) vs benchmark.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CAPMRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/factors/ff3",
    alias: "factors_ff3_api_v1_factors_ff3_post",
    description: `Calcula métricas Fama-French 3 fatores (mensal) com RF selecionável (SELIC default, US10Y opcional).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FF3Request,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/factors/ff5",
    alias: "factors_ff5_api_v1_factors_ff5_post",
    description: `Calcula métricas Fama-French 5 fatores (mensal): MKT-RF, SMB, HML, RMW, CMA.

RF selecionável: SELIC (padrão) ou US10Y.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FF5Request,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/opt/blacklitterman",
    alias: "opt_blacklitterman_api_v1_opt_blacklitterman_post",
    description: `Otimização Black-Litterman com views subjetivas.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: BLRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/opt/blacklitterman/frontier-data",
    alias: "bl_frontier_data_api_v1_opt_blacklitterman_frontier_data_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: BLFrontierRequest,
      },
    ],
    response: FrontierDataResponse,
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/opt/markowitz",
    alias: "opt_markowitz_api_v1_opt_markowitz_post",
    description: `Otimização de portfólio Markowitz (max Sharpe, min var, max return).

- **risk_free_rate**: Taxa livre de risco anualizada (ex: 0.05 para 5%). 
  Se não especificada, usa o valor configurado em &#x60;RISK_FREE_RATE&#x60;.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: OptimizeRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/opt/markowitz/frontier-data",
    alias: "frontier_data_api_v1_opt_markowitz_frontier_data_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FrontierRequest,
      },
    ],
    response: FrontierDataResponse,
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/asset-allocation",
    alias:
      "plot_asset_allocation_endpoint_api_v1_plots_advanced_asset_allocation_post",
    description: `Gera um gráfico de pizza da alocação de ativos.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AssetAllocationRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/candlestick",
    alias: "plot_advanced_candlestick_api_v1_plots_advanced_candlestick_post",
    description: `Gráfico de candlestick avançado com volume.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/correlation-heatmap",
    alias:
      "plot_correlation_heatmap_api_v1_plots_advanced_correlation_heatmap_post",
    description: `Heatmap de correlação entre ativos.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/cumulative-performance",
    alias:
      "plot_cumulative_performance_endpoint_api_v1_plots_advanced_cumulative_performance_post",
    description: `Gera um gráfico de linha da performance acumulada de ativos/portfólio vs. benchmarks.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CumulativePerformanceRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/efficient-frontier-advanced",
    alias:
      "plot_efficient_frontier_advanced_api_v1_plots_advanced_efficient_frontier_advanced_post",
    description: `Fronteira eficiente avançada.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
      {
        name: "n_portfolios",
        type: "Query",
        schema: z.number().int().optional().default(1000),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/performance-metrics",
    alias:
      "plot_performance_metrics_api_v1_plots_advanced_performance_metrics_post",
    description: `Métricas de performance comparativas.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
      {
        name: "benchmark",
        type: "Query",
        schema: benchmark,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/price-comparison",
    alias: "plot_price_comparison_api_v1_plots_advanced_price_comparison_post",
    description: `Comparação de preços de múltiplos ativos.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
      {
        name: "normalize",
        type: "Query",
        schema: z.boolean().optional().default(true),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/qq-plot",
    alias: "plot_qq_plot_api_v1_plots_advanced_qq_plot_post",
    description: `Q-Q plot para verificar normalidade.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
      {
        name: "asset",
        type: "Query",
        schema: z.string(),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/return-distribution",
    alias:
      "plot_return_distribution_api_v1_plots_advanced_return_distribution_post",
    description: `Distribuição de retornos.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/risk-contribution",
    alias:
      "plot_risk_contribution_endpoint_api_v1_plots_advanced_risk_contribution_post",
    description: `Gera um gráfico de barras da contribuição de risco de cada ativo para o portfólio.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: RiskContributionRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/risk-metrics",
    alias: "plot_risk_metrics_api_v1_plots_advanced_risk_metrics_post",
    description: `Métricas de risco comparativas.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/rolling-beta",
    alias: "plot_rolling_beta_endpoint_api_v1_plots_advanced_rolling_beta_post",
    description: `Plota o beta rolante de um ativo contra um benchmark.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: RollingBetaRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/advanced/underwater",
    alias: "plot_underwater_endpoint_api_v1_plots_advanced_underwater_post",
    description: `Plota o gráfico de drawdown (underwater plot) para um ativo.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: UnderwaterPlotRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/comprehensive",
    alias: "generate_comprehensive_charts_api_v1_plots_comprehensive_post",
    description: `Gera todos os tipos de gráficos disponíveis e salva como arquivos PNG.

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
    - 503: Serviço temporariamente indisponível`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: ComprehensiveChartsRequest,
      },
    ],
    response: ComprehensiveChartsResponse,
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/dashboard/monte-carlo",
    alias:
      "generate_monte_carlo_dashboard_api_v1_plots_dashboard_monte_carlo_post",
    description: `Gera um dashboard de simulação Monte Carlo para um portfólio.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: MonteCarloDashboardRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/dashboard/performance",
    alias:
      "generate_performance_dashboard_api_v1_plots_dashboard_performance_post",
    description: `Dashboard focado em performance.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DashboardRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/dashboard/portfolio",
    alias: "generate_portfolio_dashboard_api_v1_plots_dashboard_portfolio_post",
    description: `Dashboard completo de portfólio.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DashboardRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/dashboard/risk",
    alias: "generate_risk_dashboard_api_v1_plots_dashboard_risk_post",
    description: `Dashboard focado em análise de risco.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DashboardRequest,
      },
      {
        name: "var_alpha",
        type: "Query",
        schema: z.number().optional().default(0.95),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/dashboard/sector-analysis",
    alias:
      "generate_sector_analysis_dashboard_api_v1_plots_dashboard_sector_analysis_post",
    description: `Gera um dashboard de análise de setores.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: SectorAnalysisRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/efficient-frontier",
    alias: "plot_efficient_frontier_api_v1_plots_efficient_frontier_post",
    description: `Gera gráfico PNG da fronteira eficiente de Markowitz.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FrontierRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/ff-betas",
    alias: "plot_ff_betas_endpoint_api_v1_plots_ff_betas_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FFBetaPlotRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/ff-factors",
    alias: "plot_ff_factors_endpoint_api_v1_plots_ff_factors_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: FFFactorsPlotRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/interactive/candlestick",
    alias:
      "plot_interactive_candlestick_api_v1_plots_interactive_candlestick_post",
    description: `Gráfico de candlestick interativo (JSON).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/interactive/correlation-matrix",
    alias:
      "plot_interactive_correlation_matrix_api_v1_plots_interactive_correlation_matrix_post",
    description: `Matriz de correlação interativa (JSON).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/interactive/efficient-frontier",
    alias:
      "plot_interactive_efficient_frontier_api_v1_plots_interactive_efficient_frontier_post",
    description: `Fronteira eficiente interativa (JSON).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
      {
        name: "n_portfolios",
        type: "Query",
        schema: z.number().int().optional().default(1000),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/interactive/monte-carlo",
    alias:
      "plot_interactive_monte_carlo_api_v1_plots_interactive_monte_carlo_post",
    description: `Simulação Monte Carlo interativa (JSON).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
      {
        name: "asset",
        type: "Query",
        schema: z.string(),
      },
      {
        name: "n_simulations",
        type: "Query",
        schema: z.number().int().optional().default(1000),
      },
      {
        name: "n_days",
        type: "Query",
        schema: z.number().int().optional().default(252),
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/interactive/portfolio-analysis",
    alias:
      "plot_interactive_portfolio_analysis_api_v1_plots_interactive_portfolio_analysis_post",
    description: `Análise interativa de portfólio (JSON).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
      {
        name: "benchmark",
        type: "Query",
        schema: benchmark,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/interactive/risk-metrics",
    alias:
      "plot_interactive_risk_metrics_api_v1_plots_interactive_risk_metrics_post",
    description: `Métricas de risco interativas (JSON).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/plots/ta",
    alias: "plot_technical_analysis_api_v1_plots_ta_post",
    description: `Gera gráfico PNG de análise técnica (preços + MAs + MACD).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TAPlotRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/portfolio/simulate",
    alias: "simulate_portfolio_api_v1_portfolio_simulate_post",
    description: `Simulate portfolio performance based on initial investment and trading orders.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PortfolioSimulationRequest,
      },
    ],
    response: PortfolioSimulationResponse,
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/portfolio/weights-series",
    alias: "portfolio_weights_series_api_v1_portfolio_weights_series_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: WeightsSeriesRequest,
      },
    ],
    response: WeightsSeriesResponse,
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "options",
    path: "/api/v1/prices",
    alias: "options_prices_api_v1_prices_options",
    description: `Handles OPTIONS requests for /prices endpoint.`,
    requestFormat: "json",
    response: z.unknown(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/prices",
    alias: "get_prices_api_v1_prices_get",
    description: `Retorna preços históricos para os ativos especificados.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
      {
        name: "assets",
        type: "Query",
        schema: z.string().optional(),
      },
      {
        name: "start_date",
        type: "Query",
        schema: z.string().optional(),
      },
      {
        name: "end_date",
        type: "Query",
        schema: z.string().optional(),
      },
    ],
    response: PricesResponse,
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/prices",
    alias: "get_prices_api_v1_prices_post",
    description: `Retorna preços históricos para os ativos especificados.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
      },
      {
        name: "assets",
        type: "Query",
        schema: z.string().optional(),
      },
      {
        name: "start_date",
        type: "Query",
        schema: z.string().optional(),
      },
      {
        name: "end_date",
        type: "Query",
        schema: z.string().optional(),
      },
    ],
    response: PricesResponse,
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/processar_operacoes",
    alias: "processar_operacoes_api_v1_processar_operacoes_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: Body,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/attribution",
    alias: "risk_attribution_api_v1_risk_attribution_post",
    description: `Atribuição de risco por ativo (contribuição para volatilidade e VaR).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: AttributionRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/backtest",
    alias: "risk_backtest_api_v1_risk_backtest_post",
    description: `Backtest do VaR com testes de Kupiec, Christoffersen e Basel zones.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: BacktestRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/compare",
    alias: "risk_compare_api_v1_risk_compare_post",
    description: `Compara VaR e ES entre diferentes métodos (historical, std, ewma, garch, evt).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CompareRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/covariance",
    alias: "risk_covariance_api_v1_risk_covariance_post",
    description: `Calcula matriz de covariância com shrinkage Ledoit-Wolf.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: VarRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/drawdown",
    alias: "risk_drawdown_api_v1_risk_drawdown_post",
    description: `Calcula Maximum Drawdown - maior queda de pico a vale.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DrawdownRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/drawdown-series",
    alias: "risk_drawdown_series_api_v1_risk_drawdown_series_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: DrawdownSeriesRequest,
      },
    ],
    response: TimeSeriesResponse,
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/es",
    alias: "risk_es_api_v1_risk_es_post",
    description: `Calcula Expected Shortfall (ES/CVaR) - perda média além do VaR.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: EsRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/ivar",
    alias: "risk_ivar_api_v1_risk_ivar_post",
    description: `Calcula Incremental VaR (IVaR) - sensibilidade do VaR a mudanças nos pesos.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: IVaRRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/montecarlo",
    alias: "risk_montecarlo_api_v1_risk_montecarlo_post",
    description: `Simulação Monte Carlo usando Geometric Brownian Motion (GBM).`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: MonteCarloRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/montecarlo/distribution",
    alias:
      "risk_montecarlo_distribution_api_v1_risk_montecarlo_distribution_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: MonteCarloSamplesRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/mvar",
    alias: "risk_mvar_api_v1_risk_mvar_post",
    description: `Calcula Marginal VaR (MVaR) - impacto de remover cada ativo da carteira.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: MVaRRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/relvar",
    alias: "risk_relative_var_api_v1_risk_relvar_post",
    description: `Calcula VaR Relativo - risco de underperformance vs benchmark.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: RelVaRRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/stress",
    alias: "risk_stress_api_v1_risk_stress_post",
    description: `Simula cenário de stress aplicando choque aos retornos.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: StressRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/risk/var",
    alias: "risk_var_api_v1_risk_var_post",
    description: `Calcula Value at Risk (VaR) - métrica de risco de perda máxima esperada.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: VarRequest,
      },
    ],
    response: z
      .object({ result: z.object({}).partial().passthrough() })
      .passthrough(),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "get",
    path: "/api/v1/status",
    alias: "status_api_v1_status_get",
    description: `Verifica se a API está online.`,
    requestFormat: "json",
    response: z.record(z.string()),
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/ta/macd",
    alias: "ta_macd_api_v1_ta_macd_post",
    description: `Calcula MACD (Moving Average Convergence Divergence) para os ativos.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TAMacdRequest,
      },
    ],
    response: PricesResponse,
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/ta/moving-averages",
    alias: "ta_moving_averages_api_v1_ta_moving_averages_post",
    description: `Calcula médias móveis (SMA ou EMA) para os ativos.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: TAMovingAveragesRequest,
      },
    ],
    response: PricesResponse,
    errors: [
      {
        status: 404,
        description: `Not found`,
        schema: z.void(),
      },
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
  {
    method: "post",
    path: "/api/v1/test-investment",
    alias: "test_investment_api_v1_test_investment_post",
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: InvestmentRequest,
      },
    ],
    response: z.unknown(),
    errors: [
      {
        status: 422,
        description: `Validation Error`,
        schema: HTTPValidationError,
      },
    ],
  },
]);

export const api = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
