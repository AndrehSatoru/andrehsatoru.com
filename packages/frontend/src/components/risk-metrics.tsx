"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { motion } from "framer-motion"
import { useRefreshAnimation } from "@/hooks/use-refresh-animation"

interface MetricRowProps {
  label: string
  value: number
  max?: number
  color?: string
  suffix?: string
  isProgress?: boolean
  valueClassName?: string
}

function MetricRow({ label, value, max, color, suffix = "", isProgress = true, valueClassName = "text-foreground" }: MetricRowProps) {
  const controls = useRefreshAnimation(value)

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-foreground">{label}</span>
        <motion.span 
          animate={controls} 
          className={`text-base font-bold inline-block px-2 py-0.5 rounded-md ${valueClassName}`}
        >
          {value.toFixed(2)}{suffix}
        </motion.span>
      </div>
      {isProgress && max && (
        <Progress value={Math.min((Math.abs(value) / max) * 100, 100)} className="h-2.5" />
      )}
    </div>
  )
}

export function RiskMetrics() {
  const { analysisResult } = useDashboardData()
  
  const desempenho = analysisResult?.desempenho || {}
  
  const maxDrawdown = desempenho["max_drawdown_%"] || 0
  const es95 = desempenho["es_95%_1d_%"] || 0
  const diasAnalisados = desempenho["dias_analisados"] || 0

  // Animation controls for the bottom section
  const drawdownControls = useRefreshAnimation(maxDrawdown)
  const esControls = useRefreshAnimation(es95)
  const diasControls = useRefreshAnimation(diasAnalisados)

  const riskMetrics = [
    { 
      label: "Volatilidade Anual", 
      value: desempenho["volatilidade_anual_%"] || 0, 
      max: 50, 
      color: "bg-primary",
      suffix: "%"
    },
    { 
      label: "Sharpe Ratio", 
      value: desempenho["indice_sharpe"] || 0, 
      max: 3, 
      color: "bg-secondary",
      suffix: ""
    },
    { 
      label: "VaR 95%", 
      value: Math.abs(desempenho["var_95%_1d_%"] || 0), 
      max: 10, 
      color: "bg-accent",
      suffix: "%"
    },
  ]

  return (
    <Card className="border-border hover:shadow-md transition-shadow">
      <CardHeader>
        <CardTitle className="text-foreground">Métricas de Risco</CardTitle>
        <CardDescription className="text-muted-foreground">Indicadores ajustados ao risco</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        {riskMetrics.map((metric) => (
          <MetricRow 
            key={metric.label}
            {...metric}
          />
        ))}

        <div className="mt-6 space-y-4 rounded-xl bg-muted p-5">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Drawdown Máximo</span>
            <motion.span animate={drawdownControls} className="text-base font-semibold text-destructive px-2 py-0.5 rounded-md inline-block">
              {maxDrawdown.toFixed(2)}%
            </motion.span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Expected Shortfall (95%)</span>
            <motion.span animate={esControls} className="text-base font-semibold text-foreground px-2 py-0.5 rounded-md inline-block">
              {es95.toFixed(2)}%
            </motion.span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Dias Analisados</span>
            <motion.span animate={diasControls} className="text-base font-semibold text-foreground px-2 py-0.5 rounded-md inline-block">
              {diasAnalisados}
            </motion.span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

