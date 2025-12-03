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
import { EfficientFrontier } from "@/components/efficient-frontier"
import { CorrelationMatrix } from "@/components/correlation-matrix"
import { AllocationEvolution } from "@/components/allocation-evolution"
import { RollingReturns } from "@/components/rolling-returns"
import { RiskContribution } from "@/components/risk-contribution"
import { BetaMatrix } from "@/components/beta-matrix"
import { MonteCarloDistribution } from "@/components/monte-carlo-distribution"
import { BetaEvolution } from "@/components/beta-evolution"
import { ProfitabilityTable } from "@/components/profitability-table"
import { FamaFrenchPanel } from "@/components/fama-french-panel"
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
          <AllocationChart />
        </div>

        <VarChart />
        <CVarChart />

        <EfficientFrontier />
        
        <BetaMatrix />

        <AllocationEvolution />

        <RiskContribution />

        <BetaEvolution />

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