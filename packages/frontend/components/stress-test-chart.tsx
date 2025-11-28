"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"

// Dados de fallback caso não haja dados do backend
const fallbackScenarios = [
  { scenario: "Crise 2008", impact: -18.5, type: "historical" },
  { scenario: "COVID-19", impact: -12.3, type: "historical" },
  { scenario: "Crise Subprime", impact: -15.7, type: "historical" },
  { scenario: "Choque Taxa +3%", impact: -8.2, type: "hypothetical" },
  { scenario: "Recessão Global", impact: -14.1, type: "hypothetical" },
  { scenario: "Crise Cambial", impact: -9.8, type: "hypothetical" },
]

export function StressTestChart() {
  const { analysisResult } = useDashboardData()
  
  const stressScenarios = useMemo(() => {
    // Usar dados do backend se disponíveis
    if (analysisResult?.results?.stress_tests && analysisResult.results.stress_tests.length > 0) {
      return analysisResult.results.stress_tests.map((test: any) => ({
        scenario: test.scenario,
        impact: test.impact,
        type: test.type
      }))
    }
    // Fallback para dados mockados
    return fallbackScenarios
  }, [analysisResult])

  return (
    <Card className="border-border hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <CardTitle className="text-foreground text-lg">Testes de Estresse</CardTitle>
        <CardDescription className="text-muted-foreground text-sm">Impacto de cenários adversos na carteira</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={stressScenarios} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} horizontal={true} vertical={false} />
            <XAxis
              type="number"
              stroke="hsl(var(--muted-foreground))"
              fontSize={11}
              tickFormatter={(value) => `${value}%`}
              domain={['dataMin - 5', 0]}
            />
            <YAxis 
              type="category" 
              dataKey="scenario" 
              stroke="hsl(var(--muted-foreground))" 
              fontSize={11} 
              width={100}
              tick={{ fill: 'hsl(var(--muted-foreground))' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--popover))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              labelStyle={{ color: "hsl(var(--popover-foreground))" }}
              formatter={(value: number) => [`${value.toFixed(2)}%`, "Impacto"]}
            />
            <Bar dataKey="impact" radius={[0, 4, 4, 0]} maxBarSize={30}>
              {stressScenarios.map((entry: any, index: number) => (
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
            <div className="h-3 w-3 rounded bg-destructive" />
            <span className="text-muted-foreground">Histórico</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded bg-chart-2" />
            <span className="text-muted-foreground">Hipotético</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
