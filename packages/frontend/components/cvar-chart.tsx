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

export function CVarChart() {
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
      return null // Dados insuficientes para calcular CVaR
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

    // Janela móvel para CVaR dinâmico (até 252 dias úteis = 1 ano)
    const maxWindowSize = 252
    const minWindowSize = 20
    const data = []
    let violationCount = 0

    // Calcular CVaR rolling para cada ponto, usando janela adaptativa
    for (let i = minWindowSize; i < returns.length; i++) {
      // Janela cresce até maxWindowSize
      const windowSize = Math.min(i, maxWindowSize)
      const windowReturns = returns.slice(i - windowSize, i)
      const sortedWindow = [...windowReturns].sort((a, b) => a - b)
      
      // VaR com interpolação linear
      const var95 = percentile(sortedWindow, 0.05)
      
      // CVaR é a média dos retornos abaixo do VaR (Expected Shortfall)
      const var95Index = Math.ceil(windowSize * 0.05)
      const tailReturns = sortedWindow.slice(0, var95Index + 1)
      const cvar95 = tailReturns.length > 0 
        ? tailReturns.reduce((sum, r) => sum + r, 0) / tailReturns.length 
        : var95

      const dailyReturn = returns[i]
      const isViolation = dailyReturn < cvar95
      if (isViolation) violationCount++

      data.push({
        date: performanceData[i + 1].date,
        returns: dailyReturn,
        var95: var95,
        cvar95: cvar95,
        violation: isViolation ? dailyReturn : null,
      })
    }

    // Calcular valores atuais (último ponto)
    const lastPoint = data[data.length - 1]
    const currentVar95 = lastPoint?.var95 || 0
    const currentCvar95 = lastPoint?.cvar95 || 0
    
    // Calcular diferença percentual CVaR/VaR
    const diffPercent = currentVar95 !== 0 ? ((currentCvar95 - currentVar95) / Math.abs(currentVar95)) * 100 : 0

    return { data, var95: currentVar95, cvar95: currentCvar95, diffPercent, violationCount }
  }, [analysisResult])

  const formatValue = (value: number) => {
    if (Math.abs(value) >= 1000000) {
      return `R$ ${(value / 1000000).toFixed(2)}M`
    } else if (Math.abs(value) >= 1000) {
      return `R$ ${(value / 1000).toFixed(0)}K`
    }
    return `R$ ${value.toFixed(2)}`
  }

  if (!chartData) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">CVaR (Conditional Value at Risk)</CardTitle>
          <CardDescription className="text-muted-foreground">
            Perda média esperada além do VaR - Expected Shortfall
          </CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[400px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar o CVaR</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">CVaR (Conditional Value at Risk)</CardTitle>
        <CardDescription className="text-muted-foreground">
          Perda média esperada além do VaR - Expected Shortfall
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
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
                return [
                  `R$ ${value.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
                  name,
                ]
              }}
              labelFormatter={(label) => {
                const date = new Date(label)
                return date.toLocaleDateString("pt-BR")
              }}
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
            {/* Linha CVaR 95% Rolling */}
            <Line
              type="monotone"
              dataKey="cvar95"
              stroke="#dc2626"
              strokeWidth={2}
              dot={false}
              name="CVaR 95% (Rolling 252d)"
            />
            <Scatter
              dataKey="violation"
              fill="#eab308"
              stroke="#000"
              strokeWidth={2}
              name="Quebras do CVaR (95%)"
            />
            <Bar dataKey="returns" name="Retorno Diário" radius={[2, 2, 0, 0]}>
              {chartData.data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.returns >= 0 ? "hsl(142, 76%, 36%)" : "hsl(0, 84%, 60%)"} />
              ))}
            </Bar>
          </ComposedChart>
        </ResponsiveContainer>
        <div className="mt-4 grid grid-cols-4 gap-4 rounded-lg bg-muted p-4">
          <div>
            <p className="text-xs text-muted-foreground">VaR 95% Atual</p>
            <p className="text-lg font-bold text-orange-500">{formatValue(chartData.var95)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">CVaR 95% Atual</p>
            <p className="text-lg font-bold text-red-600">{formatValue(chartData.cvar95)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Quebras CVaR 95%</p>
            <p className="text-lg font-bold text-yellow-500">{chartData.violationCount}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Diferença CVaR/VaR</p>
            <p className="text-lg font-bold text-amber-600">
              {chartData.diffPercent > 0 ? "+" : ""}{chartData.diffPercent.toFixed(0)}%
            </p>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="h-0.5 w-8 bg-orange-500" style={{ borderStyle: 'dashed', borderWidth: '2px', borderColor: '#f97316' }} />
            <span className="text-muted-foreground">VaR 95% (Rolling 252d)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-0.5 w-8 bg-red-600" />
            <span className="text-muted-foreground">CVaR 95% (Rolling 252d)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-yellow-500 ring-2 ring-black" />
            <span className="text-muted-foreground">Quebras do CVaR: {chartData.violationCount}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-8 bg-green-600" />
            <span className="text-muted-foreground">Retorno Positivo</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-8 bg-red-500" />
            <span className="text-muted-foreground">Retorno Negativo</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
