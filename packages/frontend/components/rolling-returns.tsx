"use client"

import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
} from "recharts"
import { usePeriod, filterDataByPeriod } from "@/lib/period-context"
import { useDashboardData } from "@/lib/dashboard-data-context"

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg p-3">
        <p className="text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">{payload[0].payload.date}</p>
        <div className="space-y-1">
          <p className="text-sm text-gray-900 dark:text-gray-100">
            <span className="font-medium">Retorno Anualizado:</span>{" "}
            <span className="font-semibold">{payload[0]?.value?.toFixed(1) || 0}%</span>
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            <span className="font-medium">CDI+2%:</span>{" "}
            <span className="font-semibold">{payload[1]?.value?.toFixed(1) || 0}%</span>
          </p>
        </div>
      </div>
    )
  }
  return null
}

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
      <Card>
        <CardHeader>
          <CardTitle className="text-balance">Retorno Anualizado</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[400px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar os retornos anualizados</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-balance">Retorno Anualizado</CardTitle>
        <div className="flex flex-wrap gap-4 text-sm mt-2">
          <div>
            <span className="text-muted-foreground">Retorno Atual: </span>
            <span className="font-semibold text-foreground">{currentReturn.toFixed(1)}%</span>
          </div>
          <div>
            <span className="text-muted-foreground">CDI+2%: </span>
            <span className="font-semibold">{currentBenchmark.toFixed(1)}%</span>
          </div>
          <div>
            <span className="text-muted-foreground">Outperformance: </span>
            <span className={`font-semibold ${outperformance >= 0 ? "text-green-600" : "text-red-600"}`}>
              {outperformance >= 0 ? "+" : ""}
              {outperformance.toFixed(1)}%
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div style={{ width: "100%", height: 450 }}>
          <ResponsiveContainer>
            <LineChart data={filteredData} margin={{ top: 10, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
              <XAxis
                dataKey="date"
                stroke="#6b7280"
                tick={{ fill: "#6b7280", fontSize: 12 }}
                tickLine={{ stroke: "#e5e7eb" }}
                label={{
                  value: "Data",
                  position: "insideBottom",
                  offset: -10,
                  style: { fill: "#6b7280", fontSize: 12 },
                }}
              />
              <YAxis
                stroke="#6b7280"
                tick={{ fill: "#6b7280", fontSize: 12 }}
                tickLine={{ stroke: "#e5e7eb" }}
                tickFormatter={(value) => `${value}%`}
                label={{
                  value: "Retorno Anualizado",
                  angle: -90,
                  position: "insideLeft",
                  style: { fill: "#6b7280", fontSize: 12 },
                }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{
                  paddingTop: "20px",
                }}
                iconType="line"
              />
              <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" strokeWidth={1} />
              <Line
                type="monotone"
                dataKey="portfolio"
                stroke="#000000"
                strokeWidth={2.5}
                dot={false}
                name="Retorno Anualizado"
                className="dark:stroke-white"
              />
              <Line
                type="monotone"
                dataKey="benchmark"
                stroke="#6b7280"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Benchmark (CDI+2%)"
              />
              <Brush
                dataKey="date"
                height={50}
                stroke="#000000"
                fill="hsl(var(--background))"
                fillOpacity={0.3}
                travellerWidth={12}
              >
                <LineChart data={filteredData}>
                  <Line type="monotone" dataKey="portfolio" stroke="#000000" strokeWidth={1} dot={false} />
                </LineChart>
              </Brush>
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
