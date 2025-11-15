"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"

const data = [
  { month: "Jan", volatility: 6.2 },
  { month: "Fev", volatility: 7.8 },
  { month: "Mar", volatility: 8.5 },
  { month: "Abr", volatility: 7.1 },
  { month: "Mai", volatility: 9.2 },
  { month: "Jun", volatility: 8.8 },
  { month: "Jul", volatility: 7.5 },
  { month: "Ago", volatility: 8.9 },
  { month: "Set", volatility: 9.5 },
  { month: "Out", volatility: 8.1 },
  { month: "Nov", volatility: 7.8 },
  { month: "Dez", volatility: 8.3 },
]

export function VolatilityChart() {
  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Volatilidade Mensal</CardTitle>
        <CardDescription className="text-muted-foreground">Desvio padrão dos retornos (%)</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={12} />
            <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                color: "hsl(var(--foreground))",
              }}
              formatter={(value: number) => [`${value}%`, "Volatilidade"]}
            />
            <Bar dataKey="volatility" fill="hsl(var(--secondary))" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
