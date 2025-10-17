"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Bar,
  ComposedChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Line,
  Scatter,
  Cell,
} from "recharts"

const generateDailyData = () => {
  const data = []
  const startDate = new Date(2024, 6, 1) // Julho 2024
  const days = 450

  let var95 = -1500000
  let var99 = -2000000
  const violations: number[] = []

  for (let i = 0; i < days; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)

    // Simular retornos diários com distribuição realista
    const randomReturn = (Math.random() - 0.48) * 3000000
    const volatility = Math.sin(i / 30) * 500000
    const returns = randomReturn + volatility

    // VaR evolui ao longo do tempo
    var95 = -1500000 + Math.sin(i / 60) * 300000
    var99 = -2000000 + Math.sin(i / 60) * 500000

    // Detectar violações do VaR 99%
    const isViolation = returns < var99
    if (isViolation) {
      violations.push(i)
    }

    data.push({
      date: date.toISOString().split("T")[0],
      returns,
      var95,
      var99,
      violation: isViolation ? returns : null,
    })
  }

  return { data, violationCount: violations.length }
}

export function VarChart() {
  const [chartData, setChartData] = useState<{ data: any[]; violationCount: number } | null>(null)

  useEffect(() => {
    const generated = generateDailyData()
    setChartData(generated)
  }, [])

  if (!chartData) {
    return <Card className="border-border"><CardHeader><CardTitle className="text-foreground">Retorno Monetário Diário vs. VaR Histórico Diário</CardTitle><CardDescription className="text-muted-foreground">Carregando...</CardDescription></CardHeader></Card>
  }
  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Retorno Monetário Diário vs. VaR Histórico Diário</CardTitle>
        <CardDescription className="text-muted-foreground">
          Retornos diários da carteira comparados aos limites de VaR
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={chartData.data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
            <XAxis
              dataKey="date"
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`
              }}
              interval={60}
            />
            <YAxis
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickFormatter={(value) => `R$ ${(value / 1000000).toFixed(1)}M`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--popover))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              labelStyle={{ color: "hsl(var(--popover-foreground))" }}
              formatter={(value: number, name: string) => {
                if (name === "Retorno Monetário Diário") {
                  return [
                    `R$ ${value.toLocaleString("pt-BR", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`,
                    name,
                  ]
                }
                if (name === "VaR Histórico (99%)") {
                  return [
                    `R$ ${value.toLocaleString("pt-BR", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`,
                    name,
                  ]
                }
                if (name === "VaR Histórico (95%)") {
                  return [
                    `R$ ${value.toLocaleString("pt-BR", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`,
                    name,
                  ]
                }
                return [value, name]
              }}
            />
            <Bar dataKey="returns" name="Retorno Monetário Diário" radius={[2, 2, 0, 0]}>
              {chartData.data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.returns >= 0 ? "hsl(142, 76%, 36%)" : "hsl(0, 84%, 60%)"} />
              ))}
            </Bar>
            <Line
              type="monotone"
              dataKey="var99"
              stroke="hsl(var(--foreground))"
              strokeWidth={2}
              strokeDasharray="8 4"
              dot={false}
              name="VaR Histórico (99%)"
            />
            <Line
              type="monotone"
              dataKey="var95"
              stroke="hsl(var(--foreground))"
              strokeWidth={2}
              strokeDasharray="2 2"
              dot={false}
              name="VaR Histórico (95%)"
            />
            <Scatter
              dataKey="violation"
              fill="#eab308"
              stroke="#000"
              strokeWidth={2}
              shape="circle"
              name={`Quebras do VaR (99%): ${chartData.violationCount}`}
            />
          </ComposedChart>
        </ResponsiveContainer>
        <div className="mt-4 flex flex-wrap items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="h-0.5 w-8 border-t-2 border-dashed border-foreground" />
            <span className="text-muted-foreground">VaR Histórico (99%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-0.5 w-8 border-t-2 border-dotted border-foreground" />
            <span className="text-muted-foreground">VaR Histórico (95%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-yellow-500 ring-2 ring-black" />
            <span className="text-muted-foreground">Quebras do VaR (99%): {chartData.violationCount}</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-8 bg-green-600" />
            <span className="text-muted-foreground">Retorno Monetário Diário</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
