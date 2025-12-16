"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Cell, ZAxis } from "recharts"

// Cores baseadas no Alpha
const getAlphaColor = (alpha: number) => {
  if (alpha > 10) return '#22c55e' // Verde forte - excelente
  if (alpha > 5) return '#84cc16' // Verde claro - bom
  if (alpha > 0) return '#facc15' // Amarelo - neutro positivo
  if (alpha > -5) return '#fb923c' // Laranja - underperformance leve
  return '#ef4444' // Vermelho - underperformance significativa
}

const getBetaInterpretation = (beta: number) => {
  if (beta > 1.3) return { text: 'Muito Agressivo', color: 'text-red-600' }
  if (beta > 1.1) return { text: 'Agressivo', color: 'text-orange-500' }
  if (beta > 0.9) return { text: 'Neutro', color: 'text-blue-600' }
  if (beta > 0.7) return { text: 'Defensivo', color: 'text-green-500' }
  return { text: 'Muito Defensivo', color: 'text-green-600' }
}

export function CAPMAnalysis() {
  const { analysisResult } = useDashboardData()

  const capmData = useMemo(() => {
    if (!analysisResult?.capm_analysis) {
      return null
    }

    const data = analysisResult.capm_analysis

    if (data.error || !data.items || data.items.length === 0) {
      return null
    }

    return data
  }, [analysisResult])

  if (!capmData) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-2xl">📈</span>
            Análise CAPM
          </CardTitle>
          <CardDescription>
            Alpha, Beta e performance ajustada ao risco
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
            Dados insuficientes para análise CAPM
          </div>
        </CardContent>
      </Card>
    )
  }

  const { items, portfolio_metrics, benchmark, risk_free_rate } = capmData

  // Preparar dados para o scatter chart (Beta vs Alpha)
  const scatterData = items.map((item: any) => ({
    name: item.asset,
    beta: item.beta,
    alpha: item.alpha,
    sharpe: item.sharpe,
    weight: item.weight,
    r_squared: item.r_squared
  }))

  // Security Market Line (SML)
  // E(R) = Rf + β × (E(Rm) - Rf)
  // Assumindo prêmio de risco de ~8% (mercado brasileiro)
  const marketPremium = 8
  const smlData = [
    { beta: 0, expectedReturn: risk_free_rate },
    { beta: 2, expectedReturn: risk_free_rate + 2 * marketPremium }
  ]

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">📈</span>
          Análise CAPM (Capital Asset Pricing Model)
        </CardTitle>
        <CardDescription>
          Performance ajustada ao risco vs {benchmark} • Taxa livre de risco: {risk_free_rate}% a.a.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 lg:grid-cols-4 mb-6">
          {/* Card Beta do Portfólio */}
          <div className="p-4 rounded-lg border bg-blue-50 dark:bg-blue-950 border-blue-200">
            <div className="text-sm font-medium text-blue-600 dark:text-blue-400">
              Beta do Portfólio
            </div>
            <div className="text-3xl font-bold text-blue-700 dark:text-blue-300">
              {portfolio_metrics.beta.toFixed(2)}
            </div>
            <div className={`text-xs mt-1 ${getBetaInterpretation(portfolio_metrics.beta).color}`}>
              {getBetaInterpretation(portfolio_metrics.beta).text}
            </div>
          </div>

          {/* Card Alpha do Portfólio */}
          <div className={`p-4 rounded-lg border ${
            portfolio_metrics.alpha > 0 
              ? 'bg-green-50 dark:bg-green-950 border-green-200' 
              : 'bg-red-50 dark:bg-red-950 border-red-200'
          }`}>
            <div className={`text-sm font-medium ${
              portfolio_metrics.alpha > 0 
                ? 'text-green-600 dark:text-green-400' 
                : 'text-red-600 dark:text-red-400'
            }`}>
              Alpha do Portfólio
            </div>
            <div className={`text-3xl font-bold ${
              portfolio_metrics.alpha > 0 
                ? 'text-green-700 dark:text-green-300' 
                : 'text-red-700 dark:text-red-300'
            }`}>
              {portfolio_metrics.alpha > 0 ? '+' : ''}{portfolio_metrics.alpha.toFixed(2)}%
            </div>
            <div className="text-xs mt-1 text-muted-foreground">
              {portfolio_metrics.alpha > 0 ? 'Superando o esperado' : 'Abaixo do esperado'}
            </div>
          </div>

          {/* Card Benchmark */}
          <div className="p-4 rounded-lg border bg-slate-50 dark:bg-slate-950 border-slate-200">
            <div className="text-sm font-medium text-slate-600 dark:text-slate-400">
              Benchmark
            </div>
            <div className="text-2xl font-bold text-slate-700 dark:text-slate-300">
              {benchmark}
            </div>
            <div className="text-xs mt-1 text-muted-foreground">
              Índice de referência
            </div>
          </div>

          {/* Card Taxa Livre de Risco */}
          <div className="p-4 rounded-lg border bg-slate-50 dark:bg-slate-950 border-slate-200">
            <div className="text-sm font-medium text-slate-600 dark:text-slate-400">
              Taxa Livre de Risco
            </div>
            <div className="text-2xl font-bold text-slate-700 dark:text-slate-300">
              {risk_free_rate.toFixed(1)}%
            </div>
            <div className="text-xs mt-1 text-muted-foreground">
              CDI anualizado
            </div>
          </div>
        </div>

        {/* Scatter Chart: Beta vs Alpha */}
        <div className="h-[400px]">
          <h4 className="font-semibold mb-3 text-sm">Beta vs Alpha (tamanho = peso no portfólio)</h4>
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                type="number" 
                dataKey="beta" 
                name="Beta" 
                domain={[0, 'auto']}
                label={{ value: 'Beta (Risco Sistemático)', position: 'bottom', offset: 0 }}
              />
              <YAxis 
                type="number" 
                dataKey="alpha" 
                name="Alpha" 
                unit="%"
                domain={['auto', 'auto']}
                label={{ value: 'Alpha (% a.a.)', angle: -90, position: 'insideLeft' }}
              />
              <ZAxis type="number" dataKey="weight" range={[100, 500]} />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                content={({ payload }) => {
                  if (!payload || payload.length === 0) return null
                  const data = payload[0].payload
                  return (
                    <div className="bg-card border rounded-lg p-3 shadow-lg">
                      <p className="font-semibold text-lg">{data.name}</p>
                      <div className="grid grid-cols-2 gap-x-4 gap-y-1 mt-2 text-sm">
                        <span className="text-muted-foreground">Beta:</span>
                        <span className="font-medium">{data.beta?.toFixed(2)}</span>
                        <span className="text-muted-foreground">Alpha:</span>
                        <span className={`font-medium ${data.alpha > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {data.alpha > 0 ? '+' : ''}{data.alpha?.toFixed(2)}%
                        </span>
                        <span className="text-muted-foreground">Sharpe:</span>
                        <span className="font-medium">{data.sharpe?.toFixed(2)}</span>
                        <span className="text-muted-foreground">R²:</span>
                        <span className="font-medium">{(data.r_squared * 100)?.toFixed(1)}%</span>
                        <span className="text-muted-foreground">Peso:</span>
                        <span className="font-medium">{data.weight?.toFixed(1)}%</span>
                      </div>
                    </div>
                  )
                }}
              />
              
              {/* Linha de referência (Alpha = 0) */}
              <ReferenceLine y={0} stroke="#94a3b8" strokeDasharray="3 3" label={{ value: 'Alpha = 0', position: 'right' }} />
              <ReferenceLine x={1} stroke="#94a3b8" strokeDasharray="3 3" label={{ value: 'β = 1', position: 'top' }} />
              
              {/* Scatter de ativos */}
              <Scatter name="Ativos" data={scatterData}>
                {scatterData.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={getAlphaColor(entry.alpha)} />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Tabela de Ativos */}
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-2">Ativo</th>
                <th className="text-right py-2 px-2">Peso</th>
                <th className="text-right py-2 px-2">Beta</th>
                <th className="text-right py-2 px-2">Alpha (a.a.)</th>
                <th className="text-right py-2 px-2">Sharpe</th>
                <th className="text-right py-2 px-2">Treynor</th>
                <th className="text-right py-2 px-2">R²</th>
                <th className="text-right py-2 px-2">Retorno</th>
                <th className="text-right py-2 px-2">Volatilidade</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item: any) => (
                <tr key={item.asset} className="border-b hover:bg-muted/50">
                  <td className="py-2 px-2 font-medium">{item.asset}</td>
                  <td className="text-right py-2 px-2">{(item.weight ?? 0).toFixed(1)}%</td>
                  <td className={`text-right py-2 px-2 ${getBetaInterpretation(item.beta ?? 1).color}`}>
                    {(item.beta ?? 0).toFixed(2)}
                  </td>
                  <td className={`text-right py-2 px-2 font-semibold ${(item.alpha ?? 0) > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {(item.alpha ?? 0) > 0 ? '+' : ''}{(item.alpha ?? 0).toFixed(2)}%
                  </td>
                  <td className="text-right py-2 px-2">{(item.sharpe ?? 0).toFixed(2)}</td>
                  <td className="text-right py-2 px-2">{(item.treynor ?? 0).toFixed(2)}%</td>
                  <td className="text-right py-2 px-2">{((item.r_squared ?? 0) * 100).toFixed(1)}%</td>
                  <td className={`text-right py-2 px-2 ${(item.annualized_return ?? 0) > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {(item.annualized_return ?? 0).toFixed(1)}%
                  </td>
                  <td className="text-right py-2 px-2">{(item.annualized_volatility ?? 0).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Legenda */}
        <div className="mt-4 p-4 bg-muted/50 rounded-lg text-xs space-y-1">
          <p><strong>Alpha (α):</strong> Retorno excedente ajustado ao risco. Positivo = superou o esperado pelo CAPM.</p>
          <p><strong>Beta (β):</strong> Sensibilidade ao mercado. β=1 move igual ao mercado, β&gt;1 mais volátil, β&lt;1 mais defensivo.</p>
          <p><strong>Sharpe:</strong> (Retorno - Rf) / Volatilidade. Quanto maior, melhor o retorno ajustado ao risco total.</p>
          <p><strong>Treynor:</strong> (Retorno - Rf) / Beta. Quanto maior, melhor o retorno ajustado ao risco sistemático.</p>
          <p><strong>R²:</strong> Proporção da variância explicada pelo mercado. Alto R² indica alta correlação com o benchmark.</p>
        </div>
      </CardContent>
    </Card>
  )
}
