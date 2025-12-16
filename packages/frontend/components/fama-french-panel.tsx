"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend } from "recharts"

// Cores para cada fator
const factorColors = {
  mkt_beta: "#3b82f6", // blue
  smb_beta: "#10b981", // green
  hml_beta: "#f59e0b", // amber
}

const getAlphaColor = (alpha: number) => {
  if (alpha > 5) return "text-green-600"
  if (alpha > 0) return "text-green-500"
  if (alpha > -5) return "text-red-400"
  return "text-red-600"
}

export function FamaFrenchPanel() {
  const { analysisResult } = useDashboardData()

  const ffData = useMemo(() => {
    if (!analysisResult?.fama_french) {
      return null
    }

    const ff = analysisResult.fama_french

    if (ff.error || !ff.items || ff.items.length === 0) {
      return null
    }

    return ff
  }, [analysisResult])

  if (!ffData) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-2xl">📊</span>
            Análise Fama-French
          </CardTitle>
          <CardDescription>
            Modelo de 3 fatores não disponível
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
            Dados insuficientes para análise Fama-French
          </div>
        </CardContent>
      </Card>
    )
  }

  // Preparar dados para o gráfico
  const chartData = ffData.items.map((item: any) => ({
    name: item.asset,
    'Mercado (MKT)': item.mkt_beta,
    'Tamanho (SMB)': item.smb_beta,
    'Valor (HML)': item.hml_beta,
  }))

  const exposure = ffData.portfolio_exposure || {}

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">📊</span>
          Análise Fama-French (3 Fatores)
        </CardTitle>
        <CardDescription>
          Exposição aos fatores de Mercado, Tamanho (SMB) e Valor (HML)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 lg:grid-cols-3 mb-6">
          {/* Cards de exposição do portfólio */}
          <div className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="text-sm text-blue-600 dark:text-blue-400 font-medium">
              Beta de Mercado (MKT)
            </div>
            <div className="text-3xl font-bold text-blue-700 dark:text-blue-300">
              {exposure.mkt_beta?.toFixed(2) || 'N/A'}
            </div>
            <div className="text-xs text-blue-500 dark:text-blue-400 mt-1">
              Exposição ao prêmio de risco do mercado
            </div>
          </div>

          <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800">
            <div className="text-sm text-green-600 dark:text-green-400 font-medium">
              Fator Tamanho (SMB)
            </div>
            <div className="text-3xl font-bold text-green-700 dark:text-green-300">
              {exposure.smb_beta?.toFixed(2) || 'N/A'}
            </div>
            <div className="text-xs text-green-500 dark:text-green-400 mt-1">
              Small Minus Big - empresas menores vs maiores
            </div>
          </div>

          <div className="p-4 bg-amber-50 dark:bg-amber-950 rounded-lg border border-amber-200 dark:border-amber-800">
            <div className="text-sm text-amber-600 dark:text-amber-400 font-medium">
              Fator Valor (HML)
            </div>
            <div className="text-3xl font-bold text-amber-700 dark:text-amber-300">
              {exposure.hml_beta?.toFixed(2) || 'N/A'}
            </div>
            <div className="text-xs text-amber-500 dark:text-amber-400 mt-1">
              High Minus Low - value vs growth
            </div>
          </div>
        </div>

        {/* Gráfico de barras */}
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" margin={{ left: 20, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[-1, 2]} />
              <YAxis type="category" dataKey="name" width={60} />
              <Tooltip 
                formatter={(value: number) => value.toFixed(3)}
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))'
                }}
              />
              <Legend />
              <Bar dataKey="Mercado (MKT)" fill="#3b82f6" />
              <Bar dataKey="Tamanho (SMB)" fill="#10b981" />
              <Bar dataKey="Valor (HML)" fill="#f59e0b" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Tabela de detalhes */}
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-2">Ativo</th>
                <th className="text-right py-2 px-2">Peso</th>
                <th className="text-right py-2 px-2">Alpha (a.a.)</th>
                <th className="text-right py-2 px-2">MKT β</th>
                <th className="text-right py-2 px-2">SMB β</th>
                <th className="text-right py-2 px-2">HML β</th>
                <th className="text-right py-2 px-2">R²</th>
              </tr>
            </thead>
            <tbody>
              {ffData.items.map((item: any) => (
                <tr key={item.asset} className="border-b hover:bg-muted/50">
                  <td className="py-2 px-2 font-medium">{item.asset}</td>
                  <td className="text-right py-2 px-2">{(item.weight ?? 0).toFixed(1)}%</td>
                  <td className={`text-right py-2 px-2 font-semibold ${getAlphaColor(item.alpha ?? 0)}`}>
                    {(item.alpha ?? 0) > 0 ? '+' : ''}{(item.alpha ?? 0).toFixed(2)}%
                  </td>
                  <td className="text-right py-2 px-2">{(item.mkt_beta ?? 0).toFixed(2)}</td>
                  <td className="text-right py-2 px-2">{(item.smb_beta ?? 0).toFixed(2)}</td>
                  <td className="text-right py-2 px-2">{(item.hml_beta ?? 0).toFixed(2)}</td>
                  <td className="text-right py-2 px-2">{((item.r_squared ?? 0) * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Legenda dos fatores */}
        <div className="mt-4 p-4 bg-muted/50 rounded-lg text-xs space-y-1">
          <p><strong>MKT (Mercado):</strong> Exposição ao prêmio de risco do mercado. β&gt;1 = mais sensível, β&lt;1 = mais defensivo.</p>
          <p><strong>SMB (Small Minus Big):</strong> Exposição ao fator tamanho. Positivo = tende a se comportar como small caps, negativo = como large caps.</p>
          <p><strong>HML (High Minus Low):</strong> Exposição ao fator valor. Positivo = viés para ações de valor, negativo = viés para ações de crescimento.</p>
          <p><strong>Alpha (α):</strong> Retorno excedente não explicado pelos 3 fatores. Positivo indica geração de valor além da exposição a fatores.</p>
          <p><strong>R²:</strong> Proporção do retorno explicada pelo modelo. R² baixo pode indicar exposição a outros fatores não capturados.</p>
        </div>
      </CardContent>
    </Card>
  )
}
