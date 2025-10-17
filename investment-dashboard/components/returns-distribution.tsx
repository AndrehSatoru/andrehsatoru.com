"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from "recharts"

const distributionData = [
  { range: "-4%", frequency: 2, returns: -4 },
  { range: "-3%", frequency: 5, returns: -3 },
  { range: "-2%", frequency: 12, returns: -2 },
  { range: "-1%", frequency: 28, returns: -1 },
  { range: "0%", frequency: 45, returns: 0 },
  { range: "1%", frequency: 38, returns: 1 },
  { range: "2%", frequency: 22, returns: 2 },
  { range: "3%", frequency: 8, returns: 3 },
  { range: "4%", frequency: 3, returns: 4 },
]

const VAR_95 = -2.1
const CVAR_95 = -2.8

export function ReturnsDistribution() {
  return (
    <Card className="border-border lg:col-span-2">
      <CardHeader>
        <CardTitle className="text-foreground">Distribuição de Retornos</CardTitle>
        <CardDescription className="text-muted-foreground">
          Histograma com VaR e CVaR marcados (95% confiança)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={distributionData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
            <XAxis dataKey="range" stroke="hsl(var(--muted-foreground))" fontSize={12} />
            <YAxis
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              label={{ value: "Frequência", angle: -90, position: "insideLeft" }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--popover))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              labelStyle={{ color: "hsl(var(--popover-foreground))" }}
              formatter={(value: number) => [value, "Frequência"]}
            />
            <ReferenceLine
              x="-2%"
              stroke="hsl(var(--chart-1))"
              strokeWidth={2}
              strokeDasharray="5 5"
              label={{ value: "VaR 95%", position: "top", fill: "hsl(var(--chart-1))" }}
            />
            <ReferenceLine
              x="-3%"
              stroke="hsl(var(--chart-2))"
              strokeWidth={2}
              strokeDasharray="5 5"
              label={{ value: "CVaR 95%", position: "top", fill: "hsl(var(--chart-2))" }}
            />
            <Bar dataKey="frequency" radius={[4, 4, 0, 0]}>
              {distributionData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.returns < VAR_95 ? "hsl(var(--destructive))" : "hsl(var(--chart-3))"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 grid grid-cols-3 gap-4 rounded-lg bg-muted p-4 text-center">
          <div>
            <p className="text-xs text-muted-foreground">Retorno Médio</p>
            <p className="text-lg font-bold text-foreground">0.85%</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Desvio Padrão</p>
            <p className="text-lg font-bold text-foreground">1.52%</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Assimetria</p>
            <p className="text-lg font-bold text-foreground">-0.23</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
