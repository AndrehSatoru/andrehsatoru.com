"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, Brush } from "recharts"
import { usePeriod, filterDataByPeriod } from "@/lib/period-context"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { Empty } from "./ui/empty"
import { DASHBOARD_COLORS } from "@/lib/colors"
import { motion } from "framer-motion"

export function PerformanceChart() {
  const { period } = usePeriod()
  const { analysisResult } = useDashboardData()

  // Backend returns performance in results.performance
  const allData = analysisResult?.performance || []
  
  // Ensure allData is an array before filtering
  const safeData = Array.isArray(allData) ? allData : []
  const data = filterDataByPeriod(safeData, period)

  // Debug log
  console.log("[PerformanceChart] analysisResult:", analysisResult)
  console.log("[PerformanceChart] allData length:", allData.length)
  console.log("[PerformanceChart] data length:", data.length)

  if (!analysisResult || data.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="text-foreground">Performance Acumulada</CardTitle>
            <CardDescription className="text-muted-foreground">Comparação com benchmark (CDI + 2%)</CardDescription>
          </CardHeader>
          <CardContent>
            <Empty title="Nenhum dado para exibir" description="Por favor, envie suas operações na página 'Enviar' para ver a performance." />
          </CardContent>
        </Card>
      </motion.div>
    )
  }

  // Calcular o domínio do eixo Y com margem
  const allValues = data.flatMap((d: any) => [d.portfolio, d.benchmark].filter(Boolean))
  const minValue = Math.min(...allValues)
  const maxValue = Math.max(...allValues)
  const padding = (maxValue - minValue) * 0.1
  const yMin = Math.max(0, minValue - padding)
  const yMax = maxValue + padding

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
    >
      <Card className="border-2 border-border/60">
        <CardHeader>
          <CardTitle className="text-foreground text-xl">Performance Acumulada</CardTitle>
          <CardDescription className="text-muted-foreground">Comparação com benchmark (CDI + 2%)</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={380}>
            <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorPortfolio" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={DASHBOARD_COLORS.portfolio} stopOpacity={0.2} />
                  <stop offset="95%" stopColor={DASHBOARD_COLORS.portfolio} stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="colorBenchmark" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={DASHBOARD_COLORS.benchmark} stopOpacity={0.2} />
                  <stop offset="95%" stopColor={DASHBOARD_COLORS.benchmark} stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.4} />
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
                width={70}
                domain={[yMin, yMax]}
                tickFormatter={(value) => {
                  if (value >= 1000000) return `R$ ${(value / 1000000).toFixed(1)}M`
                  if (value >= 1000) return `R$ ${(value / 1000).toFixed(0)}K`
                  return `R$ ${value.toFixed(0)}`
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(255, 255, 255, 0.95)",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "12px",
                  color: "hsl(var(--foreground))",
                  boxShadow: "0 8px 16px -4px rgba(0, 0, 0, 0.1)",
                  padding: "12px"
                }}
                labelFormatter={(value) => {
                  const date = new Date(value)
                  return date.toLocaleDateString("pt-BR", {
                    day: "2-digit",
                    month: "long",
                    year: "numeric"
                  })
                }}
                formatter={(value: any, name: any) => {
                  const label = name === "portfolio" ? "Portfólio" : "Benchmark"
                  return [`R$ ${value.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`, label]
                }}
              />
              <Area
                type="monotone"
                dataKey="portfolio"
                stroke={DASHBOARD_COLORS.portfolio}
                fillOpacity={1}
                fill="url(#colorPortfolio)"
                name="portfolio"
                strokeWidth={3}
                activeDot={{ r: 6, strokeWidth: 0, fill: DASHBOARD_COLORS.portfolio }}
              />
              <Area
                type="monotone"
                dataKey="benchmark"
                stroke={DASHBOARD_COLORS.benchmark}
                fillOpacity={1}
                fill="url(#colorBenchmark)"
                name="benchmark"
                strokeWidth={3}
                strokeDasharray="4 4"
                activeDot={{ r: 6, strokeWidth: 0, fill: DASHBOARD_COLORS.benchmark }}
              />
              <Brush
                dataKey="date"
                height={40}
                stroke="hsl(var(--border))"
                fill="hsl(var(--muted))"
                fillOpacity={0.5}
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
    </motion.div>
  )
}

