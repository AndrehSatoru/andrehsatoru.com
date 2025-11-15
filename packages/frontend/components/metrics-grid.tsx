import { Card, CardContent } from "@/components/ui/card"
import { ArrowUpRight, ArrowDownRight, TrendingUp, Shield, Activity, Target } from "lucide-react"

const metrics = [
  {
    label: "Retorno Total",
    value: "R$ 2.847.392",
    change: "+12.4%",
    trend: "up",
    icon: TrendingUp,
    color: "text-success",
  },
  {
    label: "Sharpe Ratio",
    value: "1.85",
    change: "+0.12",
    trend: "up",
    icon: Target,
    color: "text-primary",
  },
  {
    label: "Volatilidade",
    value: "8.3%",
    change: "-0.5%",
    trend: "down",
    icon: Activity,
    color: "text-secondary",
  },
  {
    label: "VaR (95%)",
    value: "R$ 142.850",
    change: "+2.1%",
    trend: "up",
    icon: Shield,
    color: "text-accent",
  },
]

export function MetricsGrid() {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {metrics.map((metric) => {
        const Icon = metric.icon
        const isPositive = metric.trend === "up"

        return (
          <Card key={metric.label} className="border-border">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <p className="text-sm font-medium text-muted-foreground">{metric.label}</p>
                  <p className="text-2xl font-bold tracking-tight text-foreground">{metric.value}</p>
                  <div className="flex items-center gap-1">
                    {isPositive ? (
                      <ArrowUpRight className="h-4 w-4 text-success" />
                    ) : (
                      <ArrowDownRight className="h-4 w-4 text-success" />
                    )}
                    <span className={`text-sm font-medium ${isPositive ? "text-success" : "text-success"}`}>
                      {metric.change}
                    </span>
                    <span className="text-xs text-muted-foreground">vs mês anterior</span>
                  </div>
                </div>
                <div className={`rounded-lg bg-muted p-2.5 ${metric.color}`}>
                  <Icon className="h-5 w-5" />
                </div>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
