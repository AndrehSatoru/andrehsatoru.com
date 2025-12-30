"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine, ComposedChart, Line } from "recharts"

// Cores para os ativos
const COLORS = [
  '#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
]

export function IncrementalVarAnalysis() {
  const { analysisResult } = useDashboardData()

  const ivarData = useMemo(() => {
    if (!analysisResult?.incremental_var) {
      return null
    }

    const data = analysisResult.incremental_var

    if (data.error || !data.items || data.items.length === 0) {
      return null
    }

    return data
  }, [analysisResult])

  if (!ivarData) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-2xl">⚡</span>
            Incremental VaR
          </CardTitle>
          <CardDescription>
            Impacto de cada ativo no VaR do portfólio
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
            Dados insuficientes para análise de Incremental VaR
          </div>
        </CardContent>
      </Card>
    )
  }

  const { items, portfolio_var, undiversified_var, diversification_benefit, diversification_ratio, confidence_level } = ivarData

  // Preparar dados para gráficos
  const componentVarData = items.map((item: any, idx: number) => ({
    name: item.asset,
    'VaR Individual': item.individual_var * item.weight / 100,
    'Component VaR': item.component_var,
    'Benefício Diversif.': item.diversification_benefit,
    color: COLORS[idx % COLORS.length]
  }))

  const contributionData = items.map((item: any, idx: number) => ({
    name: item.asset,
    value: item.var_contribution_pct,
    color: COLORS[idx % COLORS.length]
  }))

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">⚡</span>
          Incremental VaR (IVaR)
        </CardTitle>
        <CardDescription>
          Impacto marginal de cada ativo no risco do portfólio • VaR {confidence_level}%
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 lg:grid-cols-4 mb-6">
          {/* Card VaR do Portfólio */}
          <div className="p-4 rounded-lg border bg-red-50 dark:bg-red-950 border-red-200">
            <div className="text-sm font-medium text-red-600 dark:text-red-400">
              VaR do Portfólio
            </div>
            <div className="text-3xl font-bold text-red-700 dark:text-red-300">
              {portfolio_var.toFixed(2)}%
            </div>
            <div className="text-xs text-red-500 mt-1">
              Perda máxima {confidence_level}% confiança
            </div>
          </div>

          {/* Card VaR Não-Diversificado */}
          <div className="p-4 rounded-lg border bg-slate-50 dark:bg-slate-950 border-slate-200">
            <div className="text-sm font-medium text-slate-600 dark:text-slate-400">
              VaR Não-Diversificado
            </div>
            <div className="text-3xl font-bold text-slate-700 dark:text-slate-300">
              {undiversified_var.toFixed(2)}%
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Soma dos VaRs individuais
            </div>
          </div>

          {/* Card Benefício de Diversificação */}
          <div className="p-4 rounded-lg border bg-green-50 dark:bg-green-950 border-green-200">
            <div className="text-sm font-medium text-green-600 dark:text-green-400">
              Benefício de Diversificação
            </div>
            <div className="text-3xl font-bold text-green-700 dark:text-green-300">
              {diversification_benefit.toFixed(2)}%
            </div>
            <div className="text-xs text-green-500 mt-1">
              Redução do risco por diversificação
            </div>
          </div>

          {/* Card Razão de Diversificação */}
          <div className="p-4 rounded-lg border bg-blue-50 dark:bg-blue-950 border-blue-200">
            <div className="text-sm font-medium text-blue-600 dark:text-blue-400">
              Razão de Diversificação
            </div>
            <div className="text-3xl font-bold text-blue-700 dark:text-blue-300">
              {diversification_ratio.toFixed(2)}x
            </div>
            <div className="text-xs text-blue-500 mt-1">
              {diversification_ratio > 1.3 ? 'Boa diversificação' : 'Diversificação limitada'}
            </div>
          </div>
        </div>

        {/* Gráfico Comparativo */}
        <div className="h-[400px]">
          <h4 className="font-semibold mb-3 text-sm">VaR Individual vs Component VaR (contribuição real)</h4>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={componentVarData} layout="vertical" margin={{ left: 10, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 'auto']} unit="%" />
              <YAxis type="category" dataKey="name" width={60} />
              <Tooltip 
                formatter={(value: any, name: any) => [`${value.toFixed(3)}%`, name]}
                contentStyle={{ 
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))'
                }}
              />
              <Bar dataKey="VaR Individual" fill="#94a3b8" name="VaR Individual (× peso)" opacity={0.5} />
              <Bar dataKey="Component VaR" name="Component VaR (real)">
                {componentVarData.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
              <ReferenceLine x={0} stroke="#000" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Tabela Detalhada */}
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-2">Ativo</th>
                <th className="text-right py-2 px-2">Peso</th>
                <th className="text-right py-2 px-2">VaR Individual</th>
                <th className="text-right py-2 px-2">MVaR</th>
                <th className="text-right py-2 px-2">IVaR</th>
                <th className="text-right py-2 px-2">Component VaR</th>
                <th className="text-right py-2 px-2">% do VaR Total</th>
                <th className="text-right py-2 px-2">Diversificação</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item: any, idx: number) => (
                <tr key={item.asset} className="border-b hover:bg-muted/50">
                  <td className="py-2 px-2">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                      />
                      <span className="font-medium">{item.asset}</span>
                    </div>
                  </td>
                  <td className="text-right py-2 px-2">{(item.weight ?? 0).toFixed(1)}%</td>
                  <td className="text-right py-2 px-2 text-slate-600">{(item.individual_var ?? 0).toFixed(2)}%</td>
                  <td className="text-right py-2 px-2 text-blue-600">{(item.marginal_var ?? 0).toFixed(4)}%</td>
                  <td className="text-right py-2 px-2 text-purple-600">{(item.incremental_var ?? 0).toFixed(4)}%</td>
                  <td className="text-right py-2 px-2 text-red-600 font-semibold">{(item.component_var ?? 0).toFixed(2)}%</td>
                  <td className="text-right py-2 px-2 font-semibold">{(item.var_contribution_pct ?? 0).toFixed(1)}%</td>
                  <td className={`text-right py-2 px-2 ${(item.diversification_benefit ?? 0) > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {(item.diversification_benefit ?? 0) > 0 ? '+' : ''}{(item.diversification_benefit ?? 0).toFixed(3)}%
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="border-t-2 font-semibold bg-muted/50">
                <td className="py-2 px-2">TOTAL</td>
                <td className="text-right py-2 px-2">100%</td>
                <td className="text-right py-2 px-2 text-slate-600">{undiversified_var.toFixed(2)}%</td>
                <td className="text-right py-2 px-2">-</td>
                <td className="text-right py-2 px-2">-</td>
                <td className="text-right py-2 px-2 text-red-600">{portfolio_var.toFixed(2)}%</td>
                <td className="text-right py-2 px-2">100%</td>
                <td className="text-right py-2 px-2 text-green-600">+{diversification_benefit.toFixed(2)}%</td>
              </tr>
            </tfoot>
          </table>
        </div>

        {/* Insight Box */}
        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          <div className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg border border-blue-200">
            <h4 className="font-semibold text-blue-700 dark:text-blue-300 mb-2">
              💡 O que significa cada métrica?
            </h4>
            <div className="text-xs space-y-1 text-blue-600 dark:text-blue-400">
              <p><strong>VaR Individual:</strong> VaR do ativo se fosse o único no portfólio.</p>
              <p><strong>MVaR (Marginal):</strong> ∂VaR/∂w - quanto o VaR muda se aumentar 1% no peso.</p>
              <p><strong>IVaR (Incremental):</strong> w × MVaR - impacto marginal considerando peso atual.</p>
              <p><strong>Component VaR:</strong> Contribuição real ao VaR do portfólio (soma = VaR total).</p>
            </div>
          </div>

          <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200">
            <h4 className="font-semibold text-green-700 dark:text-green-300 mb-2">
              📊 Interpretação da Diversificação
            </h4>
            <div className="text-xs space-y-1 text-green-600 dark:text-green-400">
              <p>• <strong>Razão {'>'}1.5x:</strong> Excelente diversificação, correlações baixas entre ativos.</p>
              <p>• <strong>Razão 1.2-1.5x:</strong> Boa diversificação, benefício significativo.</p>
              <p>• <strong>Razão {'<'}1.2x:</strong> Diversificação limitada, ativos muito correlacionados.</p>
              <p>• <strong>Benefício negativo:</strong> Ativo aumenta risco mais que proporcional ao peso.</p>
            </div>
          </div>
        </div>

        {/* Legenda */}
        <div className="mt-4 p-4 bg-muted/50 rounded-lg text-xs">
          <p>
            <strong>Como usar:</strong> Ativos com alta contribuição ao VaR (% do VaR Total) e baixo benefício 
            de diversificação são candidatos a redução de peso. Ativos com diversificação positiva alta 
            estão ajudando a reduzir o risco do portfólio.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

