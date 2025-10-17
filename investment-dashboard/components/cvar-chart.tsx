"use client"

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
  Area,
  Cell,
} from "recharts"

const generateCVarData = () => {
  const data = []
  const startDate = new Date(2024, 6, 1)
  const days = 450

  for (let i = 0; i < days; i++) {
    const date = new Date(startDate)
    date.setDate(date.getDate() + i)

    // Simular retornos diários
    const randomReturn = (Math.random() - 0.48) * 3000000
    const volatility = Math.sin(i / 30) * 500000
    const returns = randomReturn + volatility

    // CVaR é a média das perdas além do VaR
    const var95 = -1500000 + Math.sin(i / 60) * 300000
    const cvar95 = var95 * 1.35 // CVaR é tipicamente 30-40% maior que VaR

    data.push({
      date: date.toISOString().split("T")[0],
      returns,
      var95,
      cvar95,
      tailLoss: returns < var95 ? returns : null,
    })
  }

  return data
}

const cvarData = generateCVarData()

export function CVarChart() {
  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">CVaR (Conditional Value at Risk)</CardTitle>
        <CardDescription className="text-muted-foreground">
          Perda média esperada além do VaR - Expected Shortfall
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={cvarData}>
            <defs>
              <linearGradient id="tailArea" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(0, 84%, 60%)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(0, 84%, 60%)" stopOpacity={0.1} />
              </linearGradient>
            </defs>
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
                return [
                  `R$ ${value.toLocaleString("pt-BR", { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`,
                  name,
                ]
              }}
            />
            <Bar dataKey="returns" name="Retorno Diário" radius={[2, 2, 0, 0]}>
              {cvarData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.returns >= 0 ? "hsl(142, 76%, 36%)" : "hsl(0, 84%, 60%)"} />
              ))}
            </Bar>
            <Area
              type="monotone"
              dataKey="tailLoss"
              fill="url(#tailArea)"
              stroke="none"
              name="Perdas na Cauda (além do VaR)"
            />
            <Line
              type="monotone"
              dataKey="var95"
              stroke="hsl(var(--chart-1))"
              strokeWidth={2}
              strokeDasharray="8 4"
              dot={false}
              name="VaR 95%"
            />
            <Line
              type="monotone"
              dataKey="cvar95"
              stroke="hsl(var(--chart-2))"
              strokeWidth={3}
              dot={false}
              name="CVaR 95% (Expected Shortfall)"
            />
          </ComposedChart>
        </ResponsiveContainer>
        <div className="mt-4 grid grid-cols-3 gap-4 rounded-lg bg-muted p-4">
          <div>
            <p className="text-xs text-muted-foreground">VaR 95% Atual</p>
            <p className="text-lg font-bold text-foreground">R$ -1.52M</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">CVaR 95% Atual</p>
            <p className="text-lg font-bold text-destructive">R$ -2.05M</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Diferença CVaR/VaR</p>
            <p className="text-lg font-bold text-orange-600">+35%</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
