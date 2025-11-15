import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

const riskMetrics = [
  { label: "Beta", value: 0.92, max: 2, color: "bg-primary" },
  { label: "Alpha", value: 1.8, max: 3, color: "bg-secondary" },
  { label: "Correlação", value: 0.75, max: 1, color: "bg-accent" },
]

export function RiskMetrics() {
  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Métricas de Risco</CardTitle>
        <CardDescription className="text-muted-foreground">Indicadores ajustados ao risco</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {riskMetrics.map((metric) => (
          <div key={metric.label} className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-foreground">{metric.label}</span>
              <span className="text-sm font-bold text-foreground">{metric.value.toFixed(2)}</span>
            </div>
            <Progress value={(metric.value / metric.max) * 100} className="h-2" />
          </div>
        ))}

        <div className="mt-6 space-y-3 rounded-lg bg-muted p-4">
          <div className="flex justify-between">
            <span className="text-sm text-muted-foreground">Drawdown Máximo</span>
            <span className="text-sm font-semibold text-destructive">-5.2%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-muted-foreground">Sortino Ratio</span>
            <span className="text-sm font-semibold text-foreground">2.14</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-muted-foreground">Information Ratio</span>
            <span className="text-sm font-semibold text-foreground">1.67</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
