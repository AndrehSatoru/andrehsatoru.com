"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from "recharts"

// Cores para os ativos
const COLORS = [
  '#3b82f6', '#ef4444', '#22c55e', '#f59e0b', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
]

export function RiskAttributionDetailed() {
  const { analysisResult } = useDashboardData()

  const attributionData = useMemo(() => {
    if (!analysisResult?.results?.risk_attribution_detailed) {
      return null
    }

    const data = analysisResult.results.risk_attribution_detailed

    if (data.error || !data.items || data.items.length === 0) {
      return null
    }

    return data
  }, [analysisResult])

  if (!attributionData) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-2xl">📊</span>
            Atribuição de Risco
          </CardTitle>
          <CardDescription>
            Contribuição de cada ativo para o risco total
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
            Dados insuficientes para análise de atribuição de risco
          </div>
        </CardContent>
      </Card>
    )
  }

  const { items, portfolio_volatility, portfolio_var_99, concentration } = attributionData

  // Preparar dados para gráficos
  const barData = items.map((item: any, idx: number) => ({
    name: item.asset,
    'Contribuição %': item.risk_contribution_pct,
    color: COLORS[idx % COLORS.length]
  }))

  const pieData = items.map((item: any, idx: number) => ({
    name: item.asset,
    value: Math.max(0, item.risk_contribution_pct),
    color: COLORS[idx % COLORS.length]
  }))

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">📊</span>
          Atribuição de Risco Detalhada
        </CardTitle>
        <CardDescription>
          Quanto cada ativo contribui para a volatilidade e VaR do portfólio
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 lg:grid-cols-4 mb-6">
          {/* Card Volatilidade do Portfólio */}
          <div className="p-4 rounded-lg border bg-blue-50 dark:bg-blue-950 border-blue-200">
            <div className="text-sm font-medium text-blue-600 dark:text-blue-400">
              Volatilidade do Portfólio
            </div>
            <div className="text-3xl font-bold text-blue-700 dark:text-blue-300">
              {portfolio_volatility.toFixed(1)}%
            </div>
            <div className="text-xs text-blue-500 mt-1">
              Anualizada
            </div>
          </div>

          {/* Card VaR 99% */}
          <div className="p-4 rounded-lg border bg-red-50 dark:bg-red-950 border-red-200">
            <div className="text-sm font-medium text-red-600 dark:text-red-400">
              VaR 99% (Paramétrico)
            </div>
            <div className="text-3xl font-bold text-red-700 dark:text-red-300">
              {portfolio_var_99.toFixed(1)}%
            </div>
            <div className="text-xs text-red-500 mt-1">
              Perda máxima esperada 99%
            </div>
          </div>

          {/* Card Top 3 Concentração */}
          <div className="p-4 rounded-lg border bg-amber-50 dark:bg-amber-950 border-amber-200">
            <div className="text-sm font-medium text-amber-600 dark:text-amber-400">
              Concentração Top 3
            </div>
            <div className="text-3xl font-bold text-amber-700 dark:text-amber-300">
              {concentration.top3_risk.toFixed(0)}%
            </div>
            <div className="text-xs text-amber-500 mt-1">
              do risco total
            </div>
          </div>

          {/* Card HHI */}
          <div className="p-4 rounded-lg border bg-purple-50 dark:bg-purple-950 border-purple-200">
            <div className="text-sm font-medium text-purple-600 dark:text-purple-400">
              Índice HHI
            </div>
            <div className="text-3xl font-bold text-purple-700 dark:text-purple-300">
              {concentration.hhi.toFixed(0)}
            </div>
            <div className="text-xs text-purple-500 mt-1">
              {concentration.hhi > 2500 ? 'Alta concentração' : concentration.hhi > 1500 ? 'Moderada' : 'Diversificado'}
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Gráfico de Barras */}
          <div className="h-[350px]">
            <h4 className="font-semibold mb-3 text-sm">Contribuição para o Risco (%)</h4>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} layout="vertical" margin={{ left: 10, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 'auto']} unit="%" />
                <YAxis type="category" dataKey="name" width={60} />
                <Tooltip 
                  formatter={(value: number) => `${value.toFixed(1)}%`}
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))'
                  }}
                />
                <Bar dataKey="Contribuição %">
                  {barData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Gráfico de Pizza */}
          <div className="h-[350px]">
            <h4 className="font-semibold mb-3 text-sm">Distribuição do Risco</h4>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value.toFixed(0)}%`}
                  labelLine={{ stroke: '#94a3b8' }}
                >
                  {pieData.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  formatter={(value: number) => `${value.toFixed(1)}%`}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Tabela Detalhada */}
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-2">Ativo</th>
                <th className="text-right py-2 px-2">Peso</th>
                <th className="text-right py-2 px-2">Vol. Individual</th>
                <th className="text-right py-2 px-2">MCR</th>
                <th className="text-right py-2 px-2">Contrib. Risco</th>
                <th className="text-right py-2 px-2">% do Total</th>
                <th className="text-right py-2 px-2">VaR Contrib.</th>
                <th className="text-right py-2 px-2">Diversif.</th>
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
                  <td className="text-right py-2 px-2">{(item.volatility ?? 0).toFixed(1)}%</td>
                  <td className="text-right py-2 px-2">{(item.marginal_contribution ?? 0).toFixed(2)}%</td>
                  <td className="text-right py-2 px-2">{(item.risk_contribution ?? 0).toFixed(2)}%</td>
                  <td className="text-right py-2 px-2 font-semibold">
                    {(item.risk_contribution_pct ?? 0).toFixed(1)}%
                  </td>
                  <td className="text-right py-2 px-2 text-red-600">{(item.var_contribution ?? 0).toFixed(2)}%</td>
                  <td className={`text-right py-2 px-2 ${(item.diversification_benefit ?? 0) > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {(item.diversification_benefit ?? 0) > 0 ? '+' : ''}{(item.diversification_benefit ?? 0).toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Legenda */}
        <div className="mt-4 p-4 bg-muted/50 rounded-lg text-xs space-y-1">
          <p><strong>MCR (Marginal Contribution to Risk):</strong> Sensibilidade do risco do portfólio a mudanças no peso do ativo.</p>
          <p><strong>Contrib. Risco:</strong> Peso × MCR - contribuição absoluta para a volatilidade total.</p>
          <p><strong>Diversif.:</strong> Benefício de diversificação - diferença entre VaR individual e contribuição real ao VaR.</p>
        </div>
      </CardContent>
    </Card>
  )
}
