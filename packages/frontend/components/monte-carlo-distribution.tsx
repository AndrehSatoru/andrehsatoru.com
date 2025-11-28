"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { useMemo } from "react"

interface DistributionDataPoint {
  value: number
  valueLabel: string
  mgb: number
  bootstrap: number
}

interface MonteCarloData {
  distribution: DistributionDataPoint[]
  initialValue: number
  mgb: {
    median: number
    mean: number
    std: number
    percentile_5: number
    percentile_95: number
    drift_annual: number
    volatility_annual: number
  }
  bootstrap: {
    median: number
    mean: number
    std: number
    percentile_5: number
    percentile_95: number
  }
  params: {
    n_paths: number
    n_days: number
  }
}

const formatCurrency = (value: number) => {
  if (value >= 1_000_000_000) {
    return `R$ ${(value / 1_000_000_000).toFixed(2)}B`
  }
  return `R$ ${(value / 1_000_000).toFixed(1)}M`
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-background border border-border p-3 rounded-lg shadow-lg">
        <p className="font-semibold mb-1">{payload[0].payload.valueLabel}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }} className="text-sm">
            {entry.name}: {entry.value.toFixed(4)}
          </p>
        ))}
      </div>
    )
  }
  return null
}

export function MonteCarloDistribution() {
  const { analysisResult } = useDashboardData()
  
  // Obter dados de monte_carlo da API
  const monteCarloData: MonteCarloData | null = useMemo(() => {
    if (!analysisResult?.results?.monte_carlo?.distribution) {
      return null
    }
    return analysisResult.results.monte_carlo as MonteCarloData
  }, [analysisResult])
  
  // Calcular domínio do eixo Y dinamicamente
  const yDomain = useMemo(() => {
    if (!monteCarloData?.distribution) return [0, 2.5]
    
    const maxMgb = Math.max(...monteCarloData.distribution.map(d => d.mgb))
    const maxBootstrap = Math.max(...monteCarloData.distribution.map(d => d.bootstrap))
    const maxVal = Math.max(maxMgb, maxBootstrap)
    
    return [0, Math.ceil(maxVal * 1.2 * 10) / 10]
  }, [monteCarloData])
  
  // Encontrar o bin mais próximo do valor inicial para a linha de referência
  const initialValueLabel = useMemo(() => {
    if (!monteCarloData?.distribution || !monteCarloData.initialValue) return ""
    
    const initialValue = monteCarloData.initialValue
    // Encontrar o bin mais próximo
    let closestBin = monteCarloData.distribution[0]
    let minDist = Math.abs(monteCarloData.distribution[0].value - initialValue)
    
    for (const bin of monteCarloData.distribution) {
      const dist = Math.abs(bin.value - initialValue)
      if (dist < minDist) {
        minDist = dist
        closestBin = bin
      }
    }
    
    return closestBin.valueLabel
  }, [monteCarloData])

  // Estado vazio
  if (!monteCarloData || !monteCarloData.distribution?.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-balance">Distribuição Comparativa dos Resultados de Monte Carlo</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-[500px] items-center justify-center text-muted-foreground">
            Dados de simulação Monte Carlo não disponíveis
          </div>
        </CardContent>
      </Card>
    )
  }

  const { distribution, initialValue, mgb, bootstrap } = monteCarloData

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-balance">Distribuição Comparativa dos Resultados de Monte Carlo</CardTitle>
        <div className="flex flex-wrap gap-4 mt-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-[#F59E0B] border border-[#D97706]" />
            <span>MGB (Drift Anualizado: {mgb.drift_annual.toFixed(2)}%) com GARCH</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-[#6B7280] border border-[#4B5563]" />
            <span>Bootstrap Histórico</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className="w-4 h-0.5 bg-black border-dashed"
              style={{ borderTop: "2px dashed black", width: "20px" }}
            />
            <span>Valor Inicial: {formatCurrency(initialValue)}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[500px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={distribution}
              margin={{ top: 20, right: 30, left: 80, bottom: 60 }}
              barCategoryGap={0}
              barGap={-20}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="valueLabel"
                angle={-45}
                textAnchor="end"
                height={80}
                tick={{ fill: "hsl(var(--foreground))", fontSize: 11 }}
                label={{
                  value: "Valor Final da Carteira (R$)",
                  position: "insideBottom",
                  offset: -40,
                  style: { fill: "hsl(var(--foreground))", fontSize: 12 },
                }}
              />
              <YAxis
                tick={{ fill: "hsl(var(--foreground))", fontSize: 11 }}
                label={{
                  value: "Densidade",
                  angle: -90,
                  position: "insideLeft",
                  style: { fill: "hsl(var(--foreground))", fontSize: 12 },
                }}
                domain={yDomain}
              />
              <Tooltip content={<CustomTooltip />} />

              {/* Reference line for initial value */}
              {initialValueLabel && (
                <ReferenceLine x={initialValueLabel} stroke="#000" strokeDasharray="5 5" strokeWidth={2} />
              )}

              {/* Bars for distributions */}
              <Bar
                dataKey="mgb"
                fill="#F59E0B"
                fillOpacity={0.8}
                stroke="#D97706"
                strokeWidth={1}
                name="MGB com GARCH"
              />
              <Bar
                dataKey="bootstrap"
                fill="#6B7280"
                fillOpacity={0.8}
                stroke="#4B5563"
                strokeWidth={1}
                name="Bootstrap Histórico"
              />

              {/* Lines for smooth density curves */}
              <Line
                type="monotone"
                dataKey="mgb"
                stroke="#D97706"
                strokeWidth={2}
                dot={false}
                name=""
                legendType="none"
              />
              <Line
                type="monotone"
                dataKey="bootstrap"
                stroke="#374151"
                strokeWidth={2}
                dot={false}
                name=""
                legendType="none"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t">
          <div>
            <p className="text-sm text-muted-foreground">Valor Inicial</p>
            <p className="text-lg font-semibold">{formatCurrency(initialValue)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Mediana MGB</p>
            <p className="text-lg font-semibold text-amber-600">{formatCurrency(mgb.median)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Mediana Bootstrap</p>
            <p className="text-lg font-semibold text-gray-600">{formatCurrency(bootstrap.median)}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
