"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Area,
  AreaChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
} from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { useMemo } from "react"
import { SEMANTIC_COLORS } from "@/lib/colors"

export function DrawdownChart() {
  const { analysisResult } = useDashboardData()
  
  // Calcular série de drawdown a partir da série de performance
  const data = useMemo(() => {
    // Se não há dados da API, retornar array vazio
    if (!analysisResult?.results?.performance || analysisResult.results.performance.length === 0) {
      return []
    }
    
    const performanceData = analysisResult.results.performance
    
    // Calcular drawdown: (valor atual - máximo histórico) / máximo histórico * 100
    let peak = performanceData[0].portfolio
    
    return performanceData.map((item: { date: string; portfolio: number }) => {
      // Atualizar o pico se valor atual é maior
      if (item.portfolio > peak) {
        peak = item.portfolio
      }
      
      // Calcular drawdown em percentual (será negativo ou zero)
      const drawdown = ((item.portfolio - peak) / peak) * 100
      
      return {
        date: item.date,
        drawdown: parseFloat(drawdown.toFixed(2))
      }
    })
  }, [analysisResult])

  // Se não há dados, mostrar mensagem
  if (data.length === 0) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Drawdown</CardTitle>
          <CardDescription className="text-muted-foreground">Queda acumulada do pico (%)</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[250px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar o drawdown</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-border hover:shadow-md transition-shadow">
      <CardHeader>
        <CardTitle className="text-foreground">Drawdown</CardTitle>
        <CardDescription className="text-muted-foreground">Queda acumulada do pico (%)</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={380}>
          <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={SEMANTIC_COLORS.error.DEFAULT} stopOpacity={0.3} />
                <stop offset="95%" stopColor={SEMANTIC_COLORS.error.DEFAULT} stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
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
              tickFormatter={(value) => `${value}%`}
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
              formatter={(value: number) => [`${value}%`, "Drawdown"]}
            />
            <ReferenceLine y={0} stroke="hsl(var(--muted-foreground))" strokeDasharray="3 3" />
            <Area
              type="monotone"
              dataKey="drawdown"
              stroke={SEMANTIC_COLORS.error.DEFAULT}
              strokeWidth={2}
              fill="url(#drawdownGradient)"
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
                  dataKey="drawdown"
                  stroke={SEMANTIC_COLORS.error.DEFAULT}
                  fill={SEMANTIC_COLORS.error.DEFAULT}
                  fillOpacity={0.3}
                  strokeWidth={1}
                />
              </AreaChart>
            </Brush>
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
