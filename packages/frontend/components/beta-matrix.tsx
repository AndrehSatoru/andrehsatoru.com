"use client"

import { Fragment } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const assets = ["PETR4", "VALE3", "ITUB4", "BBDC4", "ABEV3", "WEGE3", "B3SA3", "RENT3"]

// Beta de cada ativo em relação ao benchmark (Ibovespa)
const betaData = [
  { asset: "PETR4", beta: 1.35, rSquared: 0.72 },
  { asset: "VALE3", beta: 1.28, rSquared: 0.68 },
  { asset: "ITUB4", beta: 1.15, rSquared: 0.81 },
  { asset: "BBDC4", beta: 1.18, rSquared: 0.79 },
  { asset: "ABEV3", beta: 0.65, rSquared: 0.45 },
  { asset: "WEGE3", beta: 0.92, rSquared: 0.58 },
  { asset: "B3SA3", beta: 1.05, rSquared: 0.75 },
  { asset: "RENT3", beta: 0.88, rSquared: 0.62 },
]

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

export function BetaMatrix() {
  const avgBeta = betaData.reduce((sum, item) => sum + item.beta, 0) / betaData.length
  const avgRSquared = betaData.reduce((sum, item) => sum + item.rSquared, 0) / betaData.length

  return (
    <Card>
      <CardHeader>
        <CardTitle>Matriz de Beta</CardTitle>
        <CardDescription>Beta e R² de cada ativo em relação ao benchmark (Ibovespa)</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div className="inline-block min-w-full">
            <div className="grid gap-1" style={{ gridTemplateColumns: "120px 100px 100px" }}>
              {/* Headers */}
              <div className="h-12 flex items-center justify-start text-xs font-semibold text-muted-foreground">
                Ativo
              </div>
              <div className="h-12 flex items-center justify-center text-xs font-semibold text-muted-foreground">
                Beta (β)
              </div>
              <div className="h-12 flex items-center justify-center text-xs font-semibold text-muted-foreground">
                R²
              </div>

              {/* Linhas da matriz */}
              {betaData.map((item) => (
                <Fragment key={`row-${item.asset}`}>
                  {/* Nome do ativo */}
                  <div
                    key={`asset-${item.asset}`}
                    className="h-12 flex items-center justify-start text-sm font-semibold text-foreground"
                  >
                    {item.asset}
                  </div>

                  {/* Beta */}
                  <div
                    key={`beta-${item.asset}`}
                    className={`h-12 flex items-center justify-center text-sm font-bold rounded transition-all hover:scale-105 hover:shadow-md cursor-default ${getBetaColor(item.beta)}`}
                    title={`Beta de ${item.asset}: ${item.beta.toFixed(2)}`}
                  >
                    {item.beta.toFixed(2)}
                  </div>

                  {/* R² */}
                  <div
                    key={`rsquared-${item.asset}`}
                    className={`h-12 flex items-center justify-center text-sm font-bold rounded transition-all hover:scale-105 hover:shadow-md cursor-default ${getRSquaredColor(item.rSquared)}`}
                    title={`R² de ${item.asset}: ${(item.rSquared * 100).toFixed(1)}%`}
                  >
                    {(item.rSquared * 100).toFixed(0)}%
                  </div>
                </Fragment>
              ))}
            </div>
          </div>
        </div>

        {/* Legenda */}
        <div className="mt-6 space-y-3">
          <div className="flex items-center justify-center gap-6 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-emerald-600" />
              <span className="text-muted-foreground">Beta Baixo (&lt;0.9)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-amber-400" />
              <span className="text-muted-foreground">Beta Neutro (0.9-1.1)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-red-600" />
              <span className="text-muted-foreground">Beta Alto (&gt;1.1)</span>
            </div>
          </div>
          <div className="text-center text-xs text-muted-foreground">
            R² indica a qualidade do ajuste do modelo (quanto maior, mais confiável o beta)
          </div>
        </div>

        {/* Estatísticas */}
        <div className="mt-6 grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-foreground">{avgBeta.toFixed(2)}</div>
            <div className="text-xs text-muted-foreground">Beta Médio da Carteira</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{(avgRSquared * 100).toFixed(0)}%</div>
            <div className="text-xs text-muted-foreground">R² Médio</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
