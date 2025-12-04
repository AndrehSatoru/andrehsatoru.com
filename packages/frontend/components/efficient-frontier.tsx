"use client"

import { useMemo, useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ComposedChart,
  Line,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Label,
  ZAxis,
  ReferenceLine,
} from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"

// Interface para os pontos da fronteira retornados pelo backend
interface FrontierPoint {
  ret_annual: number
  vol_annual: number
  sharpe: number
  weights: Record<string, number>
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    
    // Definir nome baseado no tipo
    let displayName = data.name || "Ponto"
    let colorClass = "text-foreground"
    
    if (data.type === "current") {
      displayName = "◆ Carteira Atual"
      colorClass = "text-red-500"
    } else if (data.type === "maxSharpe") {
      displayName = "★ Máximo Sharpe"
      colorClass = "text-amber-500"
    } else if (data.type === "minVar") {
      displayName = "● Mínima Volatilidade"
      colorClass = "text-yellow-600"
    } else if (data.type === "asset") {
      displayName = `■ ${data.name}`
      colorClass = "text-gray-500"
    } else if (data.type === "frontier") {
      displayName = "— Fronteira Eficiente"
      colorClass = "text-gray-800 dark:text-gray-200"
    } else if (data.type === "cal") {
      displayName = "- - Capital Allocation Line"
      colorClass = "text-orange-500"
    }
    
    return (
      <div className="bg-card border-2 border-border rounded-lg p-3 shadow-2xl min-w-[200px]">
        <p className={`font-bold text-sm mb-2 pb-2 border-b border-border ${colorClass}`}>{displayName}</p>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground">Retorno Anual:</span>
            <span className="text-sm font-bold text-green-600">{data.return?.toFixed(2)}%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground">Volatilidade:</span>
            <span className="text-sm font-bold text-orange-500">{data.volatility?.toFixed(2)}%</span>
          </div>
          {data.sharpe !== undefined && data.sharpe !== null && (
            <div className="flex justify-between items-center pt-2 border-t border-border">
              <span className="text-xs text-muted-foreground">Sharpe Ratio:</span>
              <span className="text-sm font-bold text-amber-500">{data.sharpe.toFixed(3)}</span>
            </div>
          )}
        </div>
      </div>
    )
  }
  return null
}

// Componente de shape com área de hover maior para melhor interatividade
const DiamondShape = (props: any) => {
  const { cx, cy, payload } = props
  if (cx === undefined || cy === undefined) return null
  return (
    <g style={{ cursor: 'pointer' }}>
      {/* Área invisível maior para capturar hover */}
      <circle cx={cx} cy={cy} r={20} fill="transparent" />
      <polygon
        points={`${cx},${cy-14} ${cx+14},${cy} ${cx},${cy+14} ${cx-14},${cy}`}
        fill="#EF4444"
        stroke="#991B1B"
        strokeWidth={2}
      />
    </g>
  )
}

const StarShape = (props: any) => {
  const { cx, cy } = props
  if (cx === undefined || cy === undefined) return null
  const size = 14
  return (
    <g style={{ cursor: 'pointer' }}>
      {/* Área invisível maior para capturar hover */}
      <circle cx={cx} cy={cy} r={20} fill="transparent" />
      <polygon
        points={`${cx},${cy-size} ${cx+size*0.4},${cy-size*0.4} ${cx+size},${cy} ${cx+size*0.4},${cy+size*0.4} ${cx},${cy+size} ${cx-size*0.4},${cy+size*0.4} ${cx-size},${cy} ${cx-size*0.4},${cy-size*0.4}`}
        fill="#FCD34D"
        stroke="#92400E"
        strokeWidth={2}
      />
    </g>
  )
}

const CircleShape = (props: any) => {
  const { cx, cy } = props
  if (cx === undefined || cy === undefined) return null
  return (
    <g style={{ cursor: 'pointer' }}>
      {/* Área invisível maior para capturar hover */}
      <circle cx={cx} cy={cy} r={20} fill="transparent" />
      <circle
        cx={cx}
        cy={cy}
        r={12}
        fill="#FCD34D"
        stroke="#92400E"
        strokeWidth={2}
      />
    </g>
  )
}

const SquareShape = (props: any) => {
  const { cx, cy } = props
  if (cx === undefined || cy === undefined) return null
  return (
    <g style={{ cursor: 'pointer' }}>
      {/* Área invisível maior para capturar hover */}
      <circle cx={cx} cy={cy} r={15} fill="transparent" />
      <rect
        x={cx - 7}
        y={cy - 7}
        width={14}
        height={14}
        fill="#9CA3AF"
        stroke="#4B5563"
        strokeWidth={1.5}
      />
    </g>
  )
}

// Custom Tooltip Component que segue o mouse
interface TooltipData {
  x: number
  y: number
  data: any
}

// Interface para dados do gráfico
interface ChartData {
  frontierData: Array<{ volatility: number; return: number; sharpe: number; type: string }>
  calData: Array<{ volatility: number; return: number; type: string }>
  individualAssets: Array<{ name: string; volatility: number; return: number; sharpe: number; type: string }>
  currentPortfolio: { name: string; volatility: number; return: number; sharpe: number; type: string }
  maxSharpe: { name: string; volatility: number; return: number; sharpe: number; type: string }
  minVar: { name: string; volatility: number; return: number; sharpe?: number; type: string }
  domainX: [number, number]
  domainY: [number, number]
  riskFreeRatePct: number // CDI em percentual para exibição
}

export function EfficientFrontier() {
  const { analysisResult } = useDashboardData()
  const [activeTooltip, setActiveTooltip] = useState<TooltipData | null>(null)
  const [frontierPoints, setFrontierPoints] = useState<FrontierPoint[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Taxa livre de risco - obter CDI do backend (benchmark mais recente), fallback para 12%
  const rollingReturns = analysisResult?.results?.rolling_annualized_returns
  const lastBenchmark = Array.isArray(rollingReturns) && rollingReturns.length > 0 
    ? rollingReturns[rollingReturns.length - 1]?.benchmark 
    : null
  // O benchmark é CDI+2%, então subtraímos 2% para ter apenas o CDI
  const riskFreeRate = lastBenchmark ? (lastBenchmark - 2) / 100 : 0.12 // Converter de % para decimal

  // Função para normalizar ticker - adiciona .SA apenas para tickers brasileiros
  const normalizeTicker = (ticker: string): string => {
    // Remove .SA se existir para analisar o ticker base
    const cleanTicker = ticker.replace(".SA", "").replace(".sa", "").toUpperCase()
    
    // Verifica se é ticker brasileiro (termina em 3, 4, 5, 6 ou 11)
    // 3/4 = ações ordinárias/preferenciais
    // 5/6 = preferenciais classe A/B
    // 11 = units/BDRs/ETFs
    const isBrazilian = /\d{1,2}$/.test(cleanTicker) && 
      (cleanTicker.endsWith('3') || 
       cleanTicker.endsWith('4') || 
       cleanTicker.endsWith('5') || 
       cleanTicker.endsWith('6') || 
       cleanTicker.endsWith('11'))
    
    return isBrazilian ? `${cleanTicker}.SA` : cleanTicker
  }

  // Extrair ativos e datas do analysisResult
  const { assets, startDate, endDate } = useMemo(() => {
    if (!analysisResult?.results?.alocacao?.alocacao || !analysisResult?.results?.performance) {
      return { assets: [], startDate: null, endDate: null }
    }

    const alocacaoData = analysisResult.results.alocacao.alocacao
    const performance = analysisResult.results.performance

    // Obter lista de ativos (excluir Caixa) e normalizar tickers
    const assetList = Object.keys(alocacaoData)
      .filter(a => a !== "Caixa" && alocacaoData[a]?.percentual > 0)
      .map(ticker => normalizeTicker(ticker))

    // Obter datas do período
    const dates = performance.map((p: any) => p.date).sort()
    const start = dates[0]
    const end = dates[dates.length - 1]

    console.log("[EfficientFrontier] Assets:", assetList, "Period:", start, "-", end)

    return { assets: assetList, startDate: start, endDate: end }
  }, [analysisResult])

  // Buscar dados da fronteira eficiente do backend (via rota API do Next.js)
  useEffect(() => {
    async function fetchFrontierData() {
      if (assets.length < 2 || !startDate || !endDate) {
        return
      }

      setIsLoading(true)
      setError(null)

      try {
        // Usar rota API do Next.js para evitar CORS
        const response = await fetch("/api/frontier-data", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            assets,
            start_date: startDate,
            end_date: endDate,
            n_samples: 100, // Mínimo requerido pelo backend (será convertido em pontos na fronteira)
            long_only: true,
            max_weight: null,
            rf: riskFreeRate, // CDI anual como decimal
          }),
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.message || "Erro ao buscar fronteira eficiente")
        }

        const data = await response.json()

        if (data.points && data.points.length > 0) {
          setFrontierPoints(data.points)
        } else {
          setError("Nenhum ponto da fronteira retornado")
        }
      } catch (err: any) {
        console.error("Erro ao buscar fronteira eficiente:", err)
        setError(err.message || "Erro ao calcular fronteira eficiente")
      } finally {
        setIsLoading(false)
      }
    }

    fetchFrontierData()
  }, [assets, startDate, endDate])

  // Processar dados para o gráfico
  const chartData = useMemo<ChartData | null>(() => {
    if (!analysisResult?.results?.performance || !analysisResult?.results?.alocacao?.alocacao) {
      return null
    }

    const performance = analysisResult.results.performance
    const alocacaoData = analysisResult.results.alocacao.alocacao
    const desempenho = analysisResult.results.desempenho || {}
    const backendAssetStats = analysisResult.results.asset_stats

    // Usar dados do backend para retorno e volatilidade da carteira
    // O backend já calcula CAGR e volatilidade anualizada corretamente
    let annualReturn = desempenho["retorno_anualizado_%"] ?? 0
    let annualVol = desempenho["volatilidade_anual_%"] ?? 0
    
    // Fallback: calcular se não temos os dados do backend
    if (annualReturn === 0 && annualVol === 0 && performance.length > 1) {
      const returns: number[] = []
      for (let i = 1; i < performance.length; i++) {
        const ret = (performance[i].portfolio - performance[i - 1].portfolio) / performance[i - 1].portfolio
        returns.push(ret)
      }
      
      const tradingDays = returns.length
      const totalReturn = (performance[performance.length - 1].portfolio / performance[0].portfolio) - 1
      const yearsInPeriod = tradingDays / 252
      
      annualReturn = yearsInPeriod > 0 
        ? (Math.pow(1 + totalReturn, 1 / yearsInPeriod) - 1) * 100 
        : 0
      
      const avgDailyReturn = returns.reduce((a, b) => a + b, 0) / returns.length
      const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgDailyReturn, 2), 0) / (returns.length - 1)
      const dailyVol = Math.sqrt(variance)
      annualVol = dailyVol * Math.sqrt(252) * 100
    }
    
    const currentSharpe = annualVol > 0 ? (annualReturn - riskFreeRate * 100) / annualVol : 0
    
    console.log("[EfficientFrontier] Portfolio Stats from backend:", {
      annualReturn: annualReturn.toFixed(2) + "%",
      annualVol: annualVol.toFixed(2) + "%",
      sharpe: currentSharpe.toFixed(2)
    })

    // Obter ativos individuais - usar dados do backend se disponíveis
    const individualAssets = Object.keys(alocacaoData)
      .filter(a => a !== "Caixa" && alocacaoData[a]?.percentual > 0)
      .map(asset => {
        const ticker = asset.replace(".SA", "")
        
        // Tentar dados reais do backend
        const backendStats = backendAssetStats?.find((s: { asset: string }) => s.asset === ticker)
        if (backendStats) {
          const sharpe = backendStats.volatility > 0 
            ? (backendStats.return - riskFreeRate * 100) / backendStats.volatility 
            : 0
          return {
            name: ticker,
            volatility: backendStats.volatility,
            return: backendStats.return,
            sharpe,
            type: "asset",
          }
        }
        
        // Fallback para valores padrão
        return {
          name: ticker,
          volatility: 30,
          return: 15,
          sharpe: (15 - riskFreeRate * 100) / 30,
          type: "asset",
        }
      })

    // Converter pontos da fronteira do backend para formato do gráfico
    // Retornos e volatilidades vêm como decimais (ex: 0.15 = 15%)
    // O backend agora calcula a fronteira eficiente real usando otimização
    const frontierData = frontierPoints.map(point => ({
      volatility: point.vol_annual * 100, // Converter para percentual
      return: point.ret_annual * 100,     // Converter para percentual
      sharpe: point.sharpe,
      type: "frontier",
    })).sort((a, b) => a.volatility - b.volatility) // Ordenar por volatilidade
    
    // Encontrar o ponto de mínima volatilidade
    let minVarPoint = frontierData.length > 0 
      ? frontierData.reduce((min, point) => point.volatility < min.volatility ? point : min, frontierData[0])
      : { volatility: annualVol, return: annualReturn, sharpe: currentSharpe }
    
    // Encontrar ponto de máximo Sharpe
    let maxSharpePoint = frontierData.length > 0
      ? frontierData.reduce((max, point) => point.sharpe > max.sharpe ? point : max, frontierData[0])
      : { volatility: annualVol, return: annualReturn, sharpe: currentSharpe }
    
    // Se não temos dados da API, usar valores placeholder
    if (frontierData.length === 0) {
      minVarPoint = { volatility: annualVol, return: annualReturn, sharpe: currentSharpe }
      maxSharpePoint = { volatility: annualVol, return: annualReturn, sharpe: currentSharpe }
    }

    // Calcular domínios do gráfico
    // Incluir fronteira, ativos individuais E carteira atual
    const frontierVolatilities = frontierData.length > 0 
      ? frontierData.map(p => p.volatility) 
      : []
    const frontierReturns = frontierData.length > 0 
      ? frontierData.map(p => p.return) 
      : []
    
    const allVolatilities = [
      ...individualAssets.map(a => a.volatility),
      ...frontierVolatilities,
      annualVol // Incluir volatilidade da carteira atual
    ]
    const allReturns = [
      ...individualAssets.map(a => a.return),
      ...frontierReturns,
      annualReturn // Incluir retorno da carteira atual
    ]

    // Adicionar margem para visualização (15%)
    const maxVol = Math.max(...allVolatilities) * 1.15
    const maxRet = Math.max(...allReturns) * 1.15
    const minRet = Math.min(...allReturns, 0) - 5

    // Gerar CAL (Capital Allocation Line) baseada no máximo Sharpe
    const calData = []
    for (let i = 0; i <= 100; i++) {
      const volatility = (i / 100) * maxVol
      const returnValue = riskFreeRate * 100 + maxSharpePoint.sharpe * volatility
      calData.push({
        volatility: Number(volatility.toFixed(2)),
        return: Number(returnValue.toFixed(2)),
        type: "cal",
      })
    }

    return {
      frontierData,
      calData,
      individualAssets,
      currentPortfolio: {
        name: "Carteira Atual (Backtest)",
        volatility: Number(annualVol.toFixed(2)),
        return: Number(annualReturn.toFixed(2)),
        sharpe: currentSharpe,
        type: "current",
      },
      maxSharpe: {
        name: `Máximo Sharpe (${maxSharpePoint.sharpe.toFixed(2)})`,
        volatility: Number(maxSharpePoint.volatility.toFixed(2)),
        return: Number(maxSharpePoint.return.toFixed(2)),
        sharpe: maxSharpePoint.sharpe,
        type: "maxSharpe",
      },
      minVar: {
        name: `Mínima Volatilidade (${minVarPoint.volatility.toFixed(1)}%)`,
        volatility: Number(minVarPoint.volatility.toFixed(2)),
        return: Number(minVarPoint.return.toFixed(2)),
        type: "minVar",
      },
      domainX: [0, Math.ceil(maxVol / 10) * 10] as [number, number],
      domainY: [Math.floor(minRet / 10) * 10, Math.ceil(maxRet / 10) * 10] as [number, number],
      riskFreeRatePct: riskFreeRate * 100, // CDI em percentual
    }
  }, [analysisResult, frontierPoints, riskFreeRate])

  if (!chartData) {
    return (
      <Card className="lg:col-span-2 border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Fronteira Eficiente (Premissa: Retornos Históricos)</CardTitle>
          <CardDescription className="text-muted-foreground">
            Relação risco-retorno e otimização de portfólio
          </CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[400px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar a fronteira eficiente</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="lg:col-span-2 border-border">
      <CardHeader className="pb-2">
        <CardTitle className="text-foreground">Fronteira Eficiente (Premissa: Retornos Históricos)</CardTitle>
        <CardDescription className="text-muted-foreground">
          Relação risco-retorno e otimização de portfólio
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[600px]" onMouseLeave={() => setActiveTooltip(null)}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart margin={{ top: 20, right: 30, bottom: 60, left: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.5} />
              <XAxis
                type="number"
                dataKey="volatility"
                name="Volatilidade"
                domain={chartData.domainX}
                stroke="hsl(var(--muted-foreground))"
                fontSize={11}
                tickFormatter={(value) => `${value.toFixed(0)}%`}
                tickCount={8}
              >
                <Label
                  value="Volatilidade Anualizada (Risco)"
                  offset={-10}
                  position="insideBottom"
                  style={{ fontSize: "12px", fill: "hsl(var(--muted-foreground))", fontWeight: 500 }}
                />
              </XAxis>
              <YAxis
                type="number"
                dataKey="return"
                name="Retorno"
                domain={chartData.domainY}
                stroke="hsl(var(--muted-foreground))"
                fontSize={11}
                tickFormatter={(value) => `${value.toFixed(0)}%`}
                tickCount={8}
              >
                <Label
                  value="Retorno Anualizado"
                  angle={-90}
                  position="insideLeft"
                  offset={-10}
                  style={{ fontSize: "12px", textAnchor: "middle", fill: "hsl(var(--muted-foreground))", fontWeight: 500 }}
                />
              </YAxis>
              <ZAxis range={[200, 200]} />

              {/* Risk-Free Rate Line (CDI dinâmico do backend) */}
              <ReferenceLine 
                y={chartData.riskFreeRatePct} 
                stroke="#22C55E" 
                strokeWidth={1.5}
                strokeDasharray="8 4"
              />

              {/* CAL - Capital Allocation Line */}
              <Line
                type="monotone"
                dataKey="return"
                data={chartData.calData}
                stroke="#F59E0B"
                strokeWidth={2}
                strokeDasharray="8 4"
                dot={false}
                activeDot={{ 
                  r: 6, 
                  fill: "#F59E0B", 
                  stroke: "#fff", 
                  strokeWidth: 2,
                  onMouseEnter: (e: any) => {
                    const point = e.payload
                    setActiveTooltip({ 
                      x: e.cx + 60, 
                      y: e.cy, 
                      data: { ...point, type: 'cal', name: 'Capital Allocation Line' } 
                    })
                  },
                  onMouseLeave: () => setActiveTooltip(null)
                }}
                name="Capital Allocation Line (CAL)"
                isAnimationActive={false}
              />

              {/* Fronteira Eficiente */}
              <Line
                type="monotone"
                dataKey="return"
                data={chartData.frontierData}
                stroke="#1F2937"
                strokeWidth={3}
                dot={false}
                activeDot={{ 
                  r: 6, 
                  fill: "#1F2937", 
                  stroke: "#fff", 
                  strokeWidth: 2,
                  onMouseEnter: (e: any) => {
                    const point = e.payload
                    setActiveTooltip({ 
                      x: e.cx + 60, 
                      y: e.cy, 
                      data: { ...point, type: 'frontier', name: 'Fronteira Eficiente' } 
                    })
                  },
                  onMouseLeave: () => setActiveTooltip(null)
                }}
                name="Fronteira Eficiente"
                isAnimationActive={false}
              />

              {/* Ativos Individuais */}
              <Scatter 
                name="Ativos Individuais" 
                data={chartData.individualAssets} 
                fill="#9CA3AF"
                isAnimationActive={false}
                shape={(props: any) => {
                  const { cx, cy, payload } = props
                  if (cx === undefined || cy === undefined) return <g />
                  return (
                    <g 
                      style={{ cursor: 'pointer' }}
                      onMouseEnter={(e) => setActiveTooltip({ x: e.clientX, y: e.clientY, data: payload })}
                      onMouseLeave={() => setActiveTooltip(null)}
                    >
                      <circle cx={cx} cy={cy} r={15} fill="transparent" />
                      <rect x={cx-7} y={cy-7} width={14} height={14} fill="#9CA3AF" stroke="#4B5563" strokeWidth={1.5} />
                    </g>
                  )
                }}
              />

              {/* Carteira Atual - com área de hover maior */}
              <Scatter
                name="Carteira Atual"
                data={[chartData.currentPortfolio]}
                fill="#EF4444"
                isAnimationActive={false}
                shape={(props: any) => {
                  const { cx, cy } = props
                  if (cx === undefined || cy === undefined) return <g />
                  return (
                    <g 
                      style={{ cursor: 'pointer' }}
                      onMouseEnter={(e) => setActiveTooltip({ x: e.clientX, y: e.clientY, data: chartData.currentPortfolio })}
                      onMouseLeave={() => setActiveTooltip(null)}
                    >
                      <circle cx={cx} cy={cy} r={25} fill="transparent" />
                      <polygon points={`${cx},${cy-10} ${cx+10},${cy} ${cx},${cy+10} ${cx-10},${cy}`} fill="#EF4444" stroke="#991B1B" strokeWidth={2} />
                    </g>
                  )
                }}
              />

              {/* Mínima Volatilidade - com área de hover maior */}
              <Scatter
                name="Mínima Volatilidade"
                data={[chartData.minVar]}
                fill="#3B82F6"
                isAnimationActive={false}
                shape={(props: any) => {
                  const { cx, cy } = props
                  if (cx === undefined || cy === undefined) return <g />
                  return (
                    <g 
                      style={{ cursor: 'pointer' }}
                      onMouseEnter={(e) => setActiveTooltip({ x: e.clientX, y: e.clientY, data: chartData.minVar })}
                      onMouseLeave={() => setActiveTooltip(null)}
                    >
                      <circle cx={cx} cy={cy} r={25} fill="transparent" />
                      <circle cx={cx} cy={cy} r={10} fill="#3B82F6" stroke="#1E40AF" strokeWidth={2} />
                    </g>
                  )
                }}
              />

              {/* Máximo Sharpe - com área de hover maior */}
              <Scatter
                name="Máximo Sharpe"
                data={[chartData.maxSharpe]}
                fill="#10B981"
                isAnimationActive={false}
                shape={(props: any) => {
                  const { cx, cy } = props
                  if (cx === undefined || cy === undefined) return <g />
                  return (
                    <g 
                      style={{ cursor: 'pointer' }}
                      onMouseEnter={(e) => setActiveTooltip({ x: e.clientX, y: e.clientY, data: chartData.maxSharpe })}
                      onMouseLeave={() => setActiveTooltip(null)}
                    >
                      <circle cx={cx} cy={cy} r={25} fill="transparent" />
                      <polygon points={`${cx},${cy-12} ${cx+5},${cy-5} ${cx+12},${cy} ${cx+5},${cy+5} ${cx},${cy+12} ${cx-5},${cy+5} ${cx-12},${cy} ${cx-5},${cy-5}`} fill="#10B981" stroke="#047857" strokeWidth={2} />
                    </g>
                  )
                }}
              />
            </ComposedChart>
          </ResponsiveContainer>
          
          {/* Tooltip customizado que segue o mouse */}
          {activeTooltip && (
            <div 
              className="fixed z-[9999] pointer-events-none bg-card border-2 border-border rounded-lg p-3 shadow-2xl min-w-[200px]"
              style={{ 
                left: activeTooltip.x + 15, 
                top: activeTooltip.y - 10,
              }}
            >
              <p className={`font-bold text-sm mb-2 pb-2 border-b border-border ${
                activeTooltip.data.type === 'current' ? 'text-red-500' :
                activeTooltip.data.type === 'maxSharpe' ? 'text-emerald-500' :
                activeTooltip.data.type === 'minVar' ? 'text-blue-500' :
                activeTooltip.data.type === 'frontier' ? 'text-gray-800 dark:text-gray-200' :
                activeTooltip.data.type === 'cal' ? 'text-orange-500' :
                'text-gray-500'
              }`}>
                {activeTooltip.data.type === 'current' ? '◆ Carteira Atual' :
                 activeTooltip.data.type === 'maxSharpe' ? '★ Máximo Sharpe' :
                 activeTooltip.data.type === 'minVar' ? '● Mínima Volatilidade' :
                 activeTooltip.data.type === 'frontier' ? '● Fronteira Eficiente' :
                 activeTooltip.data.type === 'cal' ? '- - Capital Allocation Line' :
                 `■ ${activeTooltip.data.name}`}
              </p>
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Retorno Anual:</span>
                  <span className="text-sm font-bold text-green-600">{activeTooltip.data.return?.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-muted-foreground">Volatilidade:</span>
                  <span className="text-sm font-bold text-orange-500">{activeTooltip.data.volatility?.toFixed(2)}%</span>
                </div>
                {activeTooltip.data.sharpe !== undefined && (
                  <div className="flex justify-between items-center pt-2 border-t border-border">
                    <span className="text-xs text-muted-foreground">Sharpe Ratio:</span>
                    <span className="text-sm font-bold text-amber-500">{activeTooltip.data.sharpe.toFixed(3)}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Legenda - Estilo padronizado com CVaR */}
        <div className="mt-5 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 rounded-lg bg-muted/50 border border-border px-4 py-3">
          <div className="flex items-center gap-2">
            <div className="h-[3px] w-6 rounded-full bg-gray-700 dark:bg-gray-300" />
            <span className="text-sm text-muted-foreground">Fronteira</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-[3px] w-6 rounded-full" style={{ background: 'repeating-linear-gradient(90deg, #F59E0B, #F59E0B 3px, transparent 3px, transparent 6px)' }} />
            <span className="text-sm text-muted-foreground">CAL</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-[3px] w-6 rounded-full" style={{ background: 'repeating-linear-gradient(90deg, #22C55E, #22C55E 3px, transparent 3px, transparent 6px)' }} />
            <span className="text-sm"><span className="text-muted-foreground">CDI:</span> <span className="font-semibold text-green-600">{chartData.riskFreeRatePct.toFixed(0)}%</span></span>
          </div>
          <div className="h-4 w-px bg-border" />
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-sm bg-gray-400" />
            <span className="text-sm text-muted-foreground">Ativos</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rotate-45 bg-red-500" />
            <span className="text-sm text-muted-foreground">Carteira</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-blue-500" />
            <span className="text-sm text-muted-foreground">Mín. Vol</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 bg-emerald-500" style={{ clipPath: 'polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%)' }} />
            <span className="text-sm text-muted-foreground">Máx. Sharpe</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
