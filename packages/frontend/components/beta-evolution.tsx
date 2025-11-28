"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { useMemo } from "react"

interface BetaDataPoint {
  date: string
  beta: number
}

export function BetaEvolution() {
  const { analysisResult } = useDashboardData()
  
  // Obter dados de beta_evolution da API
  const data: BetaDataPoint[] = useMemo(() => {
    if (!analysisResult?.results?.beta_evolution) {
      return []
    }
    return analysisResult.results.beta_evolution
  }, [analysisResult])
  
  // Calcular estatísticas (filtrando valores muito baixos que indicam início da carteira)
  const stats = useMemo(() => {
    if (data.length === 0) {
      return { currentBeta: 0, avgBeta: 0, minBeta: 0, maxBeta: 0 }
    }
    
    // Filtrar valores maiores que 0.1 para evitar betas artificialmente baixos do início
    const validBetaValues = data.map((d) => d.beta).filter((b) => b > 0.1)
    
    if (validBetaValues.length === 0) {
      return { currentBeta: 0, avgBeta: 0, minBeta: 0, maxBeta: 0 }
    }
    
    const currentBeta = data[data.length - 1].beta
    const avgBeta = validBetaValues.reduce((sum, b) => sum + b, 0) / validBetaValues.length
    const minBeta = Math.min(...validBetaValues)
    const maxBeta = Math.max(...validBetaValues)
    
    return { currentBeta, avgBeta, minBeta, maxBeta }
  }, [data])
  
  // Calcular domain do eixo Y dinamicamente
  const yDomain = useMemo(() => {
    if (data.length === 0) return [0.5, 1.5]
    
    const betaValues = data.map((d) => d.beta)
    const minVal = Math.min(...betaValues)
    const maxVal = Math.max(...betaValues)
    
    // Adicionar margem de 20% para cima e para baixo
    const margin = (maxVal - minVal) * 0.2
    const domainMin = Math.max(0, Math.floor((minVal - margin) * 10) / 10)
    const domainMax = Math.ceil((maxVal + margin) * 10) / 10
    
    return [domainMin, domainMax]
  }, [data])

  // Estado vazio
  if (data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-balance">Evolução do Beta da Carteira</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex h-[400px] items-center justify-center text-muted-foreground">
            Dados de beta não disponíveis
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-balance">Evolução do Beta da Carteira</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4 grid grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Beta Atual</p>
            <p className="text-2xl font-bold">{stats.currentBeta.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Beta Médio</p>
            <p className="text-2xl font-bold">{stats.avgBeta.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Beta Mínimo</p>
            <p className="text-2xl font-bold text-green-600">{stats.minBeta.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Beta Máximo</p>
            <p className="text-2xl font-bold text-red-600">{stats.maxBeta.toFixed(2)}</p>
          </div>
        </div>

        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" stroke="#6b7280" tick={{ fill: "#6b7280" }} />
              <YAxis stroke="#6b7280" tick={{ fill: "#6b7280" }} domain={yDomain} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(255, 255, 255, 0.95)",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                }}
                formatter={(value: number) => [value.toFixed(2), "Beta"]}
              />
              <ReferenceLine
                y={1.0}
                stroke="#9ca3af"
                strokeDasharray="5 5"
                label={{ value: "Mercado (1.0)", position: "right", fill: "#6b7280", fontSize: 11 }}
              />
              <ReferenceLine
                y={stats.avgBeta}
                stroke="#f59e0b"
                strokeDasharray="8 4"
                label={{ value: `Média (${stats.avgBeta.toFixed(2)})`, position: "left", fill: "#f59e0b", fontSize: 11 }}
              />
              <Line
                type="monotone"
                dataKey="beta"
                stroke="#2563eb"
                strokeWidth={3}
                dot={{ fill: "#2563eb", r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-4 rounded-lg bg-muted p-4">
          <p className="text-sm text-muted-foreground">
            <strong>Interpretação:</strong> Beta mede a sensibilidade da carteira em relação ao mercado. Beta = 1.0
            significa que a carteira se move igual ao mercado. Beta {">"} 1.0 indica maior volatilidade, enquanto Beta{" "}
            {"<"} 1.0 indica menor volatilidade que o mercado.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
