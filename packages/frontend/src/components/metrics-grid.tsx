"use client"

import { Card, CardContent } from "@/components/ui/card"
import { ArrowUpRight, ArrowDownRight, TrendingUp, Shield, Activity, Target } from "lucide-react"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { motion } from "framer-motion"
import { useRefreshAnimation } from "@/hooks/use-refresh-animation"

interface MetricItem {
  label: string
  value: string | number
  rawValue: number
  subValue: string | null
  change: string
  trend: "up" | "down"
  icon: any
  colorClass: string
  iconBgClass: string
}

function MetricCard({ item }: { item: MetricItem }) {
  const controls = useRefreshAnimation(item.rawValue)
  const Icon = item.icon
  const isPositive = item.trend === "up"

  return (
    <Card className="border-border hover:shadow-lg transition-all duration-300">
      <CardContent className="p-6 xl:p-7">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">{item.label}</p>
            <motion.div animate={controls} className="rounded-lg inline-block origin-left">
              <p className="text-3xl xl:text-4xl font-bold tracking-tight text-foreground">
                {item.value}
              </p>
            </motion.div>
            {item.subValue && (
              <p className="text-sm text-muted-foreground font-medium">{item.subValue}</p>
            )}
            {item.change && (
              <div className="flex items-center gap-1 mt-1">
                {isPositive ? (
                  <ArrowUpRight className="h-4 w-4 text-emerald-500" />
                ) : (
                  <ArrowDownRight className="h-4 w-4 text-rose-500" />
                )}
                <span className={`text-sm font-bold ${isPositive ? "text-emerald-500" : "text-rose-500"}`}>
                  {item.change}
                </span>
              </div>
            )}
          </div>
          <div className={`rounded-xl p-3 shadow-sm ${item.iconBgClass}`}>
            <Icon className={`h-6 w-6 ${item.colorClass}`} />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function MetricsGrid() {
  const { analysisResult } = useDashboardData()
  
  // Extrair dados do resultado da análise
  const desempenho = analysisResult?.desempenho || {}
  const alocacao = analysisResult?.alocacao || {}
  
  // Calcular valor total do portfólio
  const valorTotal = alocacao?.valor_total || 0
  
  const metrics: MetricItem[] = [
    {
      label: "Retorno Total",
      value: desempenho["retorno_total_%"] !== undefined 
        ? `${desempenho["retorno_total_%"].toFixed(2)}%`
        : "—",
      rawValue: desempenho["retorno_total_%"] || 0,
      subValue: valorTotal > 0 
        ? `R$ ${valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`
        : null,
      change: desempenho["retorno_anualizado_%"] !== undefined
        ? `${desempenho["retorno_anualizado_%"] > 0 ? '+' : ''}${desempenho["retorno_anualizado_%"].toFixed(2)}% a.a.`
        : "",
      trend: (desempenho["retorno_total_%"] || 0) >= 0 ? "up" : "down",
      icon: TrendingUp,
      colorClass: "text-emerald-600",
      iconBgClass: "bg-emerald-100 dark:bg-emerald-900/30",
    },
    {
      label: "Sharpe Ratio",
      value: desempenho["indice_sharpe"] !== undefined 
        ? desempenho["indice_sharpe"].toFixed(2)
        : "—",
      rawValue: desempenho["indice_sharpe"] || 0,
      subValue: null,
      change: "",
      trend: (desempenho["indice_sharpe"] || 0) >= 1 ? "up" : "down",
      icon: Target,
      colorClass: "text-blue-600",
      iconBgClass: "bg-blue-100 dark:bg-blue-900/30",
    },
    {
      label: "Volatilidade",
      value: desempenho["volatilidade_anual_%"] !== undefined 
        ? `${desempenho["volatilidade_anual_%"].toFixed(2)}%`
        : "—",
      rawValue: desempenho["volatilidade_anual_%"] || 0,
      subValue: null,
      change: "anual",
      trend: "down",
      icon: Activity,
      colorClass: "text-amber-600",
      iconBgClass: "bg-amber-100 dark:bg-amber-900/30",
    },
    {
      label: "VaR (95%)",
      value: desempenho["var_95%_1d_%"] !== undefined 
        ? `${desempenho["var_95%_1d_%"].toFixed(2)}%`
        : "—",
      rawValue: desempenho["var_95%_1d_%"] || 0,
      subValue: null,
      change: "1 dia",
      trend: "up",
      icon: Shield,
      colorClass: "text-rose-600",
      iconBgClass: "bg-rose-100 dark:bg-rose-900/30",
    },
  ]

  return (
    <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4 xl:gap-6">
      {metrics.map((metric) => (
        <MetricCard key={metric.label} item={metric} />
      ))}
    </div>
  )
}

