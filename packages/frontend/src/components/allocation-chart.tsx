"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { Empty } from "./ui/empty"
import { CHART_COLORS } from "@/lib/colors"
import { motion } from "framer-motion"

export function AllocationChart() {
  const { analysisResult } = useDashboardData()

  // Extrair dados de alocação do resultado
  const alocacaoData = analysisResult?.alocacao?.alocacao || {}
  
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
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card className="border-2 border-border/60">
          <CardHeader>
            <CardTitle className="text-foreground text-xl">Alocação de Ativos</CardTitle>
            <CardDescription className="text-muted-foreground">Distribuição por classe de ativo</CardDescription>
          </CardHeader>
          <CardContent>
            <Empty title="Nenhum dado para exibir" description="Por favor, envie suas operações para ver a alocação." />
          </CardContent>
        </Card>
      </motion.div>
    )
  }

  // Custom tooltip component para melhor visualização
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-popover/95 backdrop-blur-sm border-2 border-border rounded-xl shadow-lg p-4 min-w-[200px]">
          <p className="font-bold text-foreground text-base mb-2 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: data.color }} />
            {data.name}
          </p>
          <div className="space-y-1.5 text-sm">
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Alocação:</span>
              <span className="font-bold text-foreground tabular-nums">{data.value.toFixed(2)}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Valor:</span>
              <span className="font-bold text-foreground tabular-nums">
                R$ {data.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </span>
            </div>
            {data.quantidade > 0 && (
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Quantidade:</span>
                <span className="font-medium text-foreground tabular-nums">{data.quantidade.toLocaleString('pt-BR')}</span>
              </div>
            )}
          </div>
        </div>
      )
    }
    return null
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      <Card className="border-2 border-border/60 hover:shadow-lg transition-all duration-300">
        <CardHeader>
          <CardTitle className="text-foreground text-xl">Alocação de Ativos</CardTitle>
          <CardDescription className="text-muted-foreground">Distribuição por classe de ativo</CardDescription>
        </CardHeader>
        <CardContent className="flex justify-center items-center">
          <ResponsiveContainer width="100%" height={380}>
            <PieChart margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
                  if (percent < 0.05) return null; // Hide labels for small segments
                  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
                  const x = cx + radius * Math.cos(-midAngle * Math.PI / 180);
                  const y = cy + radius * Math.sin(-midAngle * Math.PI / 180);
                  return (
                    <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" className="text-xs font-bold pointer-events-none drop-shadow-md">
                      {`${(percent * 100).toFixed(0)}%`}
                    </text>
                  );
                }}
                outerRadius={150}
                innerRadius={70}
                dataKey="value"
                paddingAngle={4}
                cornerRadius={6}
              >
                {data.map((entry: any, index: number) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.color} 
                    stroke="hsl(var(--card))" 
                    strokeWidth={4}
                    className="hover:opacity-80 transition-opacity duration-300 outline-none" 
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} cursor={false} />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </motion.div>
  )
}

