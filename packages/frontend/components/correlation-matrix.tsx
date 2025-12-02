"use client"

import { Fragment, useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useDashboardData } from "@/lib/dashboard-data-context"

// Função para determinar a cor baseada na correlação
// Paleta: Vermelho (negativa) -> Laranja -> Amarelo (neutra) -> Verde claro -> Verde escuro (alta)
const getCorrelationColor = (value: number) => {
  // Correlações negativas: tons de vermelho
  if (value <= -0.6) return "bg-red-600 text-white"
  if (value <= -0.4) return "bg-red-500 text-white"
  if (value <= -0.2) return "bg-red-400 text-white"
  if (value < 0) return "bg-orange-400 text-slate-900"
  
  // Correlações baixas/neutras: tons de amarelo/âmbar
  if (value < 0.2) return "bg-amber-200 text-slate-900"
  if (value < 0.3) return "bg-yellow-300 text-slate-900"
  
  // Correlações moderadas: tons de verde claro
  if (value < 0.4) return "bg-lime-300 text-slate-900"
  if (value < 0.5) return "bg-lime-400 text-slate-900"
  if (value < 0.6) return "bg-green-400 text-slate-900"
  
  // Correlações altas: tons de verde escuro
  if (value < 0.7) return "bg-green-500 text-white"
  if (value < 0.8) return "bg-emerald-500 text-white"
  if (value < 0.9) return "bg-emerald-600 text-white"
  
  // Correlação muito alta (>=0.9, incluindo 1.0 da diagonal)
  return "bg-emerald-700 text-white"
}

// Função para calcular correlação de Pearson
const pearsonCorrelation = (x: number[], y: number[]): number => {
  const n = Math.min(x.length, y.length)
  if (n < 2) return 0

  let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0, sumY2 = 0

  for (let i = 0; i < n; i++) {
    sumX += x[i]
    sumY += y[i]
    sumXY += x[i] * y[i]
    sumX2 += x[i] * x[i]
    sumY2 += y[i] * y[i]
  }

  const numerator = n * sumXY - sumX * sumY
  const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY))

  return denominator === 0 ? 0 : numerator / denominator
}

export function CorrelationMatrix() {
  const { analysisResult } = useDashboardData()

  const matrixData = useMemo(() => {
    if (!analysisResult?.results) {
      return null
    }

    // Primeiro, tentar usar dados reais calculados pelo backend
    const backendCorrelation = analysisResult.results.correlation_matrix
    
    if (backendCorrelation && backendCorrelation.matrix && backendCorrelation.matrix.length > 0) {
      // Usar dados reais do backend
      return {
        assets: backendCorrelation.assets,
        matrix: backendCorrelation.matrix,
        avgCorrelation: backendCorrelation.avg_correlation,
        maxCorrelation: backendCorrelation.max_correlation,
        minCorrelation: backendCorrelation.min_correlation,
        source: 'calculated' as const
      }
    }

    // Fallback: calcular baseado em setores (estimativa)
    if (!analysisResult?.results?.alocacao?.alocacao) {
      return null
    }

    const alocacaoData = analysisResult.results.alocacao.alocacao

    // Extrair ativos da alocação (excluindo "Caixa")
    const assets = Object.keys(alocacaoData)
      .filter(a => a !== "Caixa" && alocacaoData[a]?.percentual > 0)
      .map(a => a.replace(".SA", ""))

    if (assets.length < 2) {
      return null
    }

    // Gerar correlações baseadas em setores típicos
    const sectorGroups: { [key: string]: string } = {
      "PETR4": "commodities",
      "VALE3": "commodities",
      "ITUB4": "financeiro",
      "BBDC4": "financeiro",
      "BBAS3": "financeiro",
      "SANB11": "financeiro",
      "ABEV3": "consumo",
      "WEGE3": "industrial",
      "B3SA3": "financeiro",
      "RENT3": "consumo",
      "MGLU3": "varejo",
      "VVAR3": "varejo",
      "LREN3": "varejo",
      "SUZB3": "commodities",
      "JBSS3": "consumo",
      "BRFS3": "consumo",
      "GGBR4": "commodities",
      "CSNA3": "commodities",
      "USIM5": "commodities",
      "CPLE6": "utilidades",
      "ELET3": "utilidades",
      "ELET6": "utilidades",
      "CMIG4": "utilidades",
      "TAEE11": "utilidades",
      "VIVT3": "telecom",
      "TIMS3": "telecom",
      "PRIO3": "commodities",
    }

    // Calcular correlação baseada em setor (simplificação)
    const correlationMatrix: number[][] = []
    for (let i = 0; i < assets.length; i++) {
      const row: number[] = []
      for (let j = 0; j < assets.length; j++) {
        if (i === j) {
          row.push(1.0)
        } else {
          const sector1 = sectorGroups[assets[i]] || "outros"
          const sector2 = sectorGroups[assets[j]] || "outros"
          
          // Correlação base: mesmos setores têm correlação maior
          let baseCorr = sector1 === sector2 ? 0.75 : 0.35
          
          // Adicionar variação baseada nos nomes dos ativos (para consistência)
          const hash = (assets[i].charCodeAt(0) + assets[j].charCodeAt(0)) / 200
          baseCorr += (hash - 0.5) * 0.3
          baseCorr = Math.max(-0.5, Math.min(0.95, baseCorr))
          
          row.push(Math.round(baseCorr * 100) / 100)
        }
      }
      correlationMatrix.push(row)
    }

    // Calcular estatísticas
    let sum = 0, count = 0, max = -Infinity, min = Infinity
    for (let i = 0; i < correlationMatrix.length; i++) {
      for (let j = i + 1; j < correlationMatrix[i].length; j++) {
        const val = correlationMatrix[i][j]
        sum += val
        count++
        if (val > max) max = val
        if (val < min) min = val
      }
    }

    return {
      assets,
      matrix: correlationMatrix,
      avgCorrelation: count > 0 ? sum / count : 0,
      maxCorrelation: max === -Infinity ? 0 : max,
      minCorrelation: min === Infinity ? 0 : min,
      source: 'estimated' as const
    }
  }, [analysisResult])

  if (!matrixData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Matriz de Correlação</CardTitle>
          <CardDescription>Correlação entre os retornos dos ativos da carteira</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[300px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar a matriz de correlação</p>
        </CardContent>
      </Card>
    )
  }

  const { assets, matrix, avgCorrelation, maxCorrelation, minCorrelation } = matrixData

  return (
    <Card>
      <CardHeader>
        <CardTitle>Matriz de Correlação</CardTitle>
        <CardDescription>
          Correlação entre os retornos dos ativos da carteira
          {matrixData.source === 'estimated' && (
            <span className="ml-2 text-amber-600">(valores estimados)</span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div className="flex justify-center">
            <div className="grid gap-1" style={{ gridTemplateColumns: `80px repeat(${assets.length}, 60px)` }}>
              {/* Header vazio no canto */}
              <div className="h-12" />

              {/* Headers das colunas */}
              {assets.map((asset) => (
                <div
                  key={`header-${asset}`}
                  className="h-12 flex items-center justify-center text-xs font-semibold text-muted-foreground"
                >
                  {asset}
                </div>
              ))}

              {/* Linhas da matriz */}
              {assets.map((rowAsset, rowIndex) => (
                <Fragment key={`row-${rowAsset}`}>
                  {/* Header da linha */}
                  <div
                    className="h-12 flex items-center justify-end pr-2 text-xs font-semibold text-muted-foreground"
                  >
                    {rowAsset}
                  </div>

                  {/* Células da matriz */}
                  {matrix[rowIndex].map((value, colIndex) => (
                    <div
                      key={`cell-${rowIndex}-${colIndex}`}
                      className={`h-12 flex items-center justify-center text-xs font-semibold rounded transition-all hover:scale-105 hover:shadow-md cursor-default ${getCorrelationColor(value)}`}
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

        {/* Legenda - Estilo padronizado com CVaR */}
        <div className="mt-5 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 rounded-lg bg-muted/50 border border-border px-4 py-3">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded bg-red-500" />
            <span className="text-sm text-muted-foreground">Negativa</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded bg-orange-400" />
            <span className="text-sm text-muted-foreground">Fraca</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded bg-amber-200 border border-amber-300" />
            <span className="text-sm text-muted-foreground">Baixa</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded bg-lime-400" />
            <span className="text-sm text-muted-foreground">Moderada</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded bg-green-500" />
            <span className="text-sm text-muted-foreground">Alta</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded bg-emerald-700" />
            <span className="text-sm text-muted-foreground">Muito Alta</span>
          </div>
          <div className="h-4 w-px bg-border" />
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Média:</span> <span className="font-semibold">{avgCorrelation.toFixed(2)}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Maior:</span> <span className="font-semibold text-emerald-600">{maxCorrelation.toFixed(2)}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Menor:</span> <span className="font-semibold text-amber-600">{minCorrelation.toFixed(2)}</span></span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
