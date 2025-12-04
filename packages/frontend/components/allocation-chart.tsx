"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { Empty } from "./ui/empty"
import { CHART_COLORS } from "@/lib/colors"

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
    color: CHART_COLORS[index % CHART_COLORS.length],
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

  // Custom tooltip component para melhor visualização
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 min-w-[200px]">
          <p className="font-bold text-gray-900 text-base mb-2">{data.name}</p>
          <div className="space-y-1">
            <div className="flex justify-between">
              <span className="text-gray-600">Alocação:</span>
              <span className="font-semibold text-gray-900">{data.value.toFixed(2)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Valor:</span>
              <span className="font-semibold text-gray-900">
                R$ {data.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </span>
            </div>
            {data.quantidade > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-600">Quantidade:</span>
                <span className="font-semibold text-gray-900">{data.quantidade.toLocaleString('pt-BR')}</span>
              </div>
            )}
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <Card className="border-border hover:shadow-md transition-shadow">
      <CardHeader>
        <CardTitle className="text-foreground">Alocação de Ativos</CardTitle>
        <CardDescription className="text-muted-foreground">Distribuição por classe de ativo</CardDescription>
      </CardHeader>
      <CardContent className="flex justify-center items-center">
        <ResponsiveContainer width="100%" height={380}>
          <PieChart margin={{ top: 10, right: 100, bottom: 10, left: 100 }}>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={true}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={140}
              innerRadius={55}
              fill="#8884d8"
              dataKey="value"
              paddingAngle={2}
            >
              {data.map((entry: any, index: number) => (
                <Cell key={`cell-${index}`} fill={entry.color} stroke="#fff" strokeWidth={2} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
