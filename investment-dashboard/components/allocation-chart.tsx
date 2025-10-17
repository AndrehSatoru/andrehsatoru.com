"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"

const data = [
  { name: "Renda Fixa", value: 45, color: "hsl(var(--chart-1))" },
  { name: "Ações", value: 30, color: "hsl(var(--chart-2))" },
  { name: "Fundos Imobiliários", value: 15, color: "hsl(var(--chart-3))" },
  { name: "Multimercado", value: 7, color: "hsl(var(--chart-4))" },
  { name: "Caixa", value: 3, color: "hsl(var(--chart-5))" },
]

export function AllocationChart() {
  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Alocação de Ativos</CardTitle>
        <CardDescription className="text-muted-foreground">Distribuição por classe de ativo</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                color: "hsl(var(--foreground))",
              }}
              formatter={(value: number) => [`${value}%`, ""]}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
