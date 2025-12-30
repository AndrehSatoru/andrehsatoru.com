"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Cell, CartesianGrid, Area } from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { DASHBOARD_COLORS } from "@/lib/colors"
import { motion } from "framer-motion"

export function ReturnsDistribution() {
  const { analysisResult } = useDashboardData()
  
  const chartData = useMemo(() => {
    // Tentar usar dados reais do backend ou calcular fallback
    let returns: number[] = []
    
    // 1. Tentar pegar retornos brutos se disponíveis (ideal para recalcular bins)
    // Se não tiver, tentar reconstruir da performance
    const performance = analysisResult?.performance
    
    if (performance && performance.length > 30) {
      for (let i = 1; i < performance.length; i++) {
        if (!performance[i] || !performance[i-1] || performance[i].portfolio === undefined || performance[i-1].portfolio === undefined) {
          continue
        }
        const ret = ((performance[i].portfolio - performance[i - 1].portfolio) / performance[i - 1].portfolio)
        if (!isNaN(ret) && isFinite(ret)) {
          returns.push(ret)
        }
      }
    }

    if (returns.length === 0) return null

    // Estatísticas Básicas
    const mean = returns.reduce((a, b) => a + b, 0) / returns.length
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length
    const std = Math.sqrt(variance)
    const skewness = returns.reduce((sum, r) => sum + Math.pow((r - mean) / std, 3), 0) / returns.length
    
    // VaR e CVaR (95%)
    const sortedReturns = [...returns].sort((a, b) => a - b)
    const varIndex = Math.floor(returns.length * 0.05)
    const var95 = sortedReturns[varIndex]
    const cvar95 = sortedReturns.slice(0, varIndex + 1).reduce((a, b) => a + b, 0) / (varIndex + 1)

    // Configuração Dinâmica dos Bins
    const minRet = Math.min(...returns)
    const maxRet = Math.max(...returns)
    
    // Padding de 10% no range
    const range = maxRet - minRet
    const paddedMin = minRet - (range * 0.1)
    const paddedMax = maxRet + (range * 0.1)
    
    // Número de bins baseado na regra de Freedman-Diaconis simplificada ou fixo em ~40
    const numBins = Math.min(50, Math.max(20, Math.ceil(Math.sqrt(returns.length))))
    const binWidth = (paddedMax - paddedMin) / numBins
    
    const histogramData: any[] = []
    let maxFrequency = 0
    
    for (let i = 0; i < numBins; i++) {
      const binStart = paddedMin + (i * binWidth)
      const binEnd = binStart + binWidth
      const binCenter = binStart + (binWidth / 2)
      
      const count = returns.filter(r => r >= binStart && r < binEnd).length
      const frequency = count / returns.length // Densidade relativa
      
      if (frequency > maxFrequency) maxFrequency = frequency
      
      // Cálculo da Curva Normal (PDF) para este ponto
      // f(x) = (1 / (σ√(2π))) * e^(-0.5 * ((x-μ)/σ)^2)
      // Multiplicamos pelo binWidth para ter a probabilidade no bin (comparável com frequência relativa)
      const normalValue = (1 / (std * Math.sqrt(2 * Math.PI))) * 
                          Math.exp(-0.5 * Math.pow((binCenter - mean) / std, 2)) * 
                          binWidth

      histogramData.push({
        rangeStart: binStart * 100,
        rangeEnd: binEnd * 100,
        binCenter: binCenter * 100, // Para eixo X (em %)
        frequency: count, // Contagem absoluta para barras
        density: frequency, // Densidade para curva (se quiséssemos normalizar)
        normalCurve: normalValue * returns.length, // Escalar curva para contagem absoluta
        tooltipLabel: `${(binStart * 100).toFixed(2)}% a ${(binEnd * 100).toFixed(2)}%`
      })
    }

    return {
      distribution: histogramData,
      stats: {
        mean: mean * 100,
        std: std * 100,
        skewness: skewness,
        var_95: var95 * 100,
        cvar_95: cvar95 * 100,
        min: minRet * 100,
        max: maxRet * 100,
        n_observations: returns.length
      }
    }
  }, [analysisResult])
  
  if (!chartData) {
    return (
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <Card className="border-2 border-border/60">
          <CardHeader>
            <CardTitle className="text-foreground">Distribuição de Retornos</CardTitle>
            <CardDescription>Histograma com Curva Normal Ajustada</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-center h-[320px]">
            <p className="text-muted-foreground text-sm">Dados insuficientes para gerar distribuição.</p>
          </CardContent>
        </Card>
      </motion.div>
    )
  }
  
  const { distribution, stats } = chartData

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      <Card className="border-2 border-border/60 hover:shadow-lg transition-all duration-300 overflow-hidden">
        <CardHeader className="pb-3 bg-gradient-to-r from-transparent to-muted/20">
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-foreground text-xl">Distribuição de Retornos</CardTitle>
              <CardDescription className="text-muted-foreground text-sm mt-1">
                Frequência de retornos diários vs. Curva Normal Teórica
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="p-4">
          <div className="h-[320px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={distribution} margin={{ top: 20, right: 10, left: 0, bottom: 20 }}>
                <defs>
                  <linearGradient id="barGradientNorm" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity={0.8} />
                    <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                  </linearGradient>
                  <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={DASHBOARD_COLORS.warning} stopOpacity={0.4} />
                    <stop offset="100%" stopColor={DASHBOARD_COLORS.warning} stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} vertical={false} />
                
                <XAxis 
                  dataKey="binCenter" 
                  stroke="hsl(var(--muted-foreground))" 
                  fontSize={11}
                  tickFormatter={(val) => `${val.toFixed(1)}%`}
                  tickLine={false}
                  axisLine={false}
                  minTickGap={30}
                  label={{ value: "Retorno Diário (%)", position: 'insideBottom', offset: -10, fill: "hsl(var(--muted-foreground))", fontSize: 11 }}
                />
                
                <YAxis 
                  stroke="hsl(var(--muted-foreground))" 
                  fontSize={11}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(val) => Math.floor(val).toString()}
                  width={30}
                />
                
                <Tooltip
                  cursor={{ fill: 'hsl(var(--muted)/0.2)' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload
                      return (
                        <div className="rounded-xl border bg-background/95 p-3 shadow-xl backdrop-blur-md text-xs">
                          <div className="font-semibold mb-2 text-foreground">
                            {data.tooltipLabel}
                          </div>
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <div className="h-2 w-2 rounded-full bg-primary" />
                              <span className="text-muted-foreground">Frequência:</span>
                              <span className="font-mono font-medium text-foreground">{data.frequency} dias</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <div className="h-2 w-2 rounded-full bg-yellow-500" />
                              <span className="text-muted-foreground">Normal Teórica:</span>
                              <span className="font-mono font-medium text-foreground">{data.normalCurve.toFixed(1)}</span>
                            </div>
                          </div>
                        </div>
                      )
                    }
                    return null
                  }}
                />

                {/* Área sob a curva normal para efeito visual */}
                <Area
                  type="monotone"
                  dataKey="normalCurve"
                  fill="url(#areaGradient)"
                  stroke="none"
                  animationDuration={1500}
                />

                {/* Barras do Histograma */}
                <Bar dataKey="frequency" barSize={20} radius={[4, 4, 0, 0]} animationDuration={1500}>
                  {distribution.map((entry: any, index: number) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.binCenter < 0 ? "hsl(var(--destructive))" : "hsl(var(--primary))"} 
                      opacity={entry.binCenter < 0 ? 0.6 : 0.7}
                    />
                  ))}
                </Bar>

                {/* Linha da Curva Normal */}
                <Line
                  type="monotone"
                  dataKey="normalCurve"
                  stroke={DASHBOARD_COLORS.warning}
                  strokeWidth={2}
                  dot={false}
                  activeDot={false}
                  animationDuration={1500}
                  animationBegin={300}
                />

                {/* Reference Lines */}
                <ReferenceLine 
                  x={stats.mean} 
                  stroke="hsl(var(--foreground))" 
                  strokeDasharray="3 3" 
                  opacity={0.5}
                >
                </ReferenceLine>

                <ReferenceLine 
                  x={stats.var_95} 
                  stroke={DASHBOARD_COLORS.negative} 
                  strokeDasharray="4 4" 
                  label={{ value: "VaR 95%", position: 'top', fill: DASHBOARD_COLORS.negative, fontSize: 10 }}
                />

              </ComposedChart>
            </ResponsiveContainer>
          </div>

          {/* Stats Grid Refinado */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-2">
            <div className="flex flex-col p-2 rounded-lg bg-muted/30 border border-border/50">
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">Média Diária</span>
              <div className="flex items-baseline gap-1">
                <span className={`text-lg font-bold ${stats.mean >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                  {stats.mean > 0 ? '+' : ''}{stats.mean.toFixed(3)}%
                </span>
              </div>
            </div>

            <div className="flex flex-col p-2 rounded-lg bg-muted/30 border border-border/50">
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">Volatilidade (σ)</span>
              <span className="text-lg font-bold text-blue-500">
                {stats.std.toFixed(3)}%
              </span>
            </div>

            <div className="flex flex-col p-2 rounded-lg bg-muted/30 border border-border/50">
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground font-semibold">Assimetria</span>
              <span className={`text-lg font-bold ${stats.skewness < 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                {stats.skewness.toFixed(3)}
              </span>
            </div>

            <div className="flex flex-col p-2 rounded-lg bg-rose-500/10 border border-rose-500/20">
              <span className="text-[10px] uppercase tracking-wider text-rose-500 font-semibold">VaR (95%)</span>
              <span className="text-lg font-bold text-rose-500">
                {stats.var_95.toFixed(2)}%
              </span>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}


