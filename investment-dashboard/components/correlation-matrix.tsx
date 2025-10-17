"use client"

import { Fragment } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

const assets = ["PETR4", "VALE3", "ITUB4", "BBDC4", "ABEV3", "WEGE3", "B3SA3", "RENT3"]

// Matriz de correlação simulada (valores entre -1 e 1)
const correlationData = [
  [1.0, 0.72, 0.45, 0.48, 0.23, 0.35, 0.52, 0.41],
  [0.72, 1.0, 0.38, 0.42, 0.18, 0.29, 0.47, 0.36],
  [0.45, 0.38, 1.0, 0.85, 0.31, 0.42, 0.68, 0.54],
  [0.48, 0.42, 0.85, 1.0, 0.28, 0.39, 0.71, 0.52],
  [0.23, 0.18, 0.31, 0.28, 1.0, 0.15, 0.25, 0.19],
  [0.35, 0.29, 0.42, 0.39, 0.15, 1.0, 0.44, 0.58],
  [0.52, 0.47, 0.68, 0.71, 0.25, 0.44, 1.0, 0.62],
  [0.41, 0.36, 0.54, 0.52, 0.19, 0.58, 0.62, 1.0],
]

// Função para determinar a cor baseada na correlação
const getCorrelationColor = (value: number) => {
  if (value >= 0.8) return "bg-emerald-600 text-white"
  if (value >= 0.6) return "bg-emerald-500 text-white"
  if (value >= 0.4) return "bg-emerald-400 text-white"
  if (value >= 0.2) return "bg-emerald-300 text-slate-900"
  if (value >= 0) return "bg-emerald-200 text-slate-900"
  if (value >= -0.2) return "bg-red-200 text-slate-900"
  if (value >= -0.4) return "bg-red-300 text-slate-900"
  if (value >= -0.6) return "bg-red-400 text-white"
  if (value >= -0.8) return "bg-red-500 text-white"
  return "bg-red-600 text-white"
}

export function CorrelationMatrix() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Matriz de Correlação</CardTitle>
        <CardDescription>Correlação entre os retornos dos ativos da carteira</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <div className="inline-block min-w-full">
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
                  {correlationData[rowIndex].map((value, colIndex) => (
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

        {/* Legenda */}
        <div className="mt-6 flex items-center justify-center gap-6 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-red-500" />
            <span className="text-muted-foreground">Correlação Negativa</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-emerald-200" />
            <span className="text-muted-foreground">Correlação Baixa</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-emerald-500" />
            <span className="text-muted-foreground">Correlação Alta</span>
          </div>
        </div>

        {/* Estatísticas */}
        <div className="mt-6 grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-foreground">0.45</div>
            <div className="text-xs text-muted-foreground">Correlação Média</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-emerald-600">0.85</div>
            <div className="text-xs text-muted-foreground">Maior Correlação</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-amber-600">0.15</div>
            <div className="text-xs text-muted-foreground">Menor Correlação</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
