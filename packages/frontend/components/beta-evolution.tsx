"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Brush } from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { useMemo } from "react"
import { DASHBOARD_COLORS } from "@/lib/colors"

interface BetaDataPoint {
  date: string
  beta: number
}

export function BetaEvolution() {
  const { analysisResult } = useDashboardData()
  
  // Obter dados de beta_evolution da API
  const data: BetaDataPoint[] = useMemo(() => {
    if (!analysisResult?.beta_evolution) {
      return []
    }
    return analysisResult.beta_evolution
  }, [analysisResult])
  
  // Calcular estatísticas (filtrando valores muito baixos que indicam início da carteira)
  const stats = useMemo(() => {
    if (data.length === 0) {
      return { currentBeta: 0, avgBeta: 0, minBeta: 0, maxBeta: 0 }
    }
    
    // Filtrar valores maiores que 0.1 para evitar betas artificialmente baixos do início
    const validBetaValues = data
      .map((d) => d.beta)
      .filter((b) => typeof b === 'number' && !isNaN(b) && b > 0.1)
    
    if (validBetaValues.length === 0) {
      return { currentBeta: 0, avgBeta: 0, minBeta: 0, maxBeta: 0 }
    }
    
    const currentBeta = data[data.length - 1].beta
    const avgBeta = validBetaValues.reduce((sum, b) => sum + b, 0) / validBetaValues.length
    const minBeta = Math.min(...validBetaValues)
    const maxBeta = Math.max(...validBetaValues)
    
    return { currentBeta, avgBeta, minBeta, maxBeta }
  }, [data])
  
  // Calcular domain do eixo Y dinamicamente
  const yDomain = useMemo(() => {
    if (data.length === 0) return [0.5, 1.5]
    
    const betaValues = data.map((d) => d.beta)
    const minVal = Math.min(...betaValues)
    const maxVal = Math.max(...betaValues)
    
    // Adicionar margem de 20% para cima e para baixo
    const margin = (maxVal - minVal) * 0.2
    const domainMin = Math.max(0, Math.floor((minVal - margin) * 10) / 10)
    const domainMax = Math.ceil((maxVal + margin) * 10) / 10
    
    return [domainMin, domainMax]
  }, [data])

  // Estado vazio
  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-foreground text-lg">Evolução do Beta da Carteira</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-[400px] items-center justify-center text-muted-foreground">
            Dados de beta não disponíveis
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-foreground text-lg">Evolução do Beta da Carteira</CardTitle>
        <p className="text-muted-foreground text-sm">Beta em janela móvel de 60 dias</p>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 80, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="betaGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={DASHBOARD_COLORS.portfolio} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={DASHBOARD_COLORS.portfolio} stopOpacity={0.05} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" vertical={false} />
              <XAxis 
                dataKey="date" 
                stroke="hsl(var(--muted-foreground))"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => {
                  const date = new Date(value)
                  return `${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear().toString().slice(2)}`
                }}
              />
              <YAxis 
                stroke="hsl(var(--muted-foreground))"
                fontSize={11}
                tickLine={false}
                axisLine={false}
                domain={yDomain}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "white",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                  color: "hsl(var(--foreground))",
                  boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                }}
                labelFormatter={(value) => {
                  const date = new Date(value)
                  return date.toLocaleDateString("pt-BR", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric"
                  })
                }}
                formatter={(value: number) => [value.toFixed(2), "Beta"]}
              />
              <ReferenceLine
                y={1.0}
                stroke="#9ca3af"
                strokeDasharray="5 5"
                label={{ value: "Mercado", position: "right", fill: "#6b7280", fontSize: 11 }}
              />
              <ReferenceLine
                y={stats.avgBeta}
                stroke="#f59e0b"
                strokeDasharray="8 4"
                label={{ value: `Média (${stats.avgBeta.toFixed(2)})`, position: "left", fill: "#f59e0b", fontSize: 11 }}
              />
              <Area
                type="monotone"
                dataKey="beta"
                stroke={DASHBOARD_COLORS.portfolio}
                strokeWidth={2}
                fill="url(#betaGradient)"
                dot={false}
                activeDot={{ r: 5 }}
              />
              <Brush
                dataKey="date"
                height={40}
                stroke="hsl(var(--border))"
                fill="#f5f5f5"
                fillOpacity={1}
                travellerWidth={10}
                startIndex={0}
                endIndex={data.length - 1}
                tickFormatter={(value) => {
                  const date = new Date(value)
                  return `${date.getDate().toString().padStart(2, "0")}/${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear()}`
                }}
              >
                <AreaChart data={data}>
                  <Area
                    type="monotone"
                    dataKey="beta"
                    stroke={DASHBOARD_COLORS.portfolio}
                    fill={DASHBOARD_COLORS.portfolio}
                    fillOpacity={0.3}
                    strokeWidth={1}
                  />
                </AreaChart>
              </Brush>
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Legenda - Estilo padronizado */}
        <div className="mt-5 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 rounded-lg bg-muted/50 border border-border px-4 py-3">
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Média:</span> <span className="font-semibold">{stats.avgBeta.toFixed(2)}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Mínimo:</span> <span className="font-semibold text-green-600">{stats.minBeta.toFixed(2)}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Máximo:</span> <span className="font-semibold text-red-600">{stats.maxBeta.toFixed(2)}</span></span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
