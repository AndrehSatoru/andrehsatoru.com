"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { useMemo } from "react"

const monthNames = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

export function VolatilityChart() {
  const { analysisResult } = useDashboardData()
  
  // Calcular volatilidade mensal a partir dos retornos mensais ou série de performance
  const data = useMemo(() => {
    // Se não há dados da API, retornar array vazio
    if (!analysisResult?.results?.performance || analysisResult.results.performance.length === 0) {
      return []
    }
    
    const performanceData = analysisResult.results.performance
    
    // Agrupar retornos por mês e calcular desvio padrão (volatilidade)
    const monthlyReturns: { [key: number]: number[] } = {}
    
    // Calcular retornos diários a partir do valor do portfólio
    for (let i = 1; i < performanceData.length; i++) {
      const prevValue = performanceData[i - 1].portfolio
      const currValue = performanceData[i].portfolio
      const dailyReturn = (currValue - prevValue) / prevValue * 100
      
      const date = new Date(performanceData[i].date)
      const month = date.getMonth()
      
      if (!monthlyReturns[month]) {
        monthlyReturns[month] = []
      }
      monthlyReturns[month].push(dailyReturn)
    }
    
    // Calcular desvio padrão para cada mês
    return monthNames.map((name, idx) => {
      const returns = monthlyReturns[idx] || []
      if (returns.length < 2) {
        return { month: name, volatility: 0 }
      }
      
      const mean = returns.reduce((a, b) => a + b, 0) / returns.length
      const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / (returns.length - 1)
      const stdDev = Math.sqrt(variance)
      // Anualizar a volatilidade (sqrt(252) para volatilidade diária)
      const annualizedVol = stdDev * Math.sqrt(252)
      
      return { month: name, volatility: parseFloat(annualizedVol.toFixed(2)) }
    }).filter(d => d.volatility > 0)
  }, [analysisResult])

  // Se não há dados, mostrar mensagem
  if (data.length === 0) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Volatilidade Mensal</CardTitle>
          <CardDescription className="text-muted-foreground">Desvio padrão dos retornos (%)</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[200px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar a volatilidade mensal</p>
        </CardContent>
      </Card>
    )
  }

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
