"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"

export function ReturnsDistribution() {
  const { analysisResult } = useDashboardData()
  
  const chartData = useMemo(() => {
    // Tentar usar dados reais do backend
    const backendData = analysisResult?.returns_distribution
    
    if (backendData && backendData.distribution && backendData.distribution.length > 0) {
      return {
        distribution: backendData.distribution,
        stats: backendData.stats,
        source: 'calculated' as const
      }
    }
    
    // Fallback: calcular a partir da série de performance
    const performance = analysisResult?.performance
    if (!performance || performance.length < 30) {
      return null
    }
    
    // Calcular retornos diários
    const returns: number[] = []
    for (let i = 1; i < performance.length; i++) {
      if (!performance[i] || !performance[i-1] || performance[i].portfolio === undefined || performance[i-1].portfolio === undefined) {
        continue
      }
      const ret = ((performance[i].portfolio - performance[i - 1].portfolio) / performance[i - 1].portfolio) * 100
      returns.push(ret)
    }
    
    // Criar bins para o histograma
    const binEdges = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
    const distribution = binEdges.slice(0, -1).map((edge, i) => {
      const nextEdge = binEdges[i + 1]
      const count = returns.filter(r => r >= edge && r < nextEdge).length
      return {
        range: `${edge}%`,
        frequency: count,
        returns: edge + 0.5
      }
    })
    
    // Calcular estatísticas
    const mean = returns.reduce((a, b) => a + b, 0) / returns.length
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length
    const std = Math.sqrt(variance)
    
    // Skewness
    const skewness = returns.reduce((sum, r) => sum + Math.pow((r - mean) / std, 3), 0) / returns.length
    
    // VaR e CVaR
    const sortedReturns = [...returns].sort((a, b) => a - b)
    const varIndex = Math.floor(returns.length * 0.05)
    const var95 = sortedReturns[varIndex]
    const cvar95 = sortedReturns.slice(0, varIndex + 1).reduce((a, b) => a + b, 0) / (varIndex + 1)
    
    return {
      distribution,
      stats: {
        mean: Math.round(mean * 100) / 100,
        std: Math.round(std * 100) / 100,
        skewness: Math.round(skewness * 100) / 100,
        var_95: Math.round(var95 * 100) / 100,
        cvar_95: Math.round(cvar95 * 100) / 100,
        n_observations: returns.length
      },
      source: 'calculated_frontend' as const
    }
  }, [analysisResult])
  
  if (!chartData) {
    return (
      <Card className="border-border hover:shadow-md transition-shadow">
        <CardHeader>
          <CardTitle className="text-foreground">Distribuição de Retornos</CardTitle>
          <CardDescription className="text-muted-foreground">
            Histograma com VaR e CVaR marcados (95% confiança)
          </CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[320px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar a distribuição de retornos</p>
        </CardContent>
      </Card>
    )
  }
  
  const { distribution, stats } = chartData
  const var95 = stats.var_95
  const cvar95 = stats.cvar_95
  
  // Encontrar o bin mais próximo do VaR para a linha de referência
  const varBin = distribution.find(d => d.returns <= var95)?.range || "-2%"
  const cvarBin = distribution.find(d => d.returns <= cvar95)?.range || "-3%"

  return (
    <Card className="border-border hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <CardTitle className="text-foreground text-lg">Distribuição de Retornos</CardTitle>
        <CardDescription className="text-muted-foreground text-sm">
          Histograma com VaR e CVaR marcados (95% confiança)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={distribution} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
            <XAxis 
              dataKey="range" 
              stroke="hsl(var(--muted-foreground))" 
              fontSize={11}
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
            />
            <YAxis
              stroke="hsl(var(--muted-foreground))"
              fontSize={11}
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
              width={50}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--popover))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              labelStyle={{ color: "hsl(var(--popover-foreground))" }}
              formatter={(value: number) => [value, "Frequência"]}
            />
            <Bar dataKey="frequency" radius={[4, 4, 0, 0]} maxBarSize={40}>
              {distribution.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.returns < var95 ? "hsl(var(--destructive))" : "hsl(var(--primary))"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 grid grid-cols-3 gap-3 rounded-lg bg-muted/50 p-4 text-center">
          <div>
            <p className="text-xs text-muted-foreground mb-0.5">Retorno Médio</p>
            <p className="text-lg font-bold text-foreground">{stats.mean}%</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-0.5">Desvio Padrão</p>
            <p className="text-lg font-bold text-foreground">{stats.std}%</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-0.5">Assimetria</p>
            <p className="text-lg font-bold text-foreground">{stats.skewness}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
