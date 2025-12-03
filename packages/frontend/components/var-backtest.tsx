"use client"

import { useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, ComposedChart, Line, Scatter } from "recharts"

const getZoneColor = (zone: string) => {
  switch (zone) {
    case 'green': return { bg: 'bg-green-100 dark:bg-green-950', border: 'border-green-500', text: 'text-green-700 dark:text-green-300' }
    case 'yellow': return { bg: 'bg-yellow-100 dark:bg-yellow-950', border: 'border-yellow-500', text: 'text-yellow-700 dark:text-yellow-300' }
    case 'red': return { bg: 'bg-red-100 dark:bg-red-950', border: 'border-red-500', text: 'text-red-700 dark:text-red-300' }
    default: return { bg: 'bg-slate-100', border: 'border-slate-500', text: 'text-slate-700' }
  }
}

const getZoneEmoji = (zone: string) => {
  switch (zone) {
    case 'green': return '✅'
    case 'yellow': return '⚠️'
    case 'red': return '🔴'
    default: return '❓'
  }
}

export function VarBacktest() {
  const { analysisResult } = useDashboardData()

  const backtestData = useMemo(() => {
    if (!analysisResult?.results?.var_backtest) {
      return null
    }

    const data = analysisResult.results.var_backtest

    if (data.error || !data.summary) {
      return null
    }

    return data
  }, [analysisResult])

  if (!backtestData) {
    return (
      <Card className="col-span-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="text-2xl">🧪</span>
            Backtest do VaR
          </CardTitle>
          <CardDescription>
            Validação do modelo de risco
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-[200px] text-muted-foreground">
            Histórico insuficiente para backtest (mínimo 100 dias)
          </div>
        </CardContent>
      </Card>
    )
  }

  const { summary, basel, exceptions, var_series } = backtestData
  const zoneColors = getZoneColor(basel.zone)

  // Preparar dados do gráfico
  const chartData = var_series?.map((item: any) => ({
    date: item.date,
    var: item.var,
    return: item.return,
    exception: item.exception
  })) || []

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="text-2xl">🧪</span>
          Backtest do VaR (Value at Risk)
        </CardTitle>
        <CardDescription>
          Validação histórica do modelo de risco - VaR {summary.confidence_level}%
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 lg:grid-cols-4 mb-6">
          {/* Card Zona Basel */}
          <div className={`p-4 rounded-lg border-2 ${zoneColors.bg} ${zoneColors.border}`}>
            <div className="text-sm font-medium text-muted-foreground">Zona Basel</div>
            <div className={`text-3xl font-bold ${zoneColors.text} flex items-center gap-2`}>
              {getZoneEmoji(basel.zone)}
              {basel.zone.toUpperCase()}
            </div>
            <div className="text-xs mt-1">{basel.description}</div>
          </div>

          {/* Card Exceções */}
          <div className="p-4 rounded-lg border bg-card">
            <div className="text-sm font-medium text-muted-foreground">Exceções</div>
            <div className="text-3xl font-bold">
              {summary.n_exceptions}
              <span className="text-lg text-muted-foreground"> / {summary.n_observations}</span>
            </div>
            <div className="text-xs mt-1">
              {summary.exception_rate.toFixed(2)}% (esperado: {summary.expected_rate.toFixed(2)}%)
            </div>
          </div>

          {/* Card Teste Kupiec */}
          <div className="p-4 rounded-lg border bg-card">
            <div className="text-sm font-medium text-muted-foreground">Teste Kupiec (LR)</div>
            <div className={`text-3xl font-bold ${summary.kupiec_pass ? 'text-green-600' : 'text-red-600'}`}>
              {summary.kupiec_lr.toFixed(2)}
            </div>
            <div className="text-xs mt-1">
              Crítico: {summary.kupiec_critical} • {summary.kupiec_pass ? 'Aprovado ✓' : 'Reprovado ✗'}
            </div>
          </div>

          {/* Card Confiança */}
          <div className="p-4 rounded-lg border bg-card">
            <div className="text-sm font-medium text-muted-foreground">Nível de Confiança</div>
            <div className="text-3xl font-bold text-blue-600">
              {summary.confidence_level}%
            </div>
            <div className="text-xs mt-1">
              Janela de cálculo: 252 dias
            </div>
          </div>
        </div>

        {/* Gráfico VaR vs Retornos */}
        <div className="h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(date) => {
                  const d = new Date(date)
                  return d.toLocaleDateString("pt-BR", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric"
                  })
                }}
              />
              <YAxis 
                domain={['auto', 'auto']}
                tickFormatter={(value) => `${value.toFixed(1)}%`}
              />
              <Tooltip 
                content={({ payload, label }) => {
                  if (!payload || payload.length === 0 || !label) return null
                  const data = payload[0].payload
                  const date = new Date(label)
                  const formattedDate = date.toLocaleDateString("pt-BR", {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric"
                  })
                  return (
                    <div className="bg-card border rounded-lg p-3 shadow-lg">
                      <p className="font-semibold">{formattedDate}</p>
                      <p className="text-sm text-red-600">VaR 99%: {data.var?.toFixed(2)}%</p>
                      <p className={`text-sm ${data.return < data.var ? 'text-red-600 font-bold' : 'text-blue-600'}`}>
                        Retorno: {data.return?.toFixed(2)}%
                      </p>
                      {data.exception && <p className="text-xs text-red-500 font-bold mt-1">⚠️ EXCEÇÃO</p>}
                    </div>
                  )
                }}
              />
              
              {/* Área do VaR */}
              <Area 
                type="monotone" 
                dataKey="var" 
                stroke="#ef4444" 
                fill="#fee2e2" 
                fillOpacity={0.3}
                name="VaR 99%"
              />
              
              {/* Linha de retornos */}
              <Line 
                type="monotone" 
                dataKey="return" 
                stroke="#3b82f6" 
                dot={false}
                name="Retorno"
              />
              
              {/* Pontos de exceção */}
              <Scatter 
                dataKey="return"
                data={chartData.filter((d: any) => d.exception)}
                fill="#ef4444"
                shape="circle"
              />
              
              <ReferenceLine y={0} stroke="#94a3b8" strokeDasharray="3 3" />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Lista de Exceções Recentes */}
        {exceptions && exceptions.length > 0 && (
          <div className="mt-6">
            <h4 className="font-semibold mb-3 text-red-600">
              Últimas Exceções ({exceptions.length})
            </h4>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-2">Data</th>
                    <th className="text-right py-2 px-2">VaR 99%</th>
                    <th className="text-right py-2 px-2">Retorno Real</th>
                    <th className="text-right py-2 px-2">Violação</th>
                  </tr>
                </thead>
                <tbody>
                  {exceptions.map((exc: any, idx: number) => (
                    <tr key={idx} className="border-b bg-red-50 dark:bg-red-950/30">
                      <td className="py-2 px-2">{exc.date}</td>
                      <td className="text-right py-2 px-2 text-red-600">{(exc.var ?? 0).toFixed(2)}%</td>
                      <td className="text-right py-2 px-2 font-semibold text-red-700">{(exc.actual_return ?? 0).toFixed(2)}%</td>
                      <td className="text-right py-2 px-2 text-red-600">{(exc.breach ?? 0).toFixed(2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Legenda */}
        <div className="mt-4 p-4 bg-muted/50 rounded-lg text-xs space-y-1">
          <p><strong>Zona Verde (0-4 exceções/ano):</strong> Modelo bem calibrado, usar normalmente.</p>
          <p><strong>Zona Amarela (5-9 exceções/ano):</strong> Modelo pode subestimar risco, considerar ajustes.</p>
          <p><strong>Zona Vermelha (10+ exceções/ano):</strong> Modelo inadequado, revisão necessária.</p>
        </div>
      </CardContent>
    </Card>
  )
}
