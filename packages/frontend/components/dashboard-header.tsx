"use client"

import { TrendingUp, Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { usePeriod, type PeriodType } from "@/lib/period-context"

export function DashboardHeader() {
  const { period, setPeriod } = usePeriod()

  return (
    <header className="border-b border-border bg-card sticky top-0 z-50 backdrop-blur-sm bg-card/95">
      <div className="max-w-[1800px] mx-auto px-6 py-5 2xl:px-8">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary shadow-lg">
              <TrendingUp className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-foreground">Gestão de Portfólio</h1>
              <p className="text-sm text-muted-foreground">Análise de Risco e Rentabilidade</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
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
