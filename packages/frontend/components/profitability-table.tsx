"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useState } from "react"
import { RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useDashboardData } from "@/src/lib/dashboard-data-context"

interface MonthlyReturnRow {
  year: number
  jan: number | null
  fev: number | null
  mar: number | null
  abr: number | null
  mai: number | null
  jun: number | null
  jul: number | null
  ago: number | null
  set_: number | null
  out: number | null
  nov: number | null
  dez: number | null
  acumAno: number | null
  cdi: number | null
  acumFdo: number | null
  acumCdi: number | null
}

export function ProfitabilityTable() {
  const { analysisResult } = useDashboardData()
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Extrair dados de retornos mensais do analysisResult
  const monthlyData: MonthlyReturnRow[] = analysisResult?.results?.monthly_returns || []
  const startDate = analysisResult?.results?.metadados?.periodo_analise?.inicio
  const lastUpdate = new Date().toISOString().split('T')[0]

  // Debug log para verificar dados
  console.log("[ProfitabilityTable] analysisResult:", analysisResult)
  console.log("[ProfitabilityTable] monthlyData:", monthlyData)

  const formatValue = (value: number | null) => {
    if (value === null || value === undefined) return "-"
    return value.toFixed(2) + "%"
  }

  const getCellColor = (value: number | null) => {
    if (value === null || value === undefined) return ""
    if (value > 0) return "text-green-600 dark:text-green-400"
    if (value < 0) return "text-red-600 dark:text-red-400"
    return ""
  }

  const handleRefresh = () => {
    setIsRefreshing(true)
    // Simular refresh - em produção, isso poderia recarregar os dados
    setTimeout(() => setIsRefreshing(false), 500)
  }

  // Se não há dados de análise, mostrar mensagem
  if (!analysisResult || monthlyData.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-balance">Rentabilidades (%)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            <p>Nenhum dado disponível.</p>
            <p className="text-sm mt-2">Envie suas operações para ver a tabela de rentabilidades.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-balance">Rentabilidades (%)</CardTitle>
        </div>
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={handleRefresh}
          disabled={isRefreshing}
          title="Atualizar dados"
        >
          <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
        </Button>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="px-2 py-2 text-left font-medium">Ano</th>
                <th className="px-2 py-2 text-right font-medium">Jan</th>
                <th className="px-2 py-2 text-right font-medium">Fev</th>
                <th className="px-2 py-2 text-right font-medium">Mar</th>
                <th className="px-2 py-2 text-right font-medium">Abr</th>
                <th className="px-2 py-2 text-right font-medium">Mai</th>
                <th className="px-2 py-2 text-right font-medium">Jun</th>
                <th className="px-2 py-2 text-right font-medium">Jul</th>
                <th className="px-2 py-2 text-right font-medium">Ago</th>
                <th className="px-2 py-2 text-right font-medium">Set</th>
                <th className="px-2 py-2 text-right font-medium">Out</th>
                <th className="px-2 py-2 text-right font-medium">Nov</th>
                <th className="px-2 py-2 text-right font-medium">Dez</th>
                <th className="px-2 py-2 text-right font-medium bg-muted">Acum. Ano</th>
                <th className="px-2 py-2 text-right font-medium bg-muted">CDI</th>
                <th className="px-2 py-2 text-right font-medium bg-muted">Acum. Fdo.</th>
                <th className="px-2 py-2 text-right font-medium bg-muted">Acum. CDI*</th>
              </tr>
            </thead>
            <tbody>
              {monthlyData.map((row) => (
                <tr key={row.year} className="border-b hover:bg-muted/50">
                  <td className="px-2 py-2 font-medium">{row.year}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.jan)}`}>{formatValue(row.jan)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.fev)}`}>{formatValue(row.fev)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.mar)}`}>{formatValue(row.mar)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.abr)}`}>{formatValue(row.abr)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.mai)}`}>{formatValue(row.mai)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.jun)}`}>{formatValue(row.jun)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.jul)}`}>{formatValue(row.jul)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.ago)}`}>{formatValue(row.ago)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.set_)}`}>{formatValue(row.set_)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.out)}`}>{formatValue(row.out)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.nov)}`}>{formatValue(row.nov)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.dez)}`}>{formatValue(row.dez)}</td>
                  <td className={`px-2 py-2 text-right font-medium bg-muted ${getCellColor(row.acumAno)}`}>
                    {formatValue(row.acumAno)}
                  </td>
                  <td className={`px-2 py-2 text-right bg-muted ${getCellColor(row.cdi)}`}>{formatValue(row.cdi)}</td>
                  <td className={`px-2 py-2 text-right font-medium bg-muted ${getCellColor(row.acumFdo)}`}>
                    {formatValue(row.acumFdo)}
                  </td>
                  <td className={`px-2 py-2 text-right bg-muted ${getCellColor(row.acumCdi)}`}>
                    {formatValue(row.acumCdi)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-muted-foreground mt-4">
          * Calculado desde a constituição do fundo • Última atualização: {lastUpdate}
        </p>
      </CardContent>
    </Card>
  )
}
