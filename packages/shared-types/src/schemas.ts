import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

const PricesRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
  })
  .passthrough();
const get_prices_api_v1_prices_get_Body = z.union([PricesRequest, z.null()]);
const assets = z.union([z.string(), z.null()]).optional();
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
const MonthlyReturnsRequest = z
  .object({
    assets: z.array(z.string()),
    start_date: z.string(),
    end_date: z.string(),
    weights: z.union([z.array(z.number()), z.null()]).optional(),
    benchmark: z.union([z.string(), z.null()]).optional(),
  })
  .passthrough();
const MonthlyReturnRow = z
  .object({
    year: z.number().int(),
    jan: z.union([z.number(), z.null()]).optional(),
    fev: z.union([z.number(), z.null()]).optional(),
    mar: z.union([z.number(), z.null()]).optional(),
    abr: z.union([z.number(), z.null()]).optional(),
    mai: z.union([z.number(), z.null()]).optional(),
    jun: z.union([z.number(), z.null()]).optional(),
    jul: z.union([z.number(), z.null()]).optional(),
    ago: z.union([z.number(), z.null()]).optional(),
    set: z.union([z.number(), z.null()]).optional(),
    out: z.union([z.number(), z.null()]).optional(),
    nov: z.union([z.number(), z.null()]).optional(),
    dez: z.union([z.number(), z.null()]).optional(),
    acumAno: z.union([z.number(), z.null()]).optional(),
    cdi: z.union([z.number(), z.null()]).optional(),
    acumFdo: z.union([z.number(), z.null()]).optional(),
    acumCdi: z.union([z.number(), z.null()]).optional(),
  })
  .passthrough();
const MonthlyReturnsResponse = z
  .object({
    data: z.array(MonthlyReturnRow),
    lastUpdate: z.string(),
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
const InvestmentRequest = z.object({}).partial().passthrough();
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
  get_prices_api_v1_prices_get_Body,
  assets,
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
  MonthlyReturnsRequest,
  MonthlyReturnRow,
  MonthlyReturnsResponse,
  OrderType,
  TradeOrder,
  PortfolioSimulationRequest,
  PortfolioValue,
  PortfolioPerformance,
  HoldingInfo,
  PortfolioSimulationResponse,
  InvestmentRequest,
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

export const endpoints = makeApi([
  {
    method: "get",
    path: "/",
    alias: "root__get",
    requestFormat: "json",
    response: z.unknown(),
  },
  {
    method: "post",
    path: "/api/v1/analysis/run",
    alias: "run_analysis_api_v1_analysis_run_post",
    description: `Runs a portfolio analysis based on an uploaded transactions file.

The uploaded file is expected to be an Excel file containing transaction data
with required columns: &#x27;Data&#x27;, &#x27;Ativo&#x27;, &#x27;Tipo&#x27;.

Args:
    transactions_file (Optional[UploadFile]): The uploaded Excel file containing transaction data.

Returns:
    dict: A dictionary containing the status, a success message, and the analysis results.

Raises:
    HTTPException: 422 if no file is uploaded,
                   400 if the file format is invalid (missing required columns),
                   500 for internal server errors during processing.`,
    requestFormat: "form-data",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: Body_run_analysis_api_v1_analysis_run_post,
      },
    ],
    response: z.object({}).partial().passthrough(),
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
    description: `Returns a list of available assets with HTTP caching headers.

The response includes &#x60;Cache-Control&#x60; and &#x60;Vary&#x60; headers to optimize caching
by clients and proxies.`,
    requestFormat: "json",
    response: z.array(z.string()),
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
    description: `Refreshes an access token using a valid refresh token.

Args:
    refresh_token (str): The refresh token provided to the client.

Returns:
    Token: A Pydantic model containing the new access token and token type.

Raises:
    HTTPException: 401 if the refresh token is invalid.`,
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
    description: `Authenticates a user and returns access and refresh tokens.

Args:
    form_data (Annotated[OAuth2PasswordRequestForm, Depends()]): OAuth2 form data
                                                                 containing username and password.

Returns:
    Token: A Pydantic model containing the access token, token type, and refresh token.

Raises:
    HTTPException: 401 if authentication fails (incorrect username or password).`,
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
    description: `Returns public configuration settings of the API.

Args:
    config (Settings): Dependency injection for application settings.

Returns:
    Dict[str, Any]: A dictionary containing public configuration parameters.`,
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
    description: `Performs Arbitrage Pricing Theory (APT) - multifactor regression.

Args:
    req (APTRequest): Request body containing assets, start date, end date, and a list of factors.
    opt (OptimizationEngine): Dependency injection for the optimization engine.

Returns:
    RiskResponse: A Pydantic model containing the APT metrics.`,
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
    description: `Calculates CAPM metrics (beta, alpha, Sharpe) against a benchmark.

Args:
    req (CAPMRequest): Request body containing assets, start date, end date, and benchmark ticker.
    opt (OptimizationEngine): Dependency injection for the optimization engine.

Returns:
    RiskResponse: A Pydantic model containing the CAPM metrics.`,
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
    description: `Calculates Fama-French 3-factor metrics (monthly) with selectable risk-free rate.

Args:
    req (FF3Request): Request body containing assets, start date, end date,
                      and the source for the risk-free rate (&#x27;ff&#x27;, &#x27;selic&#x27;, or &#x27;us10y&#x27;).
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    RiskResponse: A Pydantic model containing the Fama-French 3-factor analysis results.

Raises:
    HTTPException: 422 if an insufficient number of observations for regression is found.`,
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
    description: `Calculates Fama-French 5-factor metrics (monthly): MKT-RF, SMB, HML, RMW, CMA.

Risk-free rate is selectable: SELIC (default) or US10Y.

Args:
    req (FF5Request): Request body containing assets, start date, end date,
                      and the source for the risk-free rate (&#x27;ff&#x27;, &#x27;selic&#x27;, or &#x27;us10y&#x27;).
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    RiskResponse: A Pydantic model containing the Fama-French 5-factor analysis results.

Raises:
    HTTPException: 422 if an insufficient number of observations for regression is found.`,
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
    description: `Performs Black-Litterman optimization with subjective views.

Args:
    req (BLRequest): Request body containing assets, start date, end date,
                     market caps, investor views, and tau parameter.
    opt (OptimizationEngine): Dependency injection for the optimization engine.

Returns:
    RiskResponse: A Pydantic model containing the Black-Litterman optimization results.`,
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
    description: `Generates Black-Litterman efficient frontier data points using BL expected returns.

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
    HTTPException: 422 if fewer than 2 assets are provided.`,
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
    description: `Performs Markowitz portfolio optimization (max Sharpe, min variance, max return).

Args:
    req (OptimizeRequest): Request body containing assets, start date, end date,
                           objective, optional bounds, long-only constraint, max weight,
                           and an optional risk-free rate.
    opt (OptimizationEngine): Dependency injection for the optimization engine.

Returns:
    RiskResponse: A Pydantic model containing the optimization results.`,
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
    description: `Generates Markowitz efficient frontier data points.

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
    HTTPException: 422 if fewer than 2 assets are provided.`,
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
    description: `Generates a pie chart of asset allocation.

Args:
    req (AssetAllocationRequest): Request body containing asset weights and an optional title.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the asset allocation chart.

Raises:
    HTTPException: 422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates an advanced candlestick chart with volume for a specified asset.

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    loader (Any): Dependency injection for data loader.
    config (Any): Dependency injection for configuration settings.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the candlestick chart.

Raises:
    HTTPException: 422 if no asset is specified or data processing error,
                   503 if data fetching fails,
                   500 for internal server errors.`,
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
    description: `Generates a correlation heatmap between multiple assets.

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the correlation heatmap.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates a line chart of cumulative performance for assets/portfolio against benchmarks.

Args:
    req (CumulativePerformanceRequest): Request body containing assets, optional benchmarks,
                                        start date, end date, and an optional title.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the cumulative performance chart.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates an advanced efficient frontier chart.

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    n_portfolios (int): Number of random portfolios to simulate for the efficient frontier. Defaults to 1000.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the efficient frontier chart.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates a comparative performance metrics chart for assets, optionally against a benchmark.

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    benchmark (Optional[str]): Ticker of the benchmark asset. Defaults to None.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the performance metrics chart.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
        schema: assets,
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
    description: `Generates a price comparison chart for multiple assets.

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    normalize (bool): If True, normalizes prices to start at 1. Defaults to True.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the price comparison chart.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates a Q-Q plot to check for normality of asset returns.

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    asset (str): The specific asset ticker for which to generate the Q-Q plot.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the Q-Q plot.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates a return distribution chart for multiple assets.

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the return distribution chart.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates a bar chart of each asset&#x27;s risk contribution to the portfolio.

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
                   500 for internal server errors.`,
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
    description: `Generates a comparative risk metrics chart for multiple assets.

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the risk metrics chart.

Raises:
    HTTPException: 500 for internal server errors.`,
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
    description: `Plots the rolling beta of an asset against a benchmark.

Args:
    req (RollingBetaRequest): Request body containing asset, benchmark, start date, end date, and window.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the rolling beta chart.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Plots the drawdown chart (underwater plot) for an asset.

Args:
    req (UnderwaterPlotRequest): Request body containing asset tickers, start date, and end date.
                                 Assumes a single asset for the underwater plot.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the underwater plot.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates a Monte Carlo simulation dashboard for a portfolio.

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
                   500 for internal server errors.`,
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
    description: `Generates a dashboard focused on portfolio performance.

Args:
    req (DashboardRequest): Request body containing assets, start date, end date, and optional benchmark.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the performance dashboard.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates a comprehensive portfolio dashboard.

Args:
    req (DashboardRequest): Request body containing assets, start date, end date, and optional benchmark.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the portfolio dashboard.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates a dashboard focused on risk analysis.

Args:
    req (DashboardRequest): Request body containing assets, start date, and end date.
    var_alpha (float): Alpha level for Value at Risk (VaR) calculation. Defaults to 0.95.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the risk dashboard.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates a dashboard for sector analysis.

Args:
    req (SectorAnalysisRequest): Request body containing assets, start date, and end date.
    loader (Any): Dependency injection for data loader.
    config (Any): Dependency injection for configuration settings.

Returns:
    StreamingResponse: A streaming response containing the PNG image of the sector analysis dashboard.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates an interactive candlestick chart (JSON format).

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the JSON representation of the interactive candlestick chart.

Raises:
    HTTPException: 422 if no asset is specified or data processing error,
                   503 if data fetching fails,
                   500 for internal server errors.`,
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
    description: `Generates an interactive correlation matrix (JSON format).

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the JSON representation of the interactive correlation matrix.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates an interactive efficient frontier chart (JSON format).

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    n_portfolios (int): Number of random portfolios to simulate for the efficient frontier. Defaults to 1000.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the JSON representation of the interactive efficient frontier.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Generates an interactive Monte Carlo simulation chart (JSON format).

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
                   500 for internal server errors.`,
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
    description: `Generates an interactive portfolio analysis chart (JSON format).

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    benchmark (Optional[str]): Ticker of the benchmark asset. Defaults to None.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the JSON representation of the interactive portfolio analysis.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
        schema: assets,
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
    description: `Generates interactive risk metrics (JSON format).

Args:
    req (PricesRequest): Request body containing asset tickers, start date, and end date.
    loader (Any): Dependency injection for data loader.

Returns:
    StreamingResponse: A streaming response containing the JSON representation of the interactive risk metrics.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if data processing error,
                   500 for internal server errors.`,
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
    description: `Simulate portfolio performance based on initial investment and trading orders.

Args:
    req (PortfolioSimulationRequest): Request body containing initial investment,
                                      start date, end date, and a list of trade orders.
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    PortfolioSimulationResponse: A Pydantic model containing the simulated portfolio&#x27;s
                                 value history, performance metrics, final holdings, and transactions.

Raises:
    HTTPException: 404 if no price data is found for the given assets and date range,
                   500 for other internal server errors during simulation.`,
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
    description: `Generates a series of constant weights for a buy-and-hold portfolio over time.

Args:
    req (WeightsSeriesRequest): Request body containing assets, start date, end date, and optional weights.
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    WeightsSeriesResponse: A Pydantic model containing the time series of portfolio weights.`,
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
    method: "post",
    path: "/api/v1/portfolio/monthly-returns",
    alias: "get_monthly_returns_api_v1_portfolio_monthly_returns_post",
    description: `Calculates monthly returns for a portfolio.

Args:
    req (MonthlyReturnsRequest): Request body containing assets, start date, end date, and optional weights.
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    MonthlyReturnsResponse: A Pydantic model containing monthly returns data by year and month.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: MonthlyReturnsRequest,
      },
    ],
    response: MonthlyReturnsResponse,
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
    description: `Handles OPTIONS requests for the /prices endpoint.

This endpoint is typically used by browsers for preflight requests in CORS.

Returns:
    Response: An empty FastAPI Response with a 200 status code.`,
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
    description: `Returns historical prices for the specified assets.

This endpoint supports both GET and POST requests. For GET requests, parameters
are passed as query parameters. For POST requests, parameters are passed in the
request body as a PricesRequest object.

Args:
    assets (Optional[str]): Comma-separated string of asset tickers (for GET requests).
    start_date (Optional[str]): Start date in &#x27;YYYY-MM-DD&#x27; format (for GET requests).
    end_date (Optional[str]): End date in &#x27;YYYY-MM-DD&#x27; format (for GET requests).
    payload (Optional[PricesRequest]): Request body containing assets, start date, and end date (for POST requests).
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    PricesResponse: A Pydantic model containing the historical price data.

Raises:
    HTTPException: 400 if invalid parameters are provided,
                   404 if no data is found for the specified assets and period.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: get_prices_api_v1_prices_get_Body,
      },
      {
        name: "assets",
        type: "Query",
        schema: assets,
      },
      {
        name: "start_date",
        type: "Query",
        schema: assets,
      },
      {
        name: "end_date",
        type: "Query",
        schema: assets,
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
    description: `Returns historical prices for the specified assets.

This endpoint supports both GET and POST requests. For GET requests, parameters
are passed as query parameters. For POST requests, parameters are passed in the
request body as a PricesRequest object.

Args:
    assets (Optional[str]): Comma-separated string of asset tickers (for GET requests).
    start_date (Optional[str]): Start date in &#x27;YYYY-MM-DD&#x27; format (for GET requests).
    end_date (Optional[str]): End date in &#x27;YYYY-MM-DD&#x27; format (for GET requests).
    payload (Optional[PricesRequest]): Request body containing assets, start date, and end date (for POST requests).
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    PricesResponse: A Pydantic model containing the historical price data.

Raises:
    HTTPException: 400 if invalid parameters are provided,
                   404 if no data is found for the specified assets and period.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: get_prices_api_v1_prices_get_Body,
      },
      {
        name: "assets",
        type: "Query",
        schema: assets,
      },
      {
        name: "start_date",
        type: "Query",
        schema: assets,
      },
      {
        name: "end_date",
        type: "Query",
        schema: assets,
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
    description: `Processes a list of financial operations.

Args:
    body (Body): Request body containing initial investment, start date, and a list of operations.

Returns:
    dict: A dictionary confirming the successful receipt of data.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: Body,
      },
    ],
    response: z.object({}).partial().passthrough(),
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
    description: `Performs risk attribution by asset (contribution to volatility and VaR).

Args:
    req (AttributionRequest): Request body containing assets, start date, end date,
                              optional weights, attribution method, and EWMA lambda.
    engine (RiskEngine): Dependency injection for the risk engine.

Returns:
    RiskResponse: A Pydantic model containing the risk attribution results.`,
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
    description: `Performs VaR backtesting using Kupiec, Christoffersen tests, and Basel zones.

Args:
    req (BacktestRequest): Request body containing assets, start date, end date,
                           alpha, VaR method, EWMA lambda, and optional weights.
    engine (RiskEngine): Dependency injection for the risk engine.

Returns:
    RiskResponse: A Pydantic model containing the backtesting results.

Raises:
    HTTPException: 503 if data fetching fails,
                   422 if validation or processing errors occur,
                   500 for unexpected internal errors.`,
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
    description: `Compares VaR and ES across different methods (historical, std, ewma, garch, evt).

Args:
    req (CompareRequest): Request body containing assets, start date, end date,
                          alpha, a list of methods to compare, EWMA lambda, and optional weights.
    engine (RiskEngine): Dependency injection for the risk engine.

Returns:
    RiskResponse: A Pydantic model containing the comparison results.`,
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
    description: `Calculates the covariance matrix with Ledoit-Wolf shrinkage.

Args:
    req (PricesRequest): Request body containing assets, start date, and end date.
    engine (RiskEngine): Dependency injection for the risk engine.

Returns:
    RiskResponse: A Pydantic model containing the covariance matrix calculation results.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: PricesRequest,
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
    description: `Calculates Maximum Drawdown - the largest peak-to-trough decline in a portfolio.

Args:
    req (DrawdownRequest): Request body containing assets, start date, end date, and optional weights.
    engine (RiskEngine): Dependency injection for the risk engine.

Returns:
    RiskResponse: A Pydantic model containing the drawdown calculation results.`,
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
    description: `Calculates and returns the drawdown series for a portfolio.

Args:
    req (DrawdownSeriesRequest): Request body containing assets, start date, end date, and weights.
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    TimeSeriesResponse: A Pydantic model containing the time series of drawdown values.`,
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
    description: `Calculates Expected Shortfall (ES/CVaR) - the average loss beyond VaR.

Args:
    req (EsRequest): Request body containing assets, start date, end date,
                     alpha, ES method, EWMA lambda, and optional weights.
    engine (RiskEngine): Dependency injection for the risk engine.

Returns:
    RiskResponse: A Pydantic model containing the ES calculation results.`,
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
    description: `Calculates Incremental VaR (IVaR) - the sensitivity of VaR to changes in portfolio weights.

Args:
    req (IVaRRequest): Request body containing assets, start date, end date,
                       alpha, VaR method, EWMA lambda, and delta for incremental change.
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    RiskResponse: A Pydantic model containing the IVaR calculation results.`,
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
    description: `Performs Monte Carlo simulation using Geometric Brownian Motion (GBM).

Args:
    req (MonteCarloRequest): Request body containing assets, start date, end date,
                             optional weights, number of paths, number of days,
                             volatility method, EWMA lambda, and random seed.
    mc (MonteCarloEngine): Dependency injection for the Monte Carlo engine.

Returns:
    RiskResponse: A Pydantic model containing the Monte Carlo simulation results.`,
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
    description: `Generates Monte Carlo simulation distribution data (samples or histogram).

Args:
    req (MonteCarloSamplesRequest): Request body containing assets, start date, end date,
                                    weights, volatility method, EWMA lambda, random seed,
                                    return type (&#x27;samples&#x27; or &#x27;histogram&#x27;), and number of bins.
    loader (YFinanceProvider): Dependency injection for the data loader.
    config (Settings): Dependency injection for application settings.

Returns:
    RiskResponse: A Pydantic model containing the Monte Carlo distribution data.

Raises:
    HTTPException: 422 if an invalid volatility method is specified.`,
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
    description: `Calculates Marginal VaR (MVaR) - the impact of removing each asset from the portfolio.

Args:
    req (MVaRRequest): Request body containing assets, start date, end date,
                       alpha, VaR method, and EWMA lambda.
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    RiskResponse: A Pydantic model containing the MVaR calculation results.`,
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
    description: `Calculates Relative VaR - the risk of underperformance against a benchmark.

Args:
    req (RelVaRRequest): Request body containing assets, start date, end date,
                         benchmark, alpha, VaR method, and EWMA lambda.
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    RiskResponse: A Pydantic model containing the Relative VaR calculation results.

Raises:
    HTTPException: 422 if the benchmark is not available or has no data.`,
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
    description: `Simulates a stress scenario by applying a shock to asset returns.

Args:
    req (StressRequest): Request body containing assets, start date, end date,
                         optional weights, and the percentage shock to apply.
    engine (RiskEngine): Dependency injection for the risk engine.

Returns:
    RiskResponse: A Pydantic model containing the stress test results.`,
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
    description: `Calculates Value at Risk (VaR) - a metric for the maximum expected loss.

Args:
    req (VarRequest): Request body containing assets, start date, end date,
                      alpha, VaR method, EWMA lambda, and optional weights.
    engine (RiskEngine): Dependency injection for the risk engine.

Returns:
    RiskResponse: A Pydantic model containing the VaR calculation results.`,
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
    description: `Checks if the API is online and operational.

Returns:
    Dict[str, str]: A dictionary with a &quot;status&quot; key, indicating &quot;ok&quot; if the API is running.`,
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
    description: `Calculates MACD (Moving Average Convergence Divergence) for the specified assets.

Args:
    req (TAMacdRequest): Request body containing assets, start date, end date,
                         and MACD parameters (fast, slow, signal periods).
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    PricesResponse: A Pydantic model containing the calculated MACD data.`,
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
    description: `Calculates moving averages (SMA or EMA) for the specified assets.

Args:
    req (TAMovingAveragesRequest): Request body containing assets, start date, end date,
                                   moving average windows, method, and optional filters.
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    PricesResponse: A Pydantic model containing the calculated moving average data.`,
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
    description: `Tests an investment portfolio&#x27;s performance based on specified assets, weights, and period.

Args:
    request (InvestmentRequest): Request body containing assets, weights, and the period for analysis.
    loader (YFinanceProvider): Dependency injection for the data loader.

Returns:
    Dict[str, float]: A dictionary containing various performance metrics for the simulated portfolio.

Raises:
    HTTPException: 404 if no price data is found for the given assets and date range,
                   503 if there&#x27;s a data provider error,
                   500 for other internal server errors.`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: z.object({}).partial().passthrough(),
      },
    ],
    response: z.record(z.number()),
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
