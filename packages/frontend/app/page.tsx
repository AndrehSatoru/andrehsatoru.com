'use client';

import { DashboardHeader } from "@/components/dashboard-header"
import { PerformanceChart } from "@/components/performance-chart"
import { AllocationChart } from "@/components/allocation-chart"
import { VolatilityChart } from "@/components/volatility-chart"
import { AssetsTable } from "@/components/assets-table"
import { DrawdownChart } from "@/components/drawdown-chart"
import { VarChart } from "@/components/var-chart"
import { CVarChart } from "@/components/cvar-chart"
import { ReturnsDistribution } from "@/components/returns-distribution"
import { StressTestChart } from "@/components/stress-test-chart"
import dynamic from 'next/dynamic'
import { Skeleton } from '@/components/ui/skeleton'
// Lazy-loaded components
const EfficientFrontier = dynamic(
  () => import('@/components/efficient-frontier').then((mod) => mod.EfficientFrontier),
  { loading: () => <Skeleton className="h-[500px]" />, ssr: false }
)
const CorrelationMatrix = dynamic(
  () => import('@/components/correlation-matrix').then((mod) => mod.CorrelationMatrix),
  { loading: () => <Skeleton className="h-[400px]" />, ssr: false }
)
const DistanceCorrelationMatrix = dynamic(
  () => import('@/components/distance-correlation-matrix').then((mod) => mod.DistanceCorrelationMatrix),
  { loading: () => <Skeleton className="h-[400px]" />, ssr: false }
)
const TMFGGraph = dynamic(
  () => import('@/components/tmfg-graph').then((mod) => mod.TMFGGraph),
  { loading: () => <Skeleton className="h-[400px]" />, ssr: false }
)
import { AllocationEvolution } from "@/components/allocation-evolution"
import { RollingReturns } from "@/components/rolling-returns"
import { BetaMatrix } from "@/components/beta-matrix"
const MonteCarloDistribution = dynamic(
  () => import('@/components/monte-carlo-distribution').then((mod) => mod.MonteCarloDistribution),
  { loading: () => <Skeleton className="h-[400px]" />, ssr: false }
)
import { BetaEvolution } from "@/components/beta-evolution"
import { ProfitabilityTable } from "@/components/profitability-table"
const FamaFrenchPanel = dynamic(
  () => import('@/components/fama-french-panel').then((mod) => mod.FamaFrenchPanel),
  { loading: () => <Skeleton className="h-[400px]" />, ssr: false }
)
import { MarkowitzOptimization } from "@/components/markowitz-optimization"
import { VarBacktest } from "@/components/var-backtest"
import { RiskAttributionDetailed } from "@/components/risk-attribution-detailed"
import { CAPMAnalysis } from "@/components/capm-analysis"
import { IncrementalVarAnalysis } from "@/components/incremental-var-analysis"
import { PortfolioSummary } from "@/components/portfolio-summary"
import { LineChart } from "lucide-react"
import Link from "next/link"
import withAuth from "@/components/withAuth"

function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />

      <main className="max-w-[1800px] mx-auto px-6 py-8 space-y-8 2xl:px-8">
        <div className="flex justify-end">
          <Link href="/enviar" className="rounded-lg bg-primary text-primary-foreground px-5 py-2.5 text-sm font-medium shadow-sm hover:bg-primary/90 transition-colors">
            Enviar Operações
          </Link>
        </div>
        
        <PortfolioSummary />

        <div className="grid gap-6 lg:grid-cols-2 xl:gap-8">
          <PerformanceChart />
          <RollingReturns />
        </div>

        <div className="grid gap-6 lg:grid-cols-2 xl:gap-8">
          <VolatilityChart />
          <DrawdownChart />
        </div>

        <div className="grid gap-6 lg:grid-cols-2 xl:gap-8">
          <CorrelationMatrix />
          <DistanceCorrelationMatrix />
        </div>

        <div className="grid gap-6 lg:grid-cols-2 xl:gap-8">
          <AllocationChart />
          <TMFGGraph />
        </div>

        <BetaMatrix />

        <AllocationEvolution />

        <BetaEvolution />

        <VarChart />
        <CVarChart />

        <EfficientFrontier />

        {/* Distribuição e Stress Test lado a lado */}
        <div className="grid gap-6 lg:grid-cols-2 xl:gap-8">
          <ReturnsDistribution />
          <StressTestChart />
        </div>

        {/* Monte Carlo em largura total */}
        <MonteCarloDistribution />

        {/* Novos Componentes de Análise Avançada */}
        <div className="pt-10 border-t border-border">
          <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
            <LineChart className="h-8 w-8 text-primary" />
            <span>Análise Avançada</span>
          </h2>
        </div>

        <FamaFrenchPanel />

        <CAPMAnalysis />

        <MarkowitzOptimization />

        <div className="grid gap-6 lg:grid-cols-2 xl:gap-8">
          <RiskAttributionDetailed />
          <IncrementalVarAnalysis />
        </div>

        <VarBacktest />

        <ProfitabilityTable />

        <AssetsTable />
      </main>
    </div>
  )
}

export default withAuth(DashboardPage);