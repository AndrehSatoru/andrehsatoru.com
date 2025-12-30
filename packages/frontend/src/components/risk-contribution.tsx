"use client"

import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"

export function RiskContribution() {
  const { analysisResult } = useDashboardData()
  
  const riskContributionData = useMemo(() => {
    // Usar dados da API
    const apiData = analysisResult?.risk_contribution
    
    if (apiData && apiData.length > 0) {
      return apiData
    }
    
    // Fallback: dados vazios
    return []
  }, [analysisResult])
  
  // Calcular estatísticas
  const stats = useMemo(() => {
    if (riskContributionData.length === 0) {
      return { topContributor: null, top3Sum: 0, maxContribution: 35 }
    }
    
    const topContributor = riskContributionData[0]
    const top3Sum = riskContributionData.slice(0, 3).reduce((sum, item) => sum + item.contribution, 0)
    const maxContribution = Math.max(...riskContributionData.map(d => d.contribution), 35)
    
    return { topContributor, top3Sum, maxContribution }
  }, [riskContributionData])
  
  if (!analysisResult || riskContributionData.length === 0) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle className="text-balance">Decomposição da Contribuição de Risco (Volatilidade)</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[400px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar a contribuição de risco</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="text-balance">Decomposição da Contribuição de Risco (Volatilidade)</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={Math.max(300, riskContributionData.length * 40)}>
          <BarChart data={riskContributionData} layout="vertical" margin={{ top: 5, right: 60, left: 80, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              type="number"
              domain={[0, Math.ceil(stats.maxContribution / 5) * 5]}
              tickFormatter={(value) => `${value.toFixed(1)}%`}
              stroke="hsl(var(--foreground))"
              label={{
                value: "Contribuição Percentual para a Volatilidade Total",
                position: "insideBottom",
                offset: -5,
                style: { fill: "hsl(var(--foreground))" },
              }}
            />
            <YAxis type="category" dataKey="asset" stroke="hsl(var(--foreground))" width={80} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--popover))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "var(--radius)",
              }}
              formatter={(value: any) => [`${value.toFixed(1)}%`, "Contribuição"]}
            />
            <Bar dataKey="contribution">
              {riskContributionData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill="hsl(var(--chart-1))" />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Maior Contribuidor</p>
            <p className="font-semibold">
              {stats.topContributor ? `${stats.topContributor.asset} (${stats.topContributor.contribution}%)` : '-'}
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Top 3 Contribuição</p>
            <p className="font-semibold">
              {stats.top3Sum.toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Concentração de Risco</p>
            <p className="font-semibold">
              {stats.topContributor && stats.topContributor.contribution > 25 ? "Alta" : "Moderada"}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

