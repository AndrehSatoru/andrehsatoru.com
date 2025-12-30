"use client"

import { createContext, useContext, ReactNode } from "react"
import { create } from "zustand"

// Interfaces for specific data types
interface PerformanceData {
  retorno_total_prct: number;
  retorno_anualizado_prct: number;
  volatilidade_anual_prct: number;
  indice_sharpe: number;
  max_drawdown_prct: number;
  var_95_1d_prct: number;
  es_95_1d_prct: number;
  dias_analisados: number;
  data_inicio: string;
  data_fim: string;
}
interface AllocationData {
  data_analise: string;
  valor_total: number;
  valor_investido: number;
  caixa: number;
  alocacao: {
    [asset: string]: {
      quantidade: number;
      preco_unitario: number;
      valor_total: number;
      percentual: number;
    };
  };
}
interface RiskData {
  risk_contribution: any[];
  beta_evolution: any[];
  beta_matrix: any;
  correlation_matrix: any;
  distance_correlation_matrix: any;
  tmfg_graph: any;
  stress_tests: any[];
  var_backtest: any;
  risk_attribution_detailed: any;
  capm_analysis: any;
  incremental_var: any;
}
interface MonteCarloData {
  distribution: any[];
  initialValue: number;
  mgb: any;
  bootstrap: any;
  params: any;
}
interface PortfolioTimeSeriesData {
  performance: any[];
  monthly_returns: any[];
  allocation_history: any[];
  rolling_annualized_returns: any[];
  drawdown: any[];
}
interface AssetStatsData {
  asset_stats: any[];
  returns_distribution: any;
  metadados?: any;
}
interface FamaFrenchData {
  fama_french: any;
}
interface MarkowitzData {
  markowitz_optimization: any;
}

// --- Performance Store ---
interface PerformanceStoreType {
  performance: PerformanceData | null;
  setPerformance: (data: PerformanceData | null) => void;
}

export const usePerformanceStore = create<PerformanceStoreType>((set) => ({
  performance: null,
  setPerformance: (data) => set({ performance: data }),
}));

// --- Allocation Store ---
interface AllocationStoreType {
  allocation: AllocationData | null;
  setAllocation: (data: AllocationData | null) => void;
}

export const useAllocationStore = create<AllocationStoreType>((set) => ({
  allocation: null,
  setAllocation: (data) => set({ allocation: data }),
}));

// --- Risk Store ---
interface RiskStoreType {
  risk: RiskData | null;
  setRisk: (data: RiskData | null) => void;
}

export const useRiskStore = create<RiskStoreType>((set) => ({
  risk: null,
  setRisk: (data) => set({ risk: data }),
}));

// --- Monte Carlo Store ---
interface MonteCarloStoreType {
  monteCarlo: MonteCarloData | null;
  setMonteCarlo: (data: MonteCarloData | null) => void;
}

export const useMonteCarloStore = create<MonteCarloStoreType>((set) => ({
  monteCarlo: null,
  setMonteCarlo: (data) => set({ monteCarlo: data }),
}));

// --- Portfolio Time Series Store ---
interface PortfolioTimeSeriesStoreType {
  timeSeries: PortfolioTimeSeriesData | null;
  setTimeSeries: (data: PortfolioTimeSeriesData | null) => void;
}

export const usePortfolioTimeSeriesStore = create<PortfolioTimeSeriesStoreType>((set) => ({
  timeSeries: null,
  setTimeSeries: (data) => set({ timeSeries: data }),
}));

// --- Asset Stats Store ---
interface AssetStatsStoreType {
  assetStats: AssetStatsData | null;
  setAssetStats: (data: AssetStatsData | null) => void;
}

export const useAssetStatsStore = create<AssetStatsStoreType>((set) => ({
  assetStats: null,
  setAssetStats: (data) => set({ assetStats: data }),
}));

// --- Fama French Store ---
interface FamaFrenchStoreType {
  famaFrench: FamaFrenchData | null;
  setFamaFrench: (data: FamaFrenchData | null) => void;
}

export const useFamaFrenchStore = create<FamaFrenchStoreType>((set) => ({
  famaFrench: null,
  setFamaFrench: (data) => set({ famaFrench: data }),
}));

// --- Markowitz Store ---
interface MarkowitzStoreType {
  markowitz: MarkowitzData | null;
  setMarkowitz: (data: MarkowitzData | null) => void;
}

export const useMarkowitzStore = create<MarkowitzStoreType>((set) => ({
  markowitz: null,
  setMarkowitz: (data) => set({ markowitz: data }),
}));

// --- Main Dashboard Data Provider ---
interface DashboardDataContextType {
  setAllAnalysisResults: (results: any) => void;
  clearAllAnalysisResults: () => void;
}

const DashboardDataContext = createContext<DashboardDataContextType | undefined>(
  undefined
);

export function DashboardDataProvider({ children }: { children: ReactNode }) {
  const setPerformance = usePerformanceStore((state) => state.setPerformance);
  const setAllocation = useAllocationStore((state) => state.setAllocation);
  const setRisk = useRiskStore((state) => state.setRisk);
  const setMonteCarlo = useMonteCarloStore((state) => state.setMonteCarlo);
  const setTimeSeries = usePortfolioTimeSeriesStore((state) => state.setTimeSeries);
  const setAssetStats = useAssetStatsStore((state) => state.setAssetStats);
  const setFamaFrench = useFamaFrenchStore((state) => state.setFamaFrench);
  const setMarkowitz = useMarkowitzStore((state) => state.setMarkowitz);

  const setAllAnalysisResults = (results: any) => {
    // Helper to sanitize results: if it contains "error", return null
    const sanitizeResult = (data: any) => {
      if (data && typeof data === 'object' && 'error' in data) {
        console.warn("Analysis result contains error, treating as null:", data.error);
        return null;
      }
      return data;
    };

    // Performance
    if (results?.desempenho) setPerformance(sanitizeResult(results.desempenho)); else setPerformance(null);
    
    // Allocation
    if (results?.alocacao) setAllocation(sanitizeResult(results.alocacao)); else setAllocation(null);

    // Risk
    const riskResults: RiskData = {
      risk_contribution: sanitizeResult(results?.risk_contribution) || null,
      beta_evolution: sanitizeResult(results?.beta_evolution) || null,
      beta_matrix: sanitizeResult(results?.beta_matrix) || null,
      correlation_matrix: sanitizeResult(results?.correlation_matrix) || null,
      distance_correlation_matrix: sanitizeResult(results?.distance_correlation_matrix) || null,
      tmfg_graph: sanitizeResult(results?.tmfg_graph) || null,
      stress_tests: sanitizeResult(results?.stress_tests) || null,
      var_backtest: sanitizeResult(results?.var_backtest) || null,
      risk_attribution_detailed: sanitizeResult(results?.risk_attribution_detailed) || null,
      capm_analysis: sanitizeResult(results?.capm_analysis) || null,
      incremental_var: sanitizeResult(results?.incremental_var) || null,
    };
    if (Object.values(riskResults).some(val => val !== null)) setRisk(riskResults); else setRisk(null);

    // Monte Carlo
    if (results?.monte_carlo) setMonteCarlo(sanitizeResult(results.monte_carlo)); else setMonteCarlo(null);

    // Time Series
    const timeSeriesResults: PortfolioTimeSeriesData = {
      performance: sanitizeResult(results?.performance) || null,
      monthly_returns: sanitizeResult(results?.monthly_returns) || null,
      allocation_history: sanitizeResult(results?.allocation_history) || null,
      rolling_annualized_returns: sanitizeResult(results?.rolling_annualized_returns) || null,
      drawdown: sanitizeResult(results?.drawdown) || null,
    };
    if (Object.values(timeSeriesResults).some(val => val !== null)) setTimeSeries(timeSeriesResults); else setTimeSeries(null);

    // Asset Stats
    const assetStatsResults: AssetStatsData = {
      asset_stats: sanitizeResult(results?.asset_stats) || null,
      returns_distribution: sanitizeResult(results?.returns_distribution) || null,
      metadados: sanitizeResult(results?.metadados) || null,
    };
    if (Object.values(assetStatsResults).some(val => val !== null)) setAssetStats(assetStatsResults); else setAssetStats(null);

    // Fama French
    if (results?.fama_french) setFamaFrench(sanitizeResult(results.fama_french)); else setFamaFrench(null);

    // Markowitz
    if (results?.markowitz_optimization) setMarkowitz(sanitizeResult(results.markowitz_optimization)); else setMarkowitz(null);
  };

  const clearAllAnalysisResults = () => {
    setPerformance(null);
    setAllocation(null);
    setRisk(null);
    setMonteCarlo(null);
    setTimeSeries(null);
    setAssetStats(null);
    setFamaFrench(null);
    setMarkowitz(null);
  };

  return (
    <DashboardDataContext.Provider value={{ setAllAnalysisResults, clearAllAnalysisResults }}>
      {children}
    </DashboardDataContext.Provider>
  );
}

// Custom hook to consume the main context and aggregate data for backward compatibility
export function useDashboardData() {
  const context = useContext(DashboardDataContext);
  if (context === undefined) {
    throw new Error("useDashboardData must be used within a DashboardDataProvider");
  }

  // Aggregate data from stores for backward compatibility
  const performance = usePerformanceStore((state) => state.performance);
  const allocation = useAllocationStore((state) => state.allocation);
  const risk = useRiskStore((state) => state.risk);
  const monteCarlo = useMonteCarloStore((state) => state.monteCarlo);
  const timeSeries = usePortfolioTimeSeriesStore((state) => state.timeSeries);
  const assetStats = useAssetStatsStore((state) => state.assetStats);
  const famaFrench = useFamaFrenchStore((state) => state.famaFrench);
  const markowitz = useMarkowitzStore((state) => state.markowitz);

  const analysisResult: any = {
    desempenho: performance,
    alocacao: allocation,
    ...risk,
    monte_carlo: monteCarlo,
    performance: timeSeries?.performance,
    monthly_returns: timeSeries?.monthly_returns,
    allocation_history: timeSeries?.allocation_history,
    rolling_annualized_returns: timeSeries?.rolling_annualized_returns,
    drawdown: timeSeries?.drawdown,
    asset_stats: assetStats?.asset_stats,
    returns_distribution: assetStats?.returns_distribution,
    metadados: assetStats?.metadados,
    fama_french: famaFrench?.fama_french,
    markowitz_optimization: markowitz?.markowitz_optimization,
  };

  return {
    ...context,
    analysisResult,
    setAnalysisResult: context.setAllAnalysisResults,
    clearAnalysisResult: context.clearAllAnalysisResults
  };
}
