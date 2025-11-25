"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { Empty } from "./ui/empty"

const COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
  "hsl(var(--chart-6))",
  "hsl(var(--chart-7))",
]

export function AllocationChart() {
  const { analysisResult } = useDashboardData()

  // Extrair dados de alocação do resultado
  const alocacaoData = analysisResult?.results?.alocacao?.alocacao || {}
  
  // Converter para formato esperado pelo gráfico
  const data = Object.entries(alocacaoData).map(([name, info]: [string, any], index: number) => ({
    name,
    value: info?.percentual || 0,
    valorTotal: info?.valor_total || 0,
    quantidade: info?.quantidade || 0,
    precoUnitario: info?.preco_unitario || 0,
    color: COLORS[index % COLORS.length],
  }))

  if (!analysisResult || data.length === 0) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Alocação de Ativos</CardTitle>
          <CardDescription className="text-muted-foreground">Distribuição por classe de ativo</CardDescription>
        </CardHeader>
        <CardContent>
          <Empty title="Nenhum dado para exibir" description="Por favor, envie suas operações para ver a alocação." />
        </CardContent>
      </Card>
    )
  }

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
              {data.map((entry: any, index: number) => (
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
              formatter={(value: number, name: string, props: any) => [
                `${value.toFixed(2)}% (R$ ${props.payload.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })})`,
                props.payload.name
              ]}
            />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
