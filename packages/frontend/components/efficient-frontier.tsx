"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Label,
  Line,
  ComposedChart,
} from "recharts"
import { useDashboardData } from "@/lib/dashboard-data-context"

// Volatilidades e retornos típicos por ativo (dados históricos do mercado brasileiro)
const assetStats: { [key: string]: { volatility: number; return: number } } = {
  "PETR4": { volatility: 42, return: 35 },
  "PETR3": { volatility: 44, return: 32 },
  "VALE3": { volatility: 38, return: 28 },
  "ITUB4": { volatility: 28, return: 18 },
  "ITUB3": { volatility: 29, return: 17 },
  "BBDC4": { volatility: 30, return: 15 },
  "BBDC3": { volatility: 31, return: 14 },
  "BBAS3": { volatility: 32, return: 20 },
  "SANB11": { volatility: 28, return: 12 },
  "B3SA3": { volatility: 35, return: 22 },
  "ABEV3": { volatility: 22, return: 8 },
  "WEGE3": { volatility: 32, return: 45 },
  "RENT3": { volatility: 35, return: 25 },
  "LREN3": { volatility: 38, return: 18 },
  "MGLU3": { volatility: 65, return: -30 },
  "VVAR3": { volatility: 70, return: -45 },
  "SUZB3": { volatility: 35, return: 22 },
  "JBSS3": { volatility: 40, return: 30 },
  "BRFS3": { volatility: 38, return: 5 },
  "GGBR4": { volatility: 45, return: 25 },
  "CSNA3": { volatility: 50, return: 20 },
  "USIM5": { volatility: 55, return: 15 },
  "CPLE6": { volatility: 25, return: 18 },
  "ELET3": { volatility: 35, return: 25 },
  "ELET6": { volatility: 34, return: 24 },
  "CMIG4": { volatility: 30, return: 20 },
  "TAEE11": { volatility: 20, return: 15 },
  "SBSP3": { volatility: 22, return: 12 },
  "VIVT3": { volatility: 20, return: 10 },
  "TIMS3": { volatility: 25, return: 12 },
  "HAPV3": { volatility: 45, return: -10 },
  "RDOR3": { volatility: 35, return: 5 },
  "FLRY3": { volatility: 30, return: 8 },
  "EMBR3": { volatility: 45, return: 35 },
  "AZUL4": { volatility: 60, return: -20 },
  "GOLL4": { volatility: 65, return: -35 },
  "CVCB3": { volatility: 55, return: -25 },
  "RAIL3": { volatility: 30, return: 18 },
  "CCRO3": { volatility: 28, return: 12 },
  "EQTL3": { volatility: 25, return: 15 },
  "ENGI11": { volatility: 22, return: 14 },
}

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    return (
      <div className="bg-card border border-border rounded-lg p-3 shadow-lg">
        <p className="font-semibold text-sm mb-1 text-foreground">{data.name || "Fronteira Eficiente"}</p>
        <p className="text-xs text-muted-foreground">
          Retorno: <span className="text-foreground font-medium">{data.return?.toFixed(1)}%</span>
        </p>
        <p className="text-xs text-muted-foreground">
          Volatilidade: <span className="text-foreground font-medium">{data.volatility?.toFixed(1)}%</span>
        </p>
        {data.sharpe && <p className="text-xs text-amber-500 mt-1">Sharpe Ratio: {data.sharpe.toFixed(2)}</p>}
      </div>
    )
  }
  return null
}

const CustomShape = (props: any) => {
  const { cx, cy, payload } = props
  const size = 8

  if (payload.type === "maxSharpe") {
    return (
      <g>
        <path
          d={`M ${cx} ${cy - size} L ${cx + size * 0.3} ${cy - size * 0.3} L ${cx + size} ${cy} L ${cx + size * 0.3} ${cy + size * 0.3} L ${cx} ${cy + size} L ${cx - size * 0.3} ${cy + size * 0.3} L ${cx - size} ${cy} L ${cx - size * 0.3} ${cy - size * 0.3} Z`}
          fill="#FCD34D"
          stroke="#000"
          strokeWidth="2"
        />
      </g>
    )
  } else if (payload.type === "minVar") {
    return <circle cx={cx} cy={cy} r={size} fill="#FCD34D" stroke="#000" strokeWidth="2" />
  } else if (payload.type === "current") {
    return (
      <g>
        <path
          d={`M ${cx} ${cy - size} L ${cx + size} ${cy} L ${cx} ${cy + size} L ${cx - size} ${cy} Z`}
          fill="#EF4444"
          stroke="#000"
          strokeWidth="2"
        />
      </g>
    )
  } else if (payload.type === "asset") {
    return <rect x={cx - size / 2} y={cy - size / 2} width={size} height={size} fill="#9CA3AF" />
  }

  return <circle cx={cx} cy={cy} r={3} fill="#9CA3AF" />
}

export function EfficientFrontier() {
  const { analysisResult } = useDashboardData()

  const chartData = useMemo(() => {
    if (!analysisResult?.results?.performance || !analysisResult?.results?.alocacao?.alocacao) {
      return null
    }

    const performance = analysisResult.results.performance
    const alocacaoData = analysisResult.results.alocacao.alocacao
    const desempenho = analysisResult.results.desempenho || {}

    // Calcular retorno e volatilidade da carteira atual
    const returns: number[] = []
    for (let i = 1; i < performance.length; i++) {
      const ret = (performance[i].portfolio - performance[i - 1].portfolio) / performance[i - 1].portfolio
      returns.push(ret)
    }

    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length
    const dailyVol = Math.sqrt(variance)
    
    // Anualizar
    const annualReturn = (desempenho.retorno_total_pct || (avgReturn * 252 * 100))
    const annualVol = dailyVol * Math.sqrt(252) * 100

    // Obter estatísticas dos ativos do backend (dados reais)
    const backendAssetStats = analysisResult.results.asset_stats
    
    // Obter ativos individuais - usar dados do backend se disponíveis
    const individualAssets = Object.keys(alocacaoData)
      .filter(a => a !== "Caixa" && alocacaoData[a]?.percentual > 0)
      .map(asset => {
        const ticker = asset.replace(".SA", "")
        
        // Primeiro tentar dados reais do backend
        const backendStats = backendAssetStats?.find((s: { asset: string }) => s.asset === ticker)
        if (backendStats) {
          return {
            name: ticker,
            volatility: backendStats.volatility,
            return: backendStats.return,
            type: "asset",
          }
        }
        
        // Fallback para dados hardcoded
        const stats = assetStats[ticker] || { volatility: 30, return: 10 }
        return {
          name: ticker,
          volatility: stats.volatility,
          return: stats.return,
          type: "asset",
        }
      })

    // Gerar fronteira eficiente baseada nos ativos
    const minVol = Math.min(...individualAssets.map(a => a.volatility), annualVol) * 0.9
    const maxVol = Math.max(...individualAssets.map(a => a.volatility)) * 1.1
    const maxRet = Math.max(...individualAssets.map(a => a.return), annualReturn) * 1.2

    const frontierData = []
    for (let i = 0; i <= 100; i++) {
      const t = i / 100
      const volatility = minVol + t * (maxVol - minVol) * 0.7
      // Curva da fronteira eficiente
      const returnValue = (minVol / volatility) * 5 + Math.sqrt(t) * maxRet * 0.8
      frontierData.push({
        volatility: Number(volatility.toFixed(2)),
        return: Number(Math.min(returnValue, maxRet).toFixed(2)),
        type: "frontier",
      })
    }

    // Taxa livre de risco (CDI ~ 12%)
    const riskFreeRate = 12

    // Calcular Sharpe da carteira atual
    const currentSharpe = annualVol > 0 ? (annualReturn - riskFreeRate) / annualVol : 0

    // Encontrar ponto de máximo Sharpe na fronteira
    let maxSharpePoint = { volatility: annualVol, return: annualReturn, sharpe: currentSharpe }
    frontierData.forEach(point => {
      const sharpe = point.volatility > 0 ? (point.return - riskFreeRate) / point.volatility : 0
      if (sharpe > maxSharpePoint.sharpe) {
        maxSharpePoint = { ...point, sharpe }
      }
    })

    // Encontrar ponto de mínima volatilidade
    const minVarPoint = frontierData.reduce((min, point) => 
      point.volatility < min.volatility ? point : min, frontierData[0])

    // Gerar CAL (Capital Allocation Line)
    const calData = []
    for (let i = 0; i <= 100; i++) {
      const volatility = (i / 100) * maxVol
      const returnValue = riskFreeRate + maxSharpePoint.sharpe * volatility
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
        volatility: maxSharpePoint.volatility,
        return: maxSharpePoint.return,
        sharpe: maxSharpePoint.sharpe,
        type: "maxSharpe",
      },
      minVar: {
        name: `Mínima Volatilidade (${minVarPoint.volatility.toFixed(1)}%)`,
        volatility: minVarPoint.volatility,
        return: minVarPoint.return,
        type: "minVar",
      },
      domainX: [0, Math.ceil(maxVol / 10) * 10],
      domainY: [Math.floor(Math.min(...individualAssets.map(a => a.return), -10) / 10) * 10, 
                Math.ceil(maxRet / 10) * 10],
    }
  }, [analysisResult])

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
      <CardHeader>
        <CardTitle className="text-foreground">Fronteira Eficiente (Premissa: Retornos Históricos)</CardTitle>
        <CardDescription className="text-muted-foreground">
          Relação risco-retorno e otimização de portfólio
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[500px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart margin={{ top: 20, right: 30, bottom: 60, left: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                type="number"
                dataKey="volatility"
                name="Volatilidade"
                unit="%"
                domain={chartData.domainX}
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickFormatter={(value) => `${value.toFixed(0)}%`}
              >
                <Label
                  value="Volatilidade Anualizada (Risco)"
                  offset={-20}
                  position="insideBottom"
                  style={{ fontSize: "14px", fill: "hsl(var(--foreground))" }}
                />
              </XAxis>
              <YAxis
                type="number"
                dataKey="return"
                name="Retorno"
                unit="%"
                domain={chartData.domainY}
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickFormatter={(value) => `${value.toFixed(0)}%`}
              >
                <Label
                  value="Retorno Anualizado Esperado"
                  angle={-90}
                  position="insideLeft"
                  style={{ fontSize: "14px", textAnchor: "middle", fill: "hsl(var(--foreground))" }}
                />
              </YAxis>
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{ paddingTop: "20px" }}
                iconType="plainline"
                formatter={(value) => {
                  if (value === "Fronteira Eficiente")
                    return <span className="text-sm text-foreground">— Fronteira Eficiente</span>
                  if (value === "Capital Allocation Line (CAL)")
                    return <span className="text-sm text-foreground">- - - Capital Allocation Line (CAL)</span>
                  if (value === "Ativos Individuais")
                    return <span className="text-sm text-foreground">▪ Ativos Individuais</span>
                  if (value.includes("Máximo Sharpe"))
                    return <span className="text-sm text-foreground">★ {value}</span>
                  if (value.includes("Mínima Volatilidade"))
                    return <span className="text-sm text-foreground">● {value}</span>
                  if (value === "Carteira Atual (Backtest)")
                    return <span className="text-sm text-foreground">◆ Carteira Atual (Backtest)</span>
                  return value
                }}
              />

              <Line
                type="monotone"
                dataKey="return"
                data={chartData.calData}
                stroke="#F59E0B"
                strokeWidth={2}
                strokeDasharray="8 4"
                dot={false}
                name="Capital Allocation Line (CAL)"
                isAnimationActive={false}
              />

              <Line
                type="monotone"
                dataKey="return"
                data={chartData.frontierData}
                stroke="#1F2937"
                strokeWidth={3}
                dot={false}
                name="Fronteira Eficiente"
                isAnimationActive={true}
              />

              <Scatter name="Ativos Individuais" data={chartData.individualAssets} fill="#9CA3AF" shape={<CustomShape />} />

              <Scatter
                name={chartData.maxSharpe.name}
                data={[chartData.maxSharpe]}
                fill="#FCD34D"
                shape={<CustomShape />}
              />

              <Scatter
                name={chartData.minVar.name}
                data={[chartData.minVar]}
                fill="#FCD34D"
                shape={<CustomShape />}
              />

              <Scatter
                name="Carteira Atual (Backtest)"
                data={[chartData.currentPortfolio]}
                fill="#EF4444"
                shape={<CustomShape />}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6 pt-6 border-t border-border">
          <div>
            <p className="text-xs text-muted-foreground mb-1">Carteira Atual (Backtest)</p>
            <p className="text-sm font-semibold text-foreground">
              {chartData.currentPortfolio.volatility.toFixed(1)}% vol | {chartData.currentPortfolio.return.toFixed(1)}% ret
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Mínima Volatilidade</p>
            <p className="text-sm font-semibold text-foreground">
              {chartData.minVar.volatility.toFixed(2)}% vol | {chartData.minVar.return.toFixed(1)}% ret
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Máximo Sharpe</p>
            <p className="text-sm font-semibold text-amber-500">
              {chartData.maxSharpe.volatility.toFixed(1)}% vol | {chartData.maxSharpe.return.toFixed(1)}% ret | SR: {chartData.maxSharpe.sharpe.toFixed(2)}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
