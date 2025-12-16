"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { useDashboardData } from "@/lib/dashboard-data-context"

export function RiskMetrics() {
  const { analysisResult } = useDashboardData()
  
  const desempenho = analysisResult?.desempenho || {}
  
  const riskMetrics = [
    { 
      label: "Volatilidade Anual", 
      value: desempenho["volatilidade_anual_%"] || 0, 
      max: 50, 
      color: "bg-primary",
      suffix: "%"
    },
    { 
      label: "Sharpe Ratio", 
      value: desempenho["indice_sharpe"] || 0, 
      max: 3, 
      color: "bg-secondary",
      suffix: ""
    },
    { 
      label: "VaR 95%", 
      value: Math.abs(desempenho["var_95%_1d_%"] || 0), 
      max: 10, 
      color: "bg-accent",
      suffix: "%"
    },
  ]

  const maxDrawdown = desempenho["max_drawdown_%"] || 0
  const es95 = desempenho["es_95%_1d_%"] || 0
  const diasAnalisados = desempenho["dias_analisados"] || 0

  return (
    <Card className="border-border hover:shadow-md transition-shadow">
      <CardHeader>
        <CardTitle className="text-foreground">Métricas de Risco</CardTitle>
        <CardDescription className="text-muted-foreground">Indicadores ajustados ao risco</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        {riskMetrics.map((metric) => (
          <div key={metric.label} className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-foreground">{metric.label}</span>
              <span className="text-base font-bold text-foreground">
                {metric.value.toFixed(2)}{metric.suffix}
              </span>
            </div>
            <Progress value={Math.min((Math.abs(metric.value) / metric.max) * 100, 100)} className="h-2.5" />
          </div>
        ))}

        <div className="mt-6 space-y-4 rounded-xl bg-muted p-5">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Drawdown Máximo</span>
            <span className="text-base font-semibold text-destructive">
              {maxDrawdown.toFixed(2)}%
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Expected Shortfall (95%)</span>
            <span className="text-base font-semibold text-foreground">
              {es95.toFixed(2)}%
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Dias Analisados</span>
            <span className="text-base font-semibold text-foreground">{diasAnalisados}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
