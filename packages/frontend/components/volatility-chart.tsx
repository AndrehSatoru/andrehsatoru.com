"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, Brush, Legend } from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { useMemo } from "react"
import { SEMANTIC_COLORS } from "@/lib/colors"

const ROLLING_WINDOW = 21 // 21 dias úteis (aproximadamente 1 mês)

// Cores específicas para este gráfico
const PORTFOLIO_COLOR = SEMANTIC_COLORS.success.DEFAULT // Verde
const IBOVESPA_COLOR = "#000000" // Preto

export function VolatilityChart() {
  const { analysisResult } = useDashboardData()
  
  // Calcular volatilidade rolante de 21 dias da carteira e do Ibovespa
  const data = useMemo(() => {
    if (!analysisResult?.results?.performance || analysisResult.results.performance.length < ROLLING_WINDOW + 1) {
      return []
    }
    
    const performanceData = analysisResult.results.performance
    
    // Verificar se temos dados do Ibovespa
    const hasIbovespa = performanceData.some((d: any) => d.ibovespa !== undefined)
    
    // Calcular retornos diários da carteira e do Ibovespa
    const dailyReturns: { date: string; portfolioReturn: number; ibovespaReturn: number | null }[] = []
    for (let i = 1; i < performanceData.length; i++) {
      const prevPortfolio = performanceData[i - 1].portfolio
      const currPortfolio = performanceData[i].portfolio
      
      // Evitar divisão por zero
      if (!prevPortfolio || prevPortfolio === 0) continue
      
      const portfolioReturn = (currPortfolio - prevPortfolio) / prevPortfolio * 100
      
      let ibovespaReturn: number | null = null
      if (hasIbovespa && performanceData[i - 1].ibovespa && performanceData[i].ibovespa) {
        const prevIbov = performanceData[i - 1].ibovespa
        const currIbov = performanceData[i].ibovespa
        if (prevIbov && prevIbov !== 0) {
          ibovespaReturn = (currIbov - prevIbov) / prevIbov * 100
        }
      }
      
      dailyReturns.push({
        date: performanceData[i].date,
        portfolioReturn,
        ibovespaReturn
      })
    }
    
    // Calcular volatilidade rolante para ambos
    const rollingVolatility: { date: string; portfolio: number; ibovespa?: number }[] = []
    
    for (let i = ROLLING_WINDOW - 1; i < dailyReturns.length; i++) {
      // Pegar os últimos ROLLING_WINDOW retornos
      const windowPortfolioReturns = dailyReturns.slice(i - ROLLING_WINDOW + 1, i + 1).map(d => d.portfolioReturn)
      const windowIbovespaReturns = dailyReturns.slice(i - ROLLING_WINDOW + 1, i + 1).map(d => d.ibovespaReturn).filter(r => r !== null) as number[]
      
      // Calcular volatilidade do portfólio (precisa de pelo menos 2 pontos)
      if (windowPortfolioReturns.length < 2) continue
      
      const portfolioMean = windowPortfolioReturns.reduce((a, b) => a + b, 0) / windowPortfolioReturns.length
      const portfolioVariance = windowPortfolioReturns.reduce((sum, r) => sum + Math.pow(r - portfolioMean, 2), 0) / (windowPortfolioReturns.length - 1)
      const portfolioStdDev = Math.sqrt(Math.max(0, portfolioVariance)) // Garantir que não seja negativo
      const portfolioAnnualizedVol = portfolioStdDev * Math.sqrt(252)
      
      const dataPoint: { date: string; portfolio: number; ibovespa?: number } = {
        date: dailyReturns[i].date,
        portfolio: Math.max(0, parseFloat(portfolioAnnualizedVol.toFixed(2))) // Garantir >= 0
      }
      
      // Calcular volatilidade do Ibovespa se houver dados suficientes
      if (windowIbovespaReturns.length >= 2) {
        const ibovMean = windowIbovespaReturns.reduce((a, b) => a + b, 0) / windowIbovespaReturns.length
        const ibovVariance = windowIbovespaReturns.reduce((sum, r) => sum + Math.pow(r - ibovMean, 2), 0) / (windowIbovespaReturns.length - 1)
        const ibovStdDev = Math.sqrt(Math.max(0, ibovVariance))
        const ibovAnnualizedVol = ibovStdDev * Math.sqrt(252)
        dataPoint.ibovespa = Math.max(0, parseFloat(ibovAnnualizedVol.toFixed(2)))
      }
      
      rollingVolatility.push(dataPoint)
    }
    
    return rollingVolatility
  }, [analysisResult])

  // Verificar se temos dados do Ibovespa
  const hasIbovespaData = data.some(d => d.ibovespa !== undefined)

  if (data.length === 0) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Volatilidade</CardTitle>
          <CardDescription className="text-muted-foreground">Volatilidade anualizada em janela móvel de 21 dias (%)</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[200px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar a volatilidade</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-border hover:shadow-md transition-shadow">
      <CardHeader>
        <CardTitle className="text-foreground">Volatilidade</CardTitle>
        <CardDescription className="text-muted-foreground">Volatilidade anualizada em janela móvel de 21 dias (%)</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={380}>
          <AreaChart data={data} margin={{ top: 10, right: 60, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="portfolioVolGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={PORTFOLIO_COLOR} stopOpacity={0.3} />
                <stop offset="95%" stopColor={PORTFOLIO_COLOR} stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis 
              dataKey="date" 
              stroke="hsl(var(--muted-foreground))" 
              fontSize={11}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear().toString().slice(2)}`
              }}
            />
            <YAxis 
              stroke="hsl(var(--muted-foreground))" 
              fontSize={11}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                color: "hsl(var(--foreground))",
                boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
              }}
              labelFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleDateString("pt-BR")
              }}
              formatter={(value: number, name: string) => {
                const label = name === "portfolio" ? "Carteira" : "Ibovespa"
                return [`${value.toFixed(2)}%`, label]
              }}
            />
            {hasIbovespaData && (
              <Legend 
                verticalAlign="top" 
                height={36}
                formatter={(value) => value === "portfolio" ? "Carteira" : "Ibovespa"}
              />
            )}
            <Area
              type="monotone"
              dataKey="portfolio"
              stroke={PORTFOLIO_COLOR}
              strokeWidth={2}
              fill="url(#portfolioVolGradient)"
              name="portfolio"
              connectNulls={true}
            />
            {hasIbovespaData && (
              <Area
                type="monotone"
                dataKey="ibovespa"
                stroke={IBOVESPA_COLOR}
                strokeWidth={2}
                fill="transparent"
                name="ibovespa"
                connectNulls={true}
              />
            )}
            {data.length > 10 && (
              <Brush
                dataKey="date"
                height={40}
                stroke="hsl(var(--border))"
                fill="#f5f5f5"
                fillOpacity={1}
                travellerWidth={10}
                startIndex={0}
                endIndex={data.length - 1}
                tickFormatter={(value) => {
                  const date = new Date(value)
                  return `${date.getDate().toString().padStart(2, "0")}/${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear()}`
                }}
              >
                <AreaChart data={data}>
                  <Area
                    type="monotone"
                    dataKey="portfolio"
                    stroke={PORTFOLIO_COLOR}
                    fill={PORTFOLIO_COLOR}
                    fillOpacity={0.3}
                    strokeWidth={1}
                  />
                  {hasIbovespaData && (
                    <Area
                      type="monotone"
                      dataKey="ibovespa"
                      stroke={IBOVESPA_COLOR}
                      fill="transparent"
                      strokeWidth={1}
                    />
                  )}
                </AreaChart>
              </Brush>
            )}
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
