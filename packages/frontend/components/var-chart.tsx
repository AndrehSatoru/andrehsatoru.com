"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Bar,
  ComposedChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Line,
  Scatter,
  Cell,
} from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"

export function VarChart() {
  const { analysisResult } = useDashboardData()

  const chartData = useMemo(() => {
    if (!analysisResult?.results?.performance || analysisResult.results.performance.length < 2) {
      return null
    }

    const performanceData = analysisResult.results.performance
    
    // Calcular retornos monetários diários a partir da série de performance
    const returns: number[] = []

    for (let i = 1; i < performanceData.length; i++) {
      const prevValue = performanceData[i - 1].portfolio
      const currValue = performanceData[i].portfolio
      const dailyReturn = currValue - prevValue // Retorno monetário
      returns.push(dailyReturn)
    }

    if (returns.length < 20) {
      return null // Dados insuficientes para calcular VaR
    }

    // Função para calcular percentil com interpolação linear
    const percentile = (sortedArr: number[], p: number): number => {
      const index = (sortedArr.length - 1) * p
      const lower = Math.floor(index)
      const upper = Math.ceil(index)
      const weight = index - lower
      if (upper >= sortedArr.length) return sortedArr[lower]
      return sortedArr[lower] * (1 - weight) + sortedArr[upper] * weight
    }

    // Janela móvel para VaR dinâmico (até 252 dias úteis = 1 ano)
    const maxWindowSize = 252
    const minWindowSize = 20
    const data = []
    let violationCount = 0

    // Calcular VaR rolling para cada ponto, usando janela adaptativa
    for (let i = minWindowSize; i < returns.length; i++) {
      // Janela cresce até maxWindowSize
      const windowSize = Math.min(i, maxWindowSize)
      const windowReturns = returns.slice(i - windowSize, i)
      const sortedWindow = [...windowReturns].sort((a, b) => a - b)
      
      // VaR com interpolação linear para suavizar
      const var95 = percentile(sortedWindow, 0.05)
      const var99 = percentile(sortedWindow, 0.01)

      const dailyReturn = returns[i]
      const isViolation = dailyReturn < var99
      if (isViolation) violationCount++

      data.push({
        date: performanceData[i + 1].date,
        returns: dailyReturn,
        var95: var95,
        var99: var99,
        violation: isViolation ? dailyReturn : null,
      })
    }

    // Calcular valores atuais (último ponto)
    const lastPoint = data[data.length - 1]
    const currentVar95 = lastPoint?.var95 || 0
    const currentVar99 = lastPoint?.var99 || 0

    return { data, violationCount, var95: currentVar95, var99: currentVar99 }
  }, [analysisResult])

  const formatValue = (value: number) => {
    if (Math.abs(value) >= 1000000) {
      return `R$ ${(value / 1000000).toFixed(2)}M`
    } else if (Math.abs(value) >= 1000) {
      return `R$ ${(value / 1000).toFixed(0)}K`
    }
    return `R$ ${value.toFixed(0)}`
  }

  if (!chartData) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Retorno Monetário Diário vs. VaR Histórico Diário</CardTitle>
          <CardDescription className="text-muted-foreground">
            Retornos diários da carteira comparados aos limites de VaR
          </CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[400px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar o VaR</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Retorno Monetário Diário vs. VaR Histórico Diário</CardTitle>
        <CardDescription className="text-muted-foreground">
          Retornos diários da carteira comparados aos limites de VaR
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={450}>
          <ComposedChart data={chartData.data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
            <XAxis
              dataKey="date"
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`
              }}
              interval={Math.floor(chartData.data.length / 6)}
            />
            <YAxis
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickFormatter={(value) => {
                if (Math.abs(value) >= 1000000) {
                  return `R$ ${(value / 1000000).toFixed(1)}M`
                } else if (Math.abs(value) >= 1000) {
                  return `R$ ${(value / 1000).toFixed(0)}K`
                }
                return `R$ ${value.toFixed(0)}`
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--popover))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              labelStyle={{ color: "hsl(var(--popover-foreground))" }}
              formatter={(value: number, name: string) => {
                const formatted = `R$ ${value.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                return [formatted, name]
              }}
              labelFormatter={(label) => {
                const date = new Date(label)
                return date.toLocaleDateString("pt-BR")
              }}
            />
            {/* Linha VaR 99% Rolling */}
            <Line
              type="monotone"
              dataKey="var99"
              stroke="#dc2626"
              strokeWidth={2}
              dot={false}
              name="VaR 99% (Rolling 252d)"
            />
            {/* Linha VaR 95% Rolling */}
            <Line
              type="monotone"
              dataKey="var95"
              stroke="#f97316"
              strokeWidth={2}
              strokeDasharray="5 3"
              dot={false}
              name="VaR 95% (Rolling 252d)"
            />
            <Bar dataKey="returns" name="Retorno Monetário Diário" radius={[2, 2, 0, 0]} minPointSize={1}>
              {chartData.data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.returns >= 0 ? "hsl(142, 76%, 36%)" : "hsl(0, 84%, 60%)"} />
              ))}
            </Bar>
            <Scatter
              dataKey="violation"
              fill="#eab308"
              stroke="#000"
              strokeWidth={2}
              name={`Quebras do VaR (99%)`}
            />
          </ComposedChart>
        </ResponsiveContainer>
        <div className="mt-5 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 rounded-lg bg-muted/50 border border-border px-4 py-3">
          {/* Métricas com valores */}
          <div className="flex items-center gap-2">
            <div className="h-[3px] w-6 rounded-full bg-red-600" />
            <span className="text-sm"><span className="text-muted-foreground">VaR 99%:</span> <span className="font-semibold text-red-600">{formatValue(chartData.var99)}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-[3px] w-6 rounded-full" style={{ background: 'repeating-linear-gradient(90deg, #f97316, #f97316 3px, transparent 3px, transparent 6px)' }} />
            <span className="text-sm"><span className="text-muted-foreground">VaR 95%:</span> <span className="font-semibold text-orange-500">{formatValue(chartData.var95)}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-yellow-500 ring-1 ring-black/20" />
            <span className="text-sm"><span className="text-muted-foreground">Quebras:</span> <span className="font-semibold text-yellow-600">{chartData.violationCount}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Taxa Violação:</span> <span className="font-semibold text-foreground">{((chartData.violationCount / chartData.data.length) * 100).toFixed(2)}%</span></span>
          </div>
          <div className="h-4 w-px bg-border" />
          <div className="flex items-center gap-2">
            <div className="h-3 w-4 rounded-sm bg-green-600" />
            <span className="text-sm text-muted-foreground">Positivo</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-4 rounded-sm bg-red-500" />
            <span className="text-sm text-muted-foreground">Negativo</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
