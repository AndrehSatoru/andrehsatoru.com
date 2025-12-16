"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
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
          entry.name && entry.name !== "" && (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: {entry.value.toFixed(2)}%
            </p>
          )
        ))}
      </div>
    )
  }
  return null
}

export function MonteCarloDistribution() {
  const { analysisResult } = useDashboardData()
  
  // Obter dados de monte_carlo da API
  const monteCarloData = analysisResult.monte_carlo as MonteCarloData
  
  // Calcular domínio do eixo Y dinamicamente (valores agora são em %)
  const yDomain = useMemo(() => {
    if (!monteCarloData?.distribution) return [0, 25]
    
    const maxMgb = Math.max(...monteCarloData.distribution.map(d => d.mgb))
    const maxBootstrap = Math.max(...monteCarloData.distribution.map(d => d.bootstrap))
    const maxVal = Math.max(maxMgb, maxBootstrap)
    
    // Arredondar para cima com margem de 20%
    return [0, Math.ceil(maxVal * 1.2)]
  }, [monteCarloData])

  // Estado vazio
  if (!monteCarloData || !monteCarloData.distribution?.length) {
    return (
      <Card className="border-border hover:shadow-md transition-shadow">
        <CardHeader>
          <CardTitle className="text-balance text-foreground">Distribuição Comparativa dos Resultados de Monte Carlo</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-[400px] items-center justify-center text-muted-foreground">
            Dados de simulação Monte Carlo não disponíveis
          </div>
        </CardContent>
      </Card>
    )
  }

  const { distribution, initialValue, mgb, bootstrap } = monteCarloData

  return (
    <Card className="border-border hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <CardTitle className="text-foreground text-lg">Simulação Monte Carlo</CardTitle>
        <CardDescription className="text-muted-foreground text-sm">
          Distribuição comparativa de cenários futuros
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Legenda no topo */}
        <div className="flex flex-wrap items-center gap-6 mb-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-amber-500" />
            <span className="text-muted-foreground">MGB ({(mgb.drift_annual ?? 0).toFixed(1)}% drift)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-gray-500" />
            <span className="text-muted-foreground">Bootstrap Histórico</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-5 border-t-2 border-dashed border-foreground" />
            <span className="text-muted-foreground">Valor Inicial: {formatCurrency(initialValue)}</span>
          </div>
        </div>

        {/* Gráfico */}
        <div className="h-[450px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={distribution}
              margin={{ top: 20, right: 30, left: 60, bottom: 70 }}
              barCategoryGap={0}
              barGap={-15}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="value"
                type="number"
                domain={['dataMin', 'dataMax']}
                angle={-45}
                textAnchor="end"
                height={60}
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                tickFormatter={(value) => {
                  if (value >= 1_000_000_000) return `R$ ${(value / 1_000_000_000).toFixed(1)}B`
                  if (value >= 1_000_000) return `R$ ${(value / 1_000_000).toFixed(1)}M`
                  return `R$ ${(value / 1_000).toFixed(0)}K`
                }}
                tickCount={12}
              />
              <YAxis
                tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                width={50}
                domain={yDomain}
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip content={<CustomTooltip />} />

              {/* Reference line for initial value - linha pontilhada vertical */}
              <ReferenceLine 
                x={initialValue} 
                stroke="#000" 
                strokeDasharray="5 5" 
                strokeWidth={2}
                label={{ 
                  value: 'Valor Inicial', 
                  position: 'top',
                  fill: 'hsl(var(--foreground))',
                  fontSize: 11
                }}
              />

              {/* Bars for distributions */}
              <Bar
                dataKey="mgb"
                fill="#F59E0B"
                fillOpacity={0.8}
                stroke="#D97706"
                strokeWidth={1}
                name="MGB"
                maxBarSize={30}
              />
              <Bar
                dataKey="bootstrap"
                fill="#6B7280"
                fillOpacity={0.6}
                stroke="#4B5563"
                strokeWidth={1}
                name="Bootstrap Histórico"
                maxBarSize={30}
              />

              {/* Lines for density curves */}
              <Line
                type="monotone"
                dataKey="mgb"
                stroke="#B45309"
                strokeWidth={2}
                dot={false}
                name=""
                legendType="none"
              />
              <Line
                type="monotone"
                dataKey="bootstrap"
                stroke="#1F2937"
                strokeWidth={2}
                dot={false}
                name=""
                legendType="none"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Cards de estatísticas */}
        <div className="grid grid-cols-3 gap-4 mt-5 pt-4 border-t border-border">
          <div className="text-center p-3 rounded-lg bg-muted/50">
            <p className="text-xs text-muted-foreground mb-0.5">Valor Inicial</p>
            <p className="text-lg font-bold text-foreground">{formatCurrency(initialValue)}</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-amber-50 dark:bg-amber-950/30">
            <p className="text-xs text-muted-foreground mb-0.5">Mediana MGB</p>
            <p className="text-lg font-bold text-amber-600">{formatCurrency(mgb.median)}</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-gray-100 dark:bg-gray-800/50">
            <p className="text-xs text-muted-foreground mb-0.5">Mediana Bootstrap</p>
            <p className="text-lg font-bold text-gray-600 dark:text-gray-400">{formatCurrency(bootstrap.median)}</p>
          </div>
        </div>

        {/* Legenda explicativa */}
        <div className="mt-4 p-4 bg-muted/50 rounded-lg text-xs space-y-1">
          <p><strong>MGB (Movimento Browniano Geométrico):</strong> Modelo paramétrico que assume retornos log-normais. Usa média e volatilidade históricas para projetar cenários futuros.</p>
          <p><strong>Bootstrap Histórico:</strong> Método não-paramétrico que reamostra retornos reais do passado. Captura caudas pesadas e assimetrias da distribuição real.</p>
          <p><strong>Drift:</strong> Retorno médio esperado anualizado, baseado no histórico da carteira.</p>
          <p><strong>Interpretação:</strong> Se as duas distribuições são similares, o modelo paramétrico é adequado. Divergências indicam que a distribuição real tem características não capturadas pelo MGB.</p>
        </div>
      </CardContent>
    </Card>
  )
}
