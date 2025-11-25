"use client"

import { Card, CardContent } from "@/components/ui/card"
import { ArrowUpRight, ArrowDownRight, TrendingUp, Shield, Activity, Target } from "lucide-react"
import { useDashboardData } from "@/lib/dashboard-data-context"

export function MetricsGrid() {
  const { analysisResult } = useDashboardData()
  
  // Extrair dados do resultado da análise
  const desempenho = analysisResult?.results?.desempenho || {}
  const alocacao = analysisResult?.results?.alocacao || {}
  
  // Calcular valor total do portfólio
  const valorTotal = alocacao?.valor_total || 0
  
  const metrics = [
    {
      label: "Retorno Total",
      value: desempenho["retorno_total_%"] !== undefined 
        ? `${desempenho["retorno_total_%"].toFixed(2)}%`
        : "—",
      subValue: valorTotal > 0 
        ? `R$ ${valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
        : null,
      change: desempenho["retorno_anualizado_%"] !== undefined
        ? `${desempenho["retorno_anualizado_%"] > 0 ? '+' : ''}${desempenho["retorno_anualizado_%"].toFixed(2)}% a.a.`
        : "",
      trend: (desempenho["retorno_total_%"] || 0) >= 0 ? "up" : "down",
      icon: TrendingUp,
      color: "text-success",
    },
    {
      label: "Sharpe Ratio",
      value: desempenho["indice_sharpe"] !== undefined 
        ? desempenho["indice_sharpe"].toFixed(2)
        : "—",
      change: "",
      trend: (desempenho["indice_sharpe"] || 0) >= 1 ? "up" : "down",
      icon: Target,
      color: "text-primary",
    },
    {
      label: "Volatilidade",
      value: desempenho["volatilidade_anual_%"] !== undefined 
        ? `${desempenho["volatilidade_anual_%"].toFixed(2)}%`
        : "—",
      change: "anual",
      trend: "down",
      icon: Activity,
      color: "text-secondary",
    },
    {
      label: "VaR (95%)",
      value: desempenho["var_95%_1d_%"] !== undefined 
        ? `${desempenho["var_95%_1d_%"].toFixed(2)}%`
        : "—",
      change: "1 dia",
      trend: "up",
      icon: Shield,
      color: "text-accent",
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {metrics.map((metric) => {
        const Icon = metric.icon
        const isPositive = metric.trend === "up"

        return (
          <Card key={metric.label} className="border-border">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <p className="text-sm font-medium text-muted-foreground">{metric.label}</p>
                  <p className="text-2xl font-bold tracking-tight text-foreground">{metric.value}</p>
                  {metric.subValue && (
                    <p className="text-sm text-muted-foreground">{metric.subValue}</p>
                  )}
                  {metric.change && (
                    <div className="flex items-center gap-1">
                      {isPositive ? (
                        <ArrowUpRight className="h-4 w-4 text-success" />
                      ) : (
                        <ArrowDownRight className="h-4 w-4 text-destructive" />
                      )}
                      <span className={`text-sm font-medium ${isPositive ? "text-success" : "text-destructive"}`}>
                        {metric.change}
                      </span>
                    </div>
                  )}
                </div>
                <div className={`rounded-lg bg-muted p-2.5 ${metric.color}`}>
                  <Icon className="h-5 w-5" />
                </div>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
