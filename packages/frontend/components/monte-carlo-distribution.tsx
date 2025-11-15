"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts"

// Simulated Monte Carlo distribution data
const generateDistributionData = () => {
  const data = []
  const initialValue = 164898026.23

  // Generate histogram bins with 5M intervals instead of 10M
  for (let value = 100000000; value <= 350000000; value += 5000000) {
    // MGB with GARCH - centered around initial value with slight positive skew
    const mgbDensity = Math.exp(-Math.pow((value - 165000000) / 25000000, 2)) * 2.1

    // Bootstrap Historical - centered around 200M with wider spread
    const bootstrapDensity = Math.exp(-Math.pow((value - 200000000) / 30000000, 2)) * 1.7

    data.push({
      value,
      mgb: mgbDensity > 0.05 ? mgbDensity : 0,
      bootstrap: bootstrapDensity > 0.05 ? bootstrapDensity : 0,
      valueLabel: `R$ ${(value / 1000000).toFixed(0)}M`,
    })
  }

  return { data, initialValue }
}

const { data, initialValue } = generateDistributionData()

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-background border border-border p-3 rounded-lg shadow-lg">
        <p className="font-semibold mb-1">{payload[0].payload.valueLabel}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} style={{ color: entry.color }} className="text-sm">
            {entry.name}: {entry.value.toFixed(4)}
          </p>
        ))}
      </div>
    )
  }
  return null
}

export function MonteCarloDistribution() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-balance">Distribuição Comparativa dos Resultados de Monte Carlo</CardTitle>
        <div className="flex flex-wrap gap-4 mt-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-[#F59E0B] border border-[#D97706]" />
            <span>MGB (Drift Anualizado: 0.00%) com GARCH</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-[#6B7280] border border-[#4B5563]" />
            <span>Bootstrap Histórico</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className="w-4 h-0.5 bg-black border-dashed"
              style={{ borderTop: "2px dashed black", width: "20px" }}
            />
            <span>Valor Inicial: R$ {(initialValue / 1000000).toFixed(1)}M</span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[500px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart
              data={data}
              margin={{ top: 20, right: 30, left: 80, bottom: 60 }}
              barCategoryGap={0}
              barGap={-20}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="valueLabel"
                angle={-45}
                textAnchor="end"
                height={80}
                tick={{ fill: "hsl(var(--foreground))", fontSize: 11 }}
                label={{
                  value: "Valor Final da Carteira (R$)",
                  position: "insideBottom",
                  offset: -40,
                  style: { fill: "hsl(var(--foreground))", fontSize: 12 },
                }}
              />
              <YAxis
                tick={{ fill: "hsl(var(--foreground))", fontSize: 11 }}
                label={{
                  value: "Densidade",
                  angle: -90,
                  position: "insideLeft",
                  style: { fill: "hsl(var(--foreground))", fontSize: 12 },
                }}
                domain={[0, 2.5]}
              />
              <Tooltip content={<CustomTooltip />} />

              {/* Reference line for initial value */}
              <ReferenceLine x="R$ 165M" stroke="#000" strokeDasharray="5 5" strokeWidth={2} />

              {/* Bars for distributions */}
              <Bar
                dataKey="mgb"
                fill="#F59E0B"
                fillOpacity={0.8}
                stroke="#D97706"
                strokeWidth={1}
                name="MGB com GARCH"
              />
              <Bar
                dataKey="bootstrap"
                fill="#6B7280"
                fillOpacity={0.8}
                stroke="#4B5563"
                strokeWidth={1}
                name="Bootstrap Histórico"
              />

              {/* Lines for smooth density curves */}
              <Line
                type="monotone"
                dataKey="mgb"
                stroke="#D97706"
                strokeWidth={2}
                dot={false}
                name=""
                legendType="none"
              />
              <Line
                type="monotone"
                dataKey="bootstrap"
                stroke="#374151"
                strokeWidth={2}
                dot={false}
                name=""
                legendType="none"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t">
          <div>
            <p className="text-sm text-muted-foreground">Valor Inicial</p>
            <p className="text-lg font-semibold">R$ {(initialValue / 1000000).toFixed(2)}M</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Mediana MGB</p>
            <p className="text-lg font-semibold text-amber-600">R$ 165.0M</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Mediana Bootstrap</p>
            <p className="text-lg font-semibold text-gray-600">R$ 200.0M</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
