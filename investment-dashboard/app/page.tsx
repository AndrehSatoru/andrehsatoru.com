import { DashboardHeader } from "@/components/dashboard-header"
import { MetricsGrid } from "@/components/metrics-grid"
import { PerformanceChart } from "@/components/performance-chart"
import { AllocationChart } from "@/components/allocation-chart"
import { RiskMetrics } from "@/components/risk-metrics"
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
import Link from "next/link"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />

      <main className="container mx-auto px-4 py-6 space-y-6">
        <div className="flex justify-end">
          <Link href="/enviar" className="rounded-md bg-primary text-primary-foreground px-4 py-2 text-sm">
            Enviar Operações
          </Link>
        </div>
        <MetricsGrid />

        <div className="grid gap-6 lg:grid-cols-2">
          <PerformanceChart />
          <AllocationChart />
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <RiskMetrics />
          <VolatilityChart />
          <DrawdownChart />
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <VarChart />
          <CVarChart />
        </div>

        <EfficientFrontier />

        <div className="grid gap-6 lg:grid-cols-2">
          <CorrelationMatrix />
          <BetaMatrix />
        </div>

        <AllocationEvolution />

        <RollingReturns />

        <RiskContribution />

        <BetaEvolution />

        <div className="grid gap-6 lg:grid-cols-3">
          <ReturnsDistribution />
          <StressTestChart />
        </div>

        <MonteCarloDistribution />

        <ProfitabilityTable />

        <AssetsTable />
      </main>
    </div>
  )
}
