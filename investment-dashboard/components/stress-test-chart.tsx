"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"

const stressScenarios = [
  { scenario: "Crise 2008", impact: -18.5, type: "historical" },
  { scenario: "COVID-19", impact: -12.3, type: "historical" },
  { scenario: "Crise Subprime", impact: -15.7, type: "historical" },
  { scenario: "Choque Taxa +3%", impact: -8.2, type: "hypothetical" },
  { scenario: "Recessão Global", impact: -14.1, type: "hypothetical" },
  { scenario: "Crise Cambial", impact: -9.8, type: "hypothetical" },
]

export function StressTestChart() {
  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Testes de Estresse</CardTitle>
        <CardDescription className="text-muted-foreground">Impacto de cenários adversos na carteira</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={stressScenarios} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
            <XAxis
              type="number"
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickFormatter={(value) => `${value}%`}
            />
            <YAxis type="category" dataKey="scenario" stroke="hsl(var(--muted-foreground))" fontSize={11} width={120} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--popover))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              labelStyle={{ color: "hsl(var(--popover-foreground))" }}
              formatter={(value: number) => [`${value.toFixed(2)}%`, "Impacto"]}
            />
            <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
              {stressScenarios.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.type === "historical" ? "hsl(var(--destructive))" : "hsl(var(--chart-2))"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 flex items-center justify-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-destructive" />
            <span className="text-muted-foreground">Histórico</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-chart-2" />
            <span className="text-muted-foreground">Hipotético</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
