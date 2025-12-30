"use client"

import { TrendingUp, Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { usePeriod } from "@/lib/period-context"

export function DashboardHeader() {
  const { period, setPeriod } = usePeriod()

  return (
    <div className="fixed top-6 left-1/2 -translate-x-1/2 z-50 w-full max-w-fit pointer-events-none">
      <header className="pointer-events-auto bg-background/80 backdrop-blur-xl border border-border/40 shadow-lg rounded-full px-6 py-3 flex items-center gap-6 transition-all hover:shadow-xl hover:-translate-y-0.5">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary shadow-md">
            <TrendingUp className="h-5 w-5 text-primary-foreground" />
          </div>
          <div className="hidden md:block">
            <h1 className="text-sm font-bold tracking-tight text-foreground">Gestão de Portfólio</h1>
          </div>
        </div>

        <div className="h-8 w-px bg-border/50 hidden md:block" />

        <div className="flex items-center gap-3">
          <Select value={period} onValueChange={(value) => setPeriod(value)}>
            <SelectTrigger className="w-[130px] rounded-full border-0 bg-secondary/50 focus:ring-0 shadow-none hover:bg-secondary">
              <Calendar className="mr-2 h-4 w-4 opacity-70" />
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

          <Button variant="ghost" size="sm" className="rounded-full hover:bg-secondary/80">
            Exportar
          </Button>
        </div>
      </header>
    </div>
  )
}

