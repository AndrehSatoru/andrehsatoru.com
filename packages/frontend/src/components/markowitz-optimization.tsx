"use client"

import { useMemo, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts"

const portfolioColors = {
  'Máximo Sharpe': '#22c55e',
  'Mínima Volatilidade': '#3b82f6',
  'Máximo Retorno': '#f59e0b',
  'Portfólio Atual': '#ef4444'
}

export function MarkowitzOptimization() {
  const { analysisResult } = useDashboardData()
  const [selectedPortfolio, setSelectedPortfolio] = useState<string | null>(null)

  const optimizationData = useMemo(() => {
    if (!analysisResult?.markowitz_optimization) {
      return null
    }

    const data = analysisResult.markowitz_optimization

    if (data.error || !data.optimal_portfolios) {
      return null
    }

    return data
  }, [analysisResult])

  if (!optimizationData) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-2xl">🎯</span>
            Otimização de Portfólio
          </CardTitle>
          <CardDescription>
            Sugestões de alocação ótima (Markowitz)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
            Dados insuficientes para otimização
          </div>
        </CardContent>
      </Card>
    )
  }

  const { current_portfolio, optimal_portfolios, frontier, risk_free_rate } = optimizationData

  // Preparar dados para o scatter chart
  const scatterData = [
    {
      name: current_portfolio.name,
      volatility: current_portfolio.volatility,
      return: current_portfolio.expected_return,
      sharpe: current_portfolio.sharpe_ratio,
      type: 'current'
    },
    ...optimal_portfolios.map((p: any) => ({
      name: p.name,
      volatility: p.volatility,
      return: p.expected_return,
      sharpe: p.sharpe_ratio,
      type: 'optimal'
    }))
  ]

  // Fronteira eficiente
  const frontierData = frontier?.map((p: any) => ({
    volatility: p.volatility,
    return: p.return,
    type: 'frontier'
  })) || []

  const selected = selectedPortfolio 
    ? (selectedPortfolio === 'Portfólio Atual' ? current_portfolio : optimal_portfolios.find((p: any) => p.name === selectedPortfolio))
    : null

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">🎯</span>
          Otimização de Portfólio (Markowitz)
        </CardTitle>
        <CardDescription>
          Compare seu portfólio atual com alocações ótimas • Taxa livre de risco: {risk_free_rate}%
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 lg:grid-cols-4">
          {/* Card Portfólio Atual */}
          <div 
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
              selectedPortfolio === 'Portfólio Atual' 
                ? 'border-red-500 bg-red-50 dark:bg-red-950' 
                : 'border-red-200 hover:border-red-300'
            }`}
            onClick={() => setSelectedPortfolio('Portfólio Atual')}
          >
            <div className="flex items-center gap-2 mb-2">
              <div className="w-3 h-3 rounded-full bg-red-500"></div>
              <span className="font-semibold text-sm">Portfólio Atual</span>
            </div>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Retorno:</span>
                <span className="font-medium">{(current_portfolio?.expected_return ?? 0).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Volatilidade:</span>
                <span className="font-medium">{(current_portfolio?.volatility ?? 0).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Sharpe:</span>
                <span className="font-medium">{(current_portfolio?.sharpe_ratio ?? 0).toFixed(2)}</span>
              </div>
            </div>
          </div>

          {/* Cards Portfólios Ótimos */}
          {optimal_portfolios.map((p: any, idx: number) => {
            const color = portfolioColors[p.name as keyof typeof portfolioColors] || '#6b7280'
            const isSelected = selectedPortfolio === p.name
            const improvement = (p.sharpe_ratio ?? 0) - (current_portfolio?.sharpe_ratio ?? 0)
            
            return (
              <div 
                key={p.name}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  isSelected 
                    ? `border-current bg-opacity-10` 
                    : 'border-slate-200 hover:border-slate-300'
                }`}
                style={{ borderColor: isSelected ? color : undefined, backgroundColor: isSelected ? `${color}10` : undefined }}
                onClick={() => setSelectedPortfolio(p.name)}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }}></div>
                  <span className="font-semibold text-sm">{p.name}</span>
                </div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Retorno:</span>
                    <span className="font-medium">{(p.expected_return ?? 0).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Volatilidade:</span>
                    <span className="font-medium">{(p.volatility ?? 0).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Sharpe:</span>
                    <span className="font-medium">{(p.sharpe_ratio ?? 0).toFixed(2)}</span>
                  </div>
                  {improvement > 0 && (
                    <div className="mt-2 text-xs text-green-600 font-medium">
                      +{(improvement * 100).toFixed(0)}% Sharpe vs atual
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Gráfico Scatter */}
        <div className="h-[350px] mt-6">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                type="number" 
                dataKey="volatility" 
                name="Volatilidade" 
                unit="%" 
                domain={['auto', 'auto']}
                label={{ value: 'Volatilidade (%)', position: 'bottom', offset: 0 }}
              />
              <YAxis 
                type="number" 
                dataKey="return" 
                name="Retorno" 
                unit="%"
                domain={['auto', 'auto']}
                label={{ value: 'Retorno Esperado (%)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                content={({ payload }) => {
                  if (!payload || payload.length === 0) return null
                  const data = payload[0].payload
                  return (
                    <div className="bg-card border rounded-lg p-3 shadow-lg">
                      <p className="font-semibold">{data.name || 'Fronteira'}</p>
                      <p className="text-sm">Retorno: {data.return?.toFixed(1)}%</p>
                      <p className="text-sm">Volatilidade: {data.volatility?.toFixed(1)}%</p>
                      {data.sharpe && <p className="text-sm">Sharpe: {data.sharpe?.toFixed(2)}</p>}
                    </div>
                  )
                }}
              />
              
              {/* Fronteira eficiente */}
              <Scatter 
                name="Fronteira Eficiente" 
                data={frontierData} 
                fill="#94a3b8" 
                line={{ stroke: '#94a3b8', strokeWidth: 2 }}
                shape="circle"
                legendType="none"
              />
              
              {/* Portfólios */}
              {scatterData.map((point, idx) => {
                const color = portfolioColors[point.name as keyof typeof portfolioColors] || '#6b7280'
                return (
                  <Scatter 
                    key={point.name}
                    name={point.name} 
                    data={[point]} 
                    fill={color}
                  >
                  </Scatter>
                )
              })}
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Detalhes do portfólio selecionado */}
        {selected && (
          <div className="mt-6 p-4 bg-muted/50 rounded-lg">
            <h4 className="font-semibold mb-3">
              Pesos sugeridos: {selected.name}
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
              {Object.entries(selected.weights || {}).map(([asset, weight]) => (
                <div key={asset} className="flex justify-between items-center p-2 bg-background rounded border">
                  <span className="font-medium text-sm">{asset}</span>
                  <span className="text-sm text-muted-foreground">{((weight as number) ?? 0).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Legenda explicativa */}
        <div className="mt-4 p-4 bg-muted/50 rounded-lg text-xs space-y-1">
          <p><strong>Fronteira Eficiente:</strong> Curva de portfólios que oferecem o maior retorno para cada nível de risco (ou menor risco para cada retorno).</p>
          <p><strong>Máximo Sharpe:</strong> Portfólio que maximiza a relação retorno/risco. Melhor trade-off entre risco e retorno.</p>
          <p><strong>Mínima Volatilidade:</strong> Portfólio com menor risco possível. Ideal para perfis conservadores.</p>
          <p><strong>Máximo Retorno:</strong> Portfólio com maior retorno esperado. Concentrado em poucos ativos de alto desempenho.</p>
          <p><strong>Índice Sharpe:</strong> (Retorno - Rf) / Volatilidade. Quanto maior, melhor o retorno ajustado ao risco.</p>
        </div>
      </CardContent>
    </Card>
  )
}

