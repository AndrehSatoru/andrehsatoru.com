"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useDashboardData } from "@/lib/dashboard-data-context"

// Função para determinar a cor baseada no beta
const getBetaColor = (beta: number) => {
  if (beta >= 1.3) return "bg-red-600 text-white"
  if (beta >= 1.1) return "bg-orange-500 text-white"
  if (beta >= 0.9) return "bg-amber-400 text-slate-900"
  if (beta >= 0.7) return "bg-emerald-400 text-slate-900"
  return "bg-emerald-600 text-white"
}

// Função para determinar a cor do R²
const getRSquaredColor = (rSquared: number) => {
  if (rSquared >= 0.8) return "bg-blue-600 text-white"
  if (rSquared >= 0.6) return "bg-blue-500 text-white"
  if (rSquared >= 0.4) return "bg-blue-400 text-slate-900"
  return "bg-blue-300 text-slate-900"
}

// Betas típicos por setor (valores baseados em dados históricos do mercado brasileiro)
const sectorBetas: { [key: string]: { beta: number; rSquared: number } } = {
  // Commodities - Alta volatilidade
  "PETR4": { beta: 1.35, rSquared: 0.72 },
  "PETR3": { beta: 1.32, rSquared: 0.70 },
  "VALE3": { beta: 1.28, rSquared: 0.68 },
  "SUZB3": { beta: 1.15, rSquared: 0.55 },
  "GGBR4": { beta: 1.22, rSquared: 0.62 },
  "CSNA3": { beta: 1.30, rSquared: 0.58 },
  "USIM5": { beta: 1.35, rSquared: 0.52 },
  "JBSS3": { beta: 1.10, rSquared: 0.48 },
  "BRFS3": { beta: 0.95, rSquared: 0.45 },
  
  // Financeiro - Alta correlação com mercado
  "ITUB4": { beta: 1.15, rSquared: 0.81 },
  "ITUB3": { beta: 1.12, rSquared: 0.79 },
  "BBDC4": { beta: 1.18, rSquared: 0.79 },
  "BBDC3": { beta: 1.15, rSquared: 0.77 },
  "BBAS3": { beta: 1.08, rSquared: 0.75 },
  "SANB11": { beta: 1.05, rSquared: 0.72 },
  "B3SA3": { beta: 1.05, rSquared: 0.75 },
  
  // Consumo - Beta moderado
  "ABEV3": { beta: 0.65, rSquared: 0.45 },
  "RENT3": { beta: 0.88, rSquared: 0.62 },
  "LREN3": { beta: 0.92, rSquared: 0.58 },
  "MGLU3": { beta: 1.45, rSquared: 0.42 },
  "VVAR3": { beta: 1.50, rSquared: 0.38 },
  
  // Industrial
  "WEGE3": { beta: 0.92, rSquared: 0.58 },
  "EMBR3": { beta: 1.02, rSquared: 0.48 },
  
  // Utilidades - Defensivo
  "CPLE6": { beta: 0.55, rSquared: 0.42 },
  "ELET3": { beta: 0.78, rSquared: 0.52 },
  "ELET6": { beta: 0.75, rSquared: 0.50 },
  "CMIG4": { beta: 0.68, rSquared: 0.48 },
  "TAEE11": { beta: 0.45, rSquared: 0.38 },
  "SBSP3": { beta: 0.52, rSquared: 0.42 },
  
  // Telecom - Defensivo
  "VIVT3": { beta: 0.58, rSquared: 0.52 },
  "TIMS3": { beta: 0.62, rSquared: 0.48 },
  
  // Saúde
  "HAPV3": { beta: 0.85, rSquared: 0.45 },
  "RDOR3": { beta: 0.78, rSquared: 0.42 },
  "FLRY3": { beta: 0.72, rSquared: 0.40 },
}

export function BetaMatrix() {
  const { analysisResult } = useDashboardData()

  const betaData = useMemo(() => {
    if (!analysisResult) {
      return null
    }

    // Primeiro, tentar usar dados reais calculados pelo backend
    const backendBetaMatrix = analysisResult.beta_matrix
    
    if (backendBetaMatrix && backendBetaMatrix.items && backendBetaMatrix.items.length > 0) {
      // Usar dados reais do backend
      const data = backendBetaMatrix.items.map((item: { asset: string; beta: number; r_squared: number; weight: number }) => ({
        asset: item.asset.replace(".SA", ""),
        beta: item.beta,
        rSquared: item.r_squared,
        weight: item.weight,
      }))

      return {
        items: data,
        avgBeta: backendBetaMatrix.avg_beta,
        avgRSquared: backendBetaMatrix.avg_r_squared,
        source: 'calculated' as const
      }
    }

    // Fallback: usar dados hardcoded baseados em setor
    if (!analysisResult?.alocacao?.alocacao) {
      return null
    }

    const alocacaoData = analysisResult.alocacao.alocacao

    // Extrair ativos da alocação (excluindo "Caixa")
    const assets = Object.keys(alocacaoData)
      .filter(a => a !== "Caixa" && alocacaoData[a]?.percentual > 0)

    if (assets.length < 1) {
      return null
    }

    // Obter beta para cada ativo (fallback para dados hardcoded)
    const data = assets.map(asset => {
      const ticker = asset.replace(".SA", "")
      const sectorData = sectorBetas[ticker]
      const weight = (alocacaoData[asset]?.percentual || 0) / 100
      
      if (sectorData) {
        return {
          asset: ticker,
          beta: sectorData.beta,
          rSquared: sectorData.rSquared,
          weight: weight,
        }
      }
      
      // Default para ativos não mapeados
      return {
        asset: ticker,
        beta: 1.0,
        rSquared: 0.50,
        weight: weight,
      }
    })

    // Calcular beta ponderado da carteira
    const totalWeight = data.reduce((sum, item) => sum + item.weight, 0)
    const avgBeta = data.reduce((sum, item) => sum + item.beta * item.weight, 0) / (totalWeight || 1)
    const avgRSquared = data.reduce((sum, item) => sum + item.rSquared * item.weight, 0) / (totalWeight || 1)

    return {
      items: data,
      avgBeta,
      avgRSquared,
      source: 'estimated' as const
    }
  }, [analysisResult])

  if (!betaData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Matriz de Beta</CardTitle>
          <CardDescription>Beta e R² de cada ativo em relação ao benchmark (Ibovespa)</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[300px]">
          <p className="text-muted-foreground text-sm">Envie operações para visualizar a matriz de beta</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Matriz de Beta</CardTitle>
        <CardDescription>
          Beta e R² de cada ativo em relação ao benchmark (Ibovespa)
          {betaData.source === 'estimated' && (
            <span className="ml-2 text-amber-600">(valores estimados)</span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div className="flex justify-center">
            <div className="grid gap-1" style={{ gridTemplateColumns: `80px repeat(${betaData.items.length}, minmax(70px, 1fr))` }}>
              {/* Header - Ativo */}
              <div className="h-10 flex items-center justify-end pr-2 text-xs font-semibold text-muted-foreground">
                Ativo
              </div>
              {/* Headers - Nomes dos ativos */}
              {betaData.items.map((item: any) => (
                <div
                  key={`header-${item.asset}`}
                  className="h-10 flex items-center justify-center text-xs font-semibold text-foreground"
                >
                  {item.asset}
                </div>
              ))}

              {/* Linha Beta */}
              <div className="h-12 flex items-center justify-end pr-2 text-xs font-semibold text-muted-foreground">
                Beta (β)
              </div>
              {betaData.items.map((item: any) => (
                <div
                  key={`beta-${item.asset}`}
                  className={`h-12 flex items-center justify-center text-sm font-bold rounded transition-all hover:scale-105 hover:shadow-md cursor-default ${getBetaColor(item.beta)}`}
                  title={`Beta de ${item.asset}: ${item.beta.toFixed(2)}`}
                >
                  {item.beta.toFixed(2)}
                </div>
              ))}

              {/* Linha R² */}
              <div className="h-12 flex items-center justify-end pr-2 text-xs font-semibold text-muted-foreground">
                R²
              </div>
              {betaData.items.map((item: any) => (
                <div
                  key={`rsquared-${item.asset}`}
                  className={`h-12 flex items-center justify-center text-sm font-bold rounded transition-all hover:scale-105 hover:shadow-md cursor-default ${getRSquaredColor(item.rSquared)}`}
                  title={`R² de ${item.asset}: ${(item.rSquared * 100).toFixed(1)}%`}
                >
                  {(item.rSquared * 100).toFixed(0)}%
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Legenda - Estilo padronizado com CVaR */}
        <div className="mt-5 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 rounded-lg bg-muted/50 border border-border px-4 py-3">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded bg-emerald-600" />
            <span className="text-sm text-muted-foreground">Beta Baixo (&lt;0.9)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded bg-amber-400" />
            <span className="text-sm text-muted-foreground">Beta Neutro (0.9-1.1)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded bg-red-600" />
            <span className="text-sm text-muted-foreground">Beta Alto (&gt;1.1)</span>
          </div>
          <div className="h-4 w-px bg-border" />
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">Beta Médio:</span> <span className="font-semibold">{betaData.avgBeta.toFixed(2)}</span></span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm"><span className="text-muted-foreground">R² Médio:</span> <span className="font-semibold text-blue-600">{(betaData.avgRSquared * 100).toFixed(0)}%</span></span>
          </div>
        </div>
        <div className="mt-2 text-center text-xs text-muted-foreground">
          R² indica a qualidade do ajuste do modelo (quanto maior, mais confiável o beta)
        </div>
      </CardContent>
    </Card>
  )
}

