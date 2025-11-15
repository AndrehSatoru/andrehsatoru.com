"use client"

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

const generateEfficientFrontier = () => {
  const points = []
  for (let i = 0; i <= 100; i++) {
    const volatility = 10 + (i / 100) * 35
    // Curva mais realista com formato de fronteira eficiente
    const t = i / 100
    const returnValue = 10 + Math.sqrt(t) * 50 + Math.pow(t, 3) * 20
    points.push({
      volatility: Number(volatility.toFixed(2)),
      return: Number(returnValue.toFixed(2)),
      type: "frontier",
    })
  }
  return points
}

const generateCAL = () => {
  const points = []
  const riskFreeRate = 5 // Taxa livre de risco
  const sharpePoint = { volatility: 19, return: 55 } // Ponto de tangência (Máximo Sharpe)

  for (let i = 0; i <= 100; i++) {
    const volatility = (i / 100) * 45
    const returnValue = riskFreeRate + ((sharpePoint.return - riskFreeRate) / sharpePoint.volatility) * volatility
    points.push({
      volatility: Number(volatility.toFixed(2)),
      return: Number(returnValue.toFixed(2)),
      type: "cal",
    })
  }
  return points
}

const individualAssets = [
  { name: "Ativo 1", volatility: 40, return: 76, type: "asset" },
  { name: "Ativo 2", volatility: 38, return: 65, type: "asset" },
  { name: "Ativo 3", volatility: 45, return: -20, type: "asset" },
  { name: "Ativo 4", volatility: 42, return: -45, type: "asset" },
  { name: "Ativo 5", volatility: 35, return: 37, type: "asset" },
  { name: "Ativo 6", volatility: 33, return: 27, type: "asset" },
  { name: "Ativo 7", volatility: 32, return: 10, type: "asset" },
  { name: "Ativo 8", volatility: 28, return: 38, type: "asset" },
  { name: "Ativo 9", volatility: 25, return: 15, type: "asset" },
  { name: "Ativo 10", volatility: 30, return: -22, type: "asset" },
  { name: "Ativo 11", volatility: 22, return: 4, type: "asset" },
  { name: "Ativo 12", volatility: 24, return: -8, type: "asset" },
  { name: "Ativo 13", volatility: 26, return: 5, type: "asset" },
  { name: "Ativo 14", volatility: 20, return: 38, type: "asset" },
]

const specialPortfolios = [
  { name: "Carteira Atual (Backtest)", volatility: 11, return: 25, type: "current" },
  { name: "Mínima Volatilidade (11.35%)", volatility: 11.35, return: 11, type: "minVar" },
  { name: "Máximo Sharpe (2.70)", volatility: 19, return: 55, type: "maxSharpe" },
]

const frontierData = generateEfficientFrontier()
const calData = generateCAL()

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    return (
      <div className="bg-card border border-border rounded-lg p-3 shadow-lg">
        <p className="font-semibold text-sm mb-1 text-foreground">{data.name || "Fronteira Eficiente"}</p>
        <p className="text-xs text-muted-foreground">
          Retorno: <span className="text-foreground font-medium">{data.return.toFixed(1)}%</span>
        </p>
        <p className="text-xs text-muted-foreground">
          Volatilidade: <span className="text-foreground font-medium">{data.volatility.toFixed(1)}%</span>
        </p>
        {data.type === "maxSharpe" && <p className="text-xs text-amber-500 mt-1">Sharpe Ratio: 2.70</p>}
      </div>
    )
  }
  return null
}

const CustomShape = (props: any) => {
  const { cx, cy, fill, payload } = props
  const size = 8

  if (payload.type === "maxSharpe") {
    // Estrela amarela com borda preta
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
    // Círculo amarelo com borda preta
    return <circle cx={cx} cy={cy} r={size} fill="#FCD34D" stroke="#000" strokeWidth="2" />
  } else if (payload.type === "current") {
    // Diamante vermelho com borda preta
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
    // Quadrados cinzas para ativos individuais
    return <rect x={cx - size / 2} y={cy - size / 2} width={size} height={size} fill="#9CA3AF" />
  }

  return <circle cx={cx} cy={cy} r={3} fill={fill} />
}

export function EfficientFrontier() {
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
                domain={[0, 50]}
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
                domain={[-40, 80]}
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
                formatter={(value, entry: any) => {
                  if (value === "Fronteira Eficiente")
                    return <span className="text-sm text-foreground">— Fronteira Eficiente</span>
                  if (value === "Capital Allocation Line (CAL)")
                    return <span className="text-sm text-foreground">- - - Capital Allocation Line (CAL)</span>
                  if (value === "Ativos Individuais")
                    return <span className="text-sm text-foreground">▪ Ativos Individuais</span>
                  if (value === "Máximo Sharpe (2.70)")
                    return <span className="text-sm text-foreground">★ Máximo Sharpe (2.70)</span>
                  if (value === "Mínima Volatilidade (11.35%)")
                    return <span className="text-sm text-foreground">● Mínima Volatilidade (11.35%)</span>
                  if (value === "Carteira Atual (Backtest)")
                    return <span className="text-sm text-foreground">◆ Carteira Atual (Backtest)</span>
                  return value
                }}
              />

              <Line
                type="monotone"
                dataKey="return"
                data={calData}
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
                data={frontierData}
                stroke="#1F2937"
                strokeWidth={3}
                dot={false}
                name="Fronteira Eficiente"
                isAnimationActive={true}
              />

              <Scatter name="Ativos Individuais" data={individualAssets} fill="#9CA3AF" shape={<CustomShape />} />

              <Scatter
                name="Máximo Sharpe (2.70)"
                data={specialPortfolios.filter((p) => p.type === "maxSharpe")}
                fill="#FCD34D"
                shape={<CustomShape />}
              />

              <Scatter
                name="Mínima Volatilidade (11.35%)"
                data={specialPortfolios.filter((p) => p.type === "minVar")}
                fill="#FCD34D"
                shape={<CustomShape />}
              />

              <Scatter
                name="Carteira Atual (Backtest)"
                data={specialPortfolios.filter((p) => p.type === "current")}
                fill="#EF4444"
                shape={<CustomShape />}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6 pt-6 border-t border-border">
          <div>
            <p className="text-xs text-muted-foreground mb-1">Carteira Atual (Backtest)</p>
            <p className="text-sm font-semibold text-foreground">11.0% vol | 25.0% ret</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Mínima Volatilidade</p>
            <p className="text-sm font-semibold text-foreground">11.35% vol | 11.0% ret</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Máximo Sharpe</p>
            <p className="text-sm font-semibold text-amber-500">19.0% vol | 55.0% ret | SR: 2.70</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
