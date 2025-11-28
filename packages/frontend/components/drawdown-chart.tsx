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
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Drawdown</CardTitle>
        <CardDescription className="text-muted-foreground">Queda acumulada do pico (%)</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--destructive))" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(var(--destructive))" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              dataKey="date"
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear().toString().slice(2)}`
              }}
            />
            <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                color: "hsl(var(--foreground))",
              }}
              labelFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleDateString("pt-BR")
              }}
              formatter={(value: number) => [`${value}%`, "Drawdown"]}
            />
            <ReferenceLine y={0} stroke="hsl(var(--muted-foreground))" strokeDasharray="3 3" />
            <Area
              type="monotone"
              dataKey="drawdown"
              stroke="hsl(var(--destructive))"
              strokeWidth={2}
              fill="url(#drawdownGradient)"
            />
            <Brush
              dataKey="date"
              height={50}
              stroke="hsl(var(--destructive))"
              fill="hsl(var(--background))"
              fillOpacity={0.3}
              travellerWidth={12}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear().toString().slice(2)}`
              }}
            >
              <AreaChart data={data}>
                <Area
                  type="monotone"
                  dataKey="drawdown"
                  stroke="hsl(var(--destructive))"
                  fill="hsl(var(--destructive))"
                  fillOpacity={0.2}
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
