"use client"

import { TrendingUp, Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { usePeriod, type PeriodType } from "@/lib/period-context"

export function DashboardHeader() {
  const { period, setPeriod } = usePeriod()

  return (
    <header className="border-b border-border bg-card">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
              <TrendingUp className="h-5 w-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-foreground">Gestão de Portfólio</h1>
              <p className="text-sm text-muted-foreground">Análise de Risco e Rentabilidade</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Select value={period} onValueChange={(value) => setPeriod(value as PeriodType)}>
              <SelectTrigger className="w-[140px]">
                <Calendar className="mr-2 h-4 w-4" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1M">1 Mês</SelectItem>
                <SelectItem value="3M">3 Meses</SelectItem>
                <SelectItem value="6M">6 Meses</SelectItem>
                <SelectItem value="YTD">Ano Atual</SelectItem>
                <SelectItem value="1Y">1 Ano</SelectItem>
                <SelectItem value="5Y">5 Anos</SelectItem>
                <SelectItem value="ALL">Tudo</SelectItem>
              </SelectContent>
            </Select>

            <Button variant="outline">Exportar Relatório</Button>
          </div>
        </div>
      </div>
    </header>
  )
}
