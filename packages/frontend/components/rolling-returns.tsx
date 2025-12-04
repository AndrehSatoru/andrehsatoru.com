"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Area,
  AreaChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
} from "recharts"
import { usePeriod, filterDataByPeriod } from "@/lib/period-context"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { DASHBOARD_COLORS } from "@/lib/colors"

export function RollingReturns() {
  const { period } = usePeriod()
  const { analysisResult } = useDashboardData()

  const rollingReturnsData = useMemo(() => {
    // Usar dados reais da API
    const apiData = analysisResult?.results?.rolling_annualized_returns
    
    if (apiData && apiData.length > 0) {
      return apiData
    }
    
    // Fallback: calcular a partir dos dados de performance
    const performance = analysisResult?.results?.performance
    if (!performance || performance.length < 60) {
      return []
    }
    
    // Calcular retornos rolling mensais
    const monthlyData: { [key: string]: { values: number[], benchmark: number[] } } = {}
    
    for (let i = 1; i < performance.length; i++) {
      const date = new Date(performance[i].date)
      const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
      
      if (!monthlyData[monthKey]) {
        monthlyData[monthKey] = { values: [], benchmark: [] }
      }
      
      const ret = (performance[i].portfolio - performance[i - 1].portfolio) / performance[i - 1].portfolio
      const benchRet = (performance[i].benchmark - performance[i - 1].benchmark) / performance[i - 1].benchmark
      
      monthlyData[monthKey].values.push(ret)
      monthlyData[monthKey].benchmark.push(benchRet)
    }
    
    // Calcular retornos anualizados por mês
    const result = Object.entries(monthlyData).map(([month, data]) => {
      const avgRet = data.values.reduce((a, b) => a + b, 0) / data.values.length
      const avgBench = data.benchmark.reduce((a, b) => a + b, 0) / data.benchmark.length
      
      return {
        date: month,
        portfolio: Math.round(avgRet * 252 * 100 * 10) / 10,
        benchmark: Math.round(avgBench * 252 * 100 * 10) / 10,
      }
    })
    
    return result.sort((a, b) => a.date.localeCompare(b.date))
  }, [analysisResult])

  const filteredData = filterDataByPeriod(rollingReturnsData, period)

  const currentReturn = filteredData[filteredData.length - 1]?.portfolio || 0
  const currentBenchmark = filteredData[filteredData.length - 1]?.benchmark || 0
  const outperformance = currentReturn - currentBenchmark

  if (!analysisResult || rollingReturnsData.length === 0) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Retorno Anualizado</CardTitle>
          <CardDescription className="text-muted-foreground">Comparação com benchmark (CDI + 2%)</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[380px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar os retornos anualizados</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Retorno Anualizado</CardTitle>
        <CardDescription className="text-muted-foreground">
          Retorno: {currentReturn.toFixed(1)}% | CDI+2%: {currentBenchmark.toFixed(1)}% | Outperformance: 
          <span className={outperformance >= 0 ? "text-green-600" : "text-red-600"}>
            {" "}{outperformance >= 0 ? "+" : ""}{outperformance.toFixed(1)}%
          </span>
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={380}>
          <AreaChart data={filteredData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRetorno" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={DASHBOARD_COLORS.portfolio} stopOpacity={0.3} />
                <stop offset="95%" stopColor={DASHBOARD_COLORS.portfolio} stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="colorBenchmarkRet" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={DASHBOARD_COLORS.benchmark} stopOpacity={0.2} />
                <stop offset="95%" stopColor={DASHBOARD_COLORS.benchmark} stopOpacity={0.02} />
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
                const [year, month] = value.split('-')
                return `${month}/${year.slice(2)}`
              }}
            />
            <YAxis
              stroke="hsl(var(--muted-foreground))"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              width={45}
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
                const [year, month] = value.split('-')
                return `${month}/${year}`
              }}
              formatter={(value: number, name: string) => {
                const label = name === "portfolio" ? "Retorno Anualizado" : "Benchmark (CDI+2%)"
                return [`${value.toFixed(1)}%`, label]
              }}
            />
            <ReferenceLine y={0} stroke="hsl(var(--muted-foreground))" strokeDasharray="3 3" />
            <Area
              type="monotone"
              dataKey="portfolio"
              stroke={DASHBOARD_COLORS.portfolio}
              fillOpacity={1}
              fill="url(#colorRetorno)"
              name="portfolio"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="benchmark"
              stroke={DASHBOARD_COLORS.benchmark}
              fillOpacity={1}
              fill="url(#colorBenchmarkRet)"
              name="benchmark"
              strokeWidth={1.5}
            />
            <Brush
              dataKey="date"
              height={40}
              stroke="hsl(var(--border))"
              fill="#f5f5f5"
              fillOpacity={1}
              travellerWidth={10}
              startIndex={0}
              endIndex={filteredData.length - 1}
              tickFormatter={(value) => {
                const [year, month] = value.split('-')
                return `${month}/${year}`
              }}
            >
              <AreaChart data={filteredData}>
                <Area
                  type="monotone"
                  dataKey="portfolio"
                  stroke={DASHBOARD_COLORS.portfolio}
                  fill={DASHBOARD_COLORS.portfolio}
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
