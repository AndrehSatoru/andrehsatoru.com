"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Area,
  AreaChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
} from "recharts"
import { usePeriod, filterDataByPeriod } from "@/lib/period-context"

const allData = [
  { date: "2024-07-01", drawdown: 0 },
  { date: "2024-07-05", drawdown: -0.3 },
  { date: "2024-07-10", drawdown: -0.5 },
  { date: "2024-07-15", drawdown: -0.8 },
  { date: "2024-07-20", drawdown: -1.2 },
  { date: "2024-07-25", drawdown: -0.9 },
  { date: "2024-07-31", drawdown: -0.6 },
  { date: "2024-08-05", drawdown: -1.1 },
  { date: "2024-08-10", drawdown: -1.5 },
  { date: "2024-08-15", drawdown: -1.8 },
  { date: "2024-08-20", drawdown: -2.2 },
  { date: "2024-08-25", drawdown: -2.5 },
  { date: "2024-08-31", drawdown: -2.1 },
  { date: "2024-09-05", drawdown: -1.7 },
  { date: "2024-09-10", drawdown: -2.3 },
  { date: "2024-09-15", drawdown: -2.8 },
  { date: "2024-09-20", drawdown: -3.2 },
  { date: "2024-09-25", drawdown: -3.6 },
  { date: "2024-09-30", drawdown: -4.2 },
  { date: "2024-10-05", drawdown: -4.8 },
  { date: "2024-10-10", drawdown: -5.2 },
  { date: "2024-10-15", drawdown: -4.7 },
  { date: "2024-10-20", drawdown: -4.2 },
  { date: "2024-10-25", drawdown: -3.8 },
  { date: "2024-10-31", drawdown: -3.5 },
  { date: "2024-11-05", drawdown: -3.1 },
  { date: "2024-11-10", drawdown: -2.7 },
  { date: "2024-11-15", drawdown: -2.3 },
  { date: "2024-11-20", drawdown: -1.9 },
  { date: "2024-11-25", drawdown: -1.5 },
  { date: "2024-11-30", drawdown: -1.2 },
  { date: "2024-12-05", drawdown: -0.9 },
  { date: "2024-12-10", drawdown: -1.3 },
  { date: "2024-12-15", drawdown: -1.7 },
  { date: "2024-12-20", drawdown: -2.1 },
  { date: "2024-12-25", drawdown: -1.8 },
  { date: "2024-12-31", drawdown: -1.4 },
  { date: "2025-01-05", drawdown: -1.0 },
  { date: "2025-01-10", drawdown: -0.7 },
  { date: "2025-01-15", drawdown: -0.4 },
  { date: "2025-01-20", drawdown: -0.2 },
  { date: "2025-01-25", drawdown: -0.1 },
  { date: "2025-01-31", drawdown: 0 },
]

export function DrawdownChart() {
  const { period } = usePeriod()
  const data = filterDataByPeriod(allData, period)

  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Drawdown</CardTitle>
        <CardDescription className="text-muted-foreground">Queda acumulada do pico (%)</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={250}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--destructive))" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(var(--destructive))" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              dataKey="date"
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear().toString().slice(2)}`
              }}
            />
            <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
                color: "hsl(var(--foreground))",
              }}
              labelFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleDateString("pt-BR")
              }}
              formatter={(value: number) => [`${value}%`, "Drawdown"]}
            />
            <ReferenceLine y={0} stroke="hsl(var(--muted-foreground))" strokeDasharray="3 3" />
            <Area
              type="monotone"
              dataKey="drawdown"
              stroke="hsl(var(--destructive))"
              strokeWidth={2}
              fill="url(#drawdownGradient)"
            />
            <Brush
              dataKey="date"
              height={50}
              stroke="hsl(var(--destructive))"
              fill="hsl(var(--background))"
              fillOpacity={0.3}
              travellerWidth={12}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear().toString().slice(2)}`
              }}
            >
              <AreaChart data={data}>
                <Area
                  type="monotone"
                  dataKey="drawdown"
                  stroke="hsl(var(--destructive))"
                  fill="hsl(var(--destructive))"
                  fillOpacity={0.2}
                  strokeWidth={1}
                />
              </AreaChart>
            </Brush>
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
