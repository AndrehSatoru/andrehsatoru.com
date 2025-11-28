"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, Brush } from "recharts"
import { usePeriod, filterDataByPeriod } from "@/lib/period-context"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { Empty } from "./ui/empty"

export function PerformanceChart() {
  const { period } = usePeriod()
  const { analysisResult } = useDashboardData()

  // Backend returns performance in results.performance
  const allData = analysisResult?.results?.performance || []
  const data = filterDataByPeriod(allData, period)

  // Debug log
  console.log("[PerformanceChart] analysisResult:", analysisResult)
  console.log("[PerformanceChart] allData length:", allData.length)
  console.log("[PerformanceChart] data length:", data.length)

  if (!analysisResult || data.length === 0) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Performance Acumulada</CardTitle>
          <CardDescription className="text-muted-foreground">Comparação com benchmark (CDI + 2%)</CardDescription>
        </CardHeader>
        <CardContent>
          <Empty title="Nenhum dado para exibir" description="Por favor, envie suas operações na página 'Enviar' para ver a performance." />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Performance Acumulada</CardTitle>
        <CardDescription className="text-muted-foreground">Comparação com benchmark (CDI + 2%)</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400} className="2xl:!h-[450px]">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorPortfolio" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorBenchmark" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--secondary))" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(var(--secondary))" stopOpacity={0} />
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
            <YAxis
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickFormatter={(value) => {
                if (value >= 1000000) return `R$ ${(value / 1000000).toFixed(1)}M`
                if (value >= 1000) return `R$ ${(value / 1000).toFixed(0)}K`
                return `R$ ${value.toFixed(0)}`
              }}
            />
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
              formatter={(value: number) => [`R$ ${value.toLocaleString("pt-BR")}`, ""]}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="portfolio"
              stroke="hsl(var(--primary))"
              fillOpacity={1}
              fill="url(#colorPortfolio)"
              name="Portfólio"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="benchmark"
              stroke="hsl(var(--secondary))"
              fillOpacity={1}
              fill="url(#colorBenchmark)"
              name="Benchmark"
              strokeWidth={2}
            />
            <Brush
              dataKey="date"
              height={50}
              stroke="#3b82f6"
              fill="#f1f5f9"
              fillOpacity={0.8}
              travellerWidth={14}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear().toString().slice(2)}`
              }}
            >
              <AreaChart data={data}>
                <Area
                  type="monotone"
                  dataKey="portfolio"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.3}
                  strokeWidth={1.5}
                />
              </AreaChart>
            </Brush>
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
