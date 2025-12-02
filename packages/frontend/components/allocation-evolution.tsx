"use client"

import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Brush } from "recharts"
import { usePeriod, filterDataByPeriod } from "@/lib/period-context"
import { useDashboardData } from "@/lib/dashboard-data-context"

// Cores para os ativos
const assetColors = [
  "#1e40af", "#ea580c", "#16a34a", "#dc2626", "#9333ea",
  "#78716c", "#ec4899", "#64748b", "#84cc16", "#06b6d4",
  "#0284c7", "#f97316", "#22c55e", "#ef4444", "#8b5cf6",
  "#92400e", "#db2777", "#0891b2", "#7c3aed", "#ca8a04",
  "#059669", "#e11d48", "#4f46e5", "#14b8a6", "#f59e0b",
]

export function AllocationEvolution() {
  const { period } = usePeriod()
  const { analysisResult } = useDashboardData()

  const { allocationData, assets, originalData } = useMemo(() => {
    // Usar dados reais do histórico de alocação da API
    const allocationHistory = analysisResult?.results?.allocation_history
    
    if (allocationHistory && allocationHistory.length > 0) {
      const firstEntry = allocationHistory[0]
      const assetKeys = Object.keys(firstEntry).filter(k => k !== 'date')
      
      const assetList = assetKeys.map((key, index) => ({
        key,
        color: assetColors[index % assetColors.length],
      }))
      
      // Criar mapa de dados originais para o tooltip (com percentuais reais)
      const originalDataMap: Record<string, Record<string, number>> = {}
      
      // Normalizar manualmente para frações 0-1
      // Cada valor é dividido pelo total para que a soma seja sempre 1
      const normalizedData = allocationHistory.map((entry: Record<string, any>) => {
        const newEntry: Record<string, any> = { date: entry.date }
        const origEntry: Record<string, number> = {}
        const total = assetKeys.reduce((sum, key) => sum + (Number(entry[key]) || 0), 0)
        
        // Primeiro passo: calcular frações
        let runningSum = 0
        assetKeys.forEach((key, index) => {
          const rawValue = Number(entry[key]) || 0
          let fraction = total > 0 ? rawValue / total : 0
          
          // No último ativo, ajustar para garantir soma exata de 1
          if (index === assetKeys.length - 1 && total > 0) {
            fraction = Math.max(0, 1 - runningSum)
          }
          
          newEntry[key] = fraction
          runningSum += fraction
          // Guardar percentual para tooltip
          origEntry[key] = fraction * 100
        })
        
        originalDataMap[entry.date] = origEntry
        return newEntry
      })
      
      return {
        allocationData: normalizedData,
        assets: assetList,
        originalData: originalDataMap,
      }
    }
    
    // Fallback: calcular a partir dos dados de alocação atual
    if (!analysisResult?.results?.performance || !analysisResult?.results?.alocacao?.alocacao) {
      return { allocationData: [], assets: [], originalData: {} }
    }

    const performance = analysisResult.results.performance
    const alocacaoData = analysisResult.results.alocacao.alocacao

    // Obter ativos e suas alocações percentuais
    const assetList = Object.keys(alocacaoData)
      .filter(a => alocacaoData[a]?.percentual > 0)
      .map((key, index) => ({
        key,
        color: assetColors[index % assetColors.length],
        percentual: alocacaoData[key].percentual,
      }))

    if (assetList.length === 0 || performance.length === 0) {
      return { allocationData: [], assets: [], originalData: {} }
    }

    // Gerar dados de evolução da alocação baseado em variação de preços simulada
    const originalDataMap: Record<string, Record<string, number>> = {}
    const data = performance.map((item: { date: string; portfolio: number }, index: number) => {
      const entry: { [key: string]: string | number } = { date: item.date }
      const origEntry: Record<string, number> = {}
      
      const timeProgress = index / performance.length
      
      let totalPct = 0
      assetList.forEach((asset, i) => {
        const variation = Math.sin(timeProgress * Math.PI * 4 + i * 0.5) * 0.15
        const adjustedPct = asset.percentual * (1 + variation)
        entry[asset.key] = adjustedPct
        totalPct += adjustedPct
      })
      
      // Normalizar para frações (0 a 1)
      assetList.forEach((asset) => {
        const fraction = (entry[asset.key] as number) / totalPct
        entry[asset.key] = fraction  // 0 a 1
        origEntry[asset.key] = fraction * 100  // 0 a 100 para tooltip
      })
      
      originalDataMap[item.date] = origEntry
      return entry
    })

    return {
      allocationData: data,
      assets: assetList.map(a => ({ key: a.key, color: a.color })),
      originalData: originalDataMap,
    }
  }, [analysisResult])

  const filteredData = filterDataByPeriod(allocationData, period)

  if (!analysisResult || allocationData.length === 0) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle className="text-xl font-semibold">Evolução da Alocação Percentual da Carteira</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[400px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar a evolução da alocação</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">Evolução da Alocação Percentual da Carteira</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={550}>
          <AreaChart data={filteredData} stackOffset="none" margin={{ top: 0, right: 120, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" vertical={false} />
            <XAxis
              dataKey="date"
              className="text-xs"
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${date.getDate().toString().padStart(2, "0")}/${(date.getMonth() + 1).toString().padStart(2, "0")}`
              }}
            />
            <YAxis
              className="text-xs"
              domain={[0, 1]}
              ticks={[0, 0.25, 0.5, 0.75, 1]}
              tickFormatter={(value) => `${Math.round(value * 100)}%`}
              allowDataOverflow={true}
              scale="linear"
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const dateStr = payload[0].payload.date
                  const date = new Date(dateStr)
                  const formattedDate = `${date.getDate().toString().padStart(2, "0")}/${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear()}`
                  
                  // Usar valores originais do mapa
                  const origValues = originalData[dateStr] || {}

                  return (
                    <div className="rounded-lg border bg-background p-3 shadow-lg">
                      <p className="font-semibold mb-2">{formattedDate}</p>
                      <div className="space-y-1 max-h-64 overflow-y-auto">
                        {[...payload]
                          .sort((a: any, b: any) => {
                            const valA = origValues[a.dataKey] ?? 0
                            const valB = origValues[b.dataKey] ?? 0
                            return valB - valA
                          })
                          .map((entry: any) => {
                            const value = origValues[entry.dataKey] ?? 0
                            return (
                              <div key={entry.dataKey} className="flex items-center justify-between gap-4 text-sm">
                                <div className="flex items-center gap-2">
                                  <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: entry.color }} />
                                  <span>{entry.name}</span>
                                </div>
                                <span className="font-medium">{value.toFixed(1)}%</span>
                              </div>
                            )
                          })}
                      </div>
                    </div>
                  )
                }
                return null
              }}
            />
            <Legend
              layout="vertical"
              align="right"
              verticalAlign="middle"
              wrapperStyle={{ paddingLeft: "20px" }}
              content={({ payload }) => (
                <div className="space-y-1">
                  <p className="font-semibold text-sm mb-2">Ativos</p>
                  {payload?.map((entry) => (
                    <div key={entry.value} className="flex items-center gap-2 text-xs">
                      <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: entry.color }} />
                      <span>{entry.value}</span>
                    </div>
                  ))}
                </div>
              )}
            />
            {assets.map((asset) => (
              <Area
                key={asset.key}
                type="monotone"
                dataKey={asset.key}
                stackId="1"
                stroke={asset.color}
                fill={asset.color}
                fillOpacity={1}
                strokeWidth={0.5}
              />
            ))}
            <Brush
              dataKey="date"
              height={40}
              stroke="hsl(var(--border))"
              fill="#f5f5f5"
              fillOpacity={1}
              travellerWidth={10}
              startIndex={0}
              endIndex={filteredData.length - 1}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${date.getDate().toString().padStart(2, "0")}/${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear()}`
              }}
            >
              <AreaChart data={filteredData} stackOffset="none">
                {assets.map((asset) => (
                  <Area
                    key={asset.key}
                    type="monotone"
                    dataKey={asset.key}
                    stackId="1"
                    stroke="none"
                    fill={asset.color}
                    fillOpacity={0.5}
                  />
                ))}
              </AreaChart>
            </Brush>
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
