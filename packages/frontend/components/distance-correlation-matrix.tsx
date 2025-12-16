"use client"

import { Fragment, useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useDashboardData } from "@/lib/dashboard-data-context"

// Função para determinar a cor baseada na distance correlation
// Distance correlation vai de 0 a 1 (sempre positiva)
// 0 = independência estatística, 1 = dependência perfeita
const getDistanceCorrelationColor = (value: number) => {
  // Independência ou muito baixa (bom para diversificação)
  if (value < 0.2) return "bg-emerald-600 text-white"
  if (value < 0.3) return "bg-emerald-500 text-white"
  if (value < 0.4) return "bg-green-400 text-slate-900"
  
  // Dependência moderada
  if (value < 0.5) return "bg-lime-400 text-slate-900"
  if (value < 0.6) return "bg-yellow-300 text-slate-900"
  if (value < 0.7) return "bg-amber-300 text-slate-900"
  
  // Dependência alta (ruim para diversificação)
  if (value < 0.8) return "bg-orange-400 text-slate-900"
  if (value < 0.9) return "bg-red-500 text-white"
  
  // Dependência muito alta (>=0.9, incluindo 1.0 da diagonal)
  return "bg-red-600 text-white"
}

export function DistanceCorrelationMatrix() {
  const { analysisResult } = useDashboardData()

  const matrixData = useMemo(() => {
    if (!analysisResult) {
      return null
    }

    // Usar dados do backend
    const backendDCor = analysisResult.distance_correlation_matrix
    
    if (backendDCor && backendDCor.matrix && backendDCor.matrix.length > 0) {
      return {
        assets: backendDCor.assets,
        matrix: backendDCor.matrix,
        avgCorrelation: backendDCor.avg_correlation,
        maxCorrelation: backendDCor.max_correlation,
        minCorrelation: backendDCor.min_correlation,
      }
    }

    return null
  }, [analysisResult])

  if (!matrixData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Matriz de Correlação de Distância</CardTitle>
          <CardDescription>Correlação não-linear entre os ativos da carteira</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-64">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar a matriz de distance correlation</p>
        </CardContent>
      </Card>
    )
  }

  const { assets, matrix, avgCorrelation, minCorrelation, maxCorrelation } = matrixData

  return (
    <Card>
      <CardHeader>
        <CardTitle>Matriz de Correlação de Distância</CardTitle>
        <CardDescription>Correlação não-linear entre os ativos da carteira</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div className="flex justify-center">
            <div className="grid gap-1" style={{ gridTemplateColumns: `80px repeat(${assets.length}, 60px)` }}>
              {/* Header vazio no canto */}
              <div className="h-12" />

              {/* Headers das colunas */}
              {assets.map((asset: string) => (
                <div
                  key={`header-${asset}`}
                  className="h-12 flex items-center justify-center text-xs font-semibold text-muted-foreground"
                >
                  {asset}
                </div>
              ))}

              {/* Linhas da matriz */}
              {assets.map((rowAsset: string, rowIndex: number) => (
                <Fragment key={`row-${rowAsset}`}>
                  {/* Header da linha */}
                  <div
                    className="h-12 flex items-center justify-end pr-2 text-xs font-semibold text-muted-foreground"
                  >
                    {rowAsset}
                  </div>

                  {/* Células da matriz */}
                  {matrix[rowIndex].map((value: number, colIndex: number) => (
                    <div
                      key={`cell-${rowIndex}-${colIndex}`}
                      className={`h-12 flex items-center justify-center text-xs font-semibold rounded transition-all hover:scale-105 hover:shadow-md cursor-default ${getDistanceCorrelationColor(value)}`}
                      title={`${assets[rowIndex]} vs ${assets[colIndex]}: ${value.toFixed(2)}`}
                    >
                      {value.toFixed(2)}
                    </div>
                  ))}
                </Fragment>
              ))}
            </div>
          </div>
        </div>

        {/* Legenda - Estatísticas */}
        <div className="mt-5 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 rounded-lg bg-muted/50 border border-border px-4 py-3">
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Média:</span> <span className="font-semibold">{avgCorrelation.toFixed(2)}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Menor:</span> <span className="font-semibold text-emerald-600">{minCorrelation.toFixed(2)}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Maior:</span> <span className="font-semibold text-red-600">{maxCorrelation.toFixed(2)}</span></span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
