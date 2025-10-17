"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, Brush } from "recharts"
import { usePeriod, filterDataByPeriod } from "@/lib/period-context"

const allData = [
  { date: "2024-07-01", portfolio: 1000000, benchmark: 1000000 },
  { date: "2024-07-05", portfolio: 1012000, benchmark: 1008000 },
  { date: "2024-07-10", portfolio: 1025000, benchmark: 1015000 },
  { date: "2024-07-15", portfolio: 1038000, benchmark: 1023000 },
  { date: "2024-07-20", portfolio: 1045000, benchmark: 1030000 },
  { date: "2024-07-25", portfolio: 1052000, benchmark: 1037000 },
  { date: "2024-07-31", portfolio: 1065000, benchmark: 1045000 },
  { date: "2024-08-05", portfolio: 1078000, benchmark: 1052000 },
  { date: "2024-08-10", portfolio: 1092000, benchmark: 1060000 },
  { date: "2024-08-15", portfolio: 1105000, benchmark: 1068000 },
  { date: "2024-08-20", portfolio: 1118000, benchmark: 1075000 },
  { date: "2024-08-25", portfolio: 1132000, benchmark: 1083000 },
  { date: "2024-08-31", portfolio: 1145000, benchmark: 1090000 },
  { date: "2024-09-05", portfolio: 1159000, benchmark: 1098000 },
  { date: "2024-09-10", portfolio: 1173000, benchmark: 1105000 },
  { date: "2024-09-15", portfolio: 1187000, benchmark: 1113000 },
  { date: "2024-09-20", portfolio: 1201000, benchmark: 1120000 },
  { date: "2024-09-25", portfolio: 1215000, benchmark: 1128000 },
  { date: "2024-09-30", portfolio: 1230000, benchmark: 1135000 },
  { date: "2024-10-05", portfolio: 1245000, benchmark: 1143000 },
  { date: "2024-10-10", portfolio: 1260000, benchmark: 1150000 },
  { date: "2024-10-15", portfolio: 1275000, benchmark: 1158000 },
  { date: "2024-10-20", portfolio: 1290000, benchmark: 1165000 },
  { date: "2024-10-25", portfolio: 1305000, benchmark: 1173000 },
  { date: "2024-10-31", portfolio: 1320000, benchmark: 1180000 },
  { date: "2025-01-05", portfolio: 1336000, benchmark: 1188000 },
  { date: "2025-01-10", portfolio: 1352000, benchmark: 1195000 },
  { date: "2025-01-15", portfolio: 1368000, benchmark: 1203000 },
  { date: "2025-01-20", portfolio: 1384000, benchmark: 1300000 },
  { date: "2025-01-25", portfolio: 1400000, benchmark: 1308000 },
  { date: "2025-01-31", portfolio: 1417000, benchmark: 1315000 },
  { date: "2025-02-05", portfolio: 1434000, benchmark: 1233000 },
  { date: "2025-02-10", portfolio: 1451000, benchmark: 1240000 },
  { date: "2025-02-15", portfolio: 1468000, benchmark: 1248000 },
  { date: "2025-02-20", portfolio: 1485000, benchmark: 1255000 },
  { date: "2025-02-25", portfolio: 1502000, benchmark: 1263000 },
  { date: "2025-02-31", portfolio: 1520000, benchmark: 1270000 },
  { date: "2025-03-05", portfolio: 1538000, benchmark: 1278000 },
  { date: "2025-03-10", portfolio: 1556000, benchmark: 1285000 },
  { date: "2025-03-15", portfolio: 1574000, benchmark: 1293000 },
  { date: "2025-03-20", portfolio: 1592000, benchmark: 1300000 },
  { date: "2025-03-25", portfolio: 1610000, benchmark: 1308000 },
  { date: "2025-03-31", portfolio: 1624000, benchmark: 1315000 },
]

export function PerformanceChart() {
  const { period } = usePeriod()
  const data = filterDataByPeriod(allData, period)

  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Performance Acumulada</CardTitle>
        <CardDescription className="text-muted-foreground">Comparação com benchmark (CDI + 2%)</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorPortfolio" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorBenchmark" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="hsl(var(--secondary))" stopOpacity={0.3} />
                <stop offset="95%" stopColor="hsl(var(--secondary))" stopOpacity={0} />
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
            <YAxis
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickFormatter={(value) => `R$ ${(value / 1000000).toFixed(1)}M`}
            />
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
              formatter={(value: number) => [`R$ ${value.toLocaleString("pt-BR")}`, ""]}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="portfolio"
              stroke="hsl(var(--primary))"
              fillOpacity={1}
              fill="url(#colorPortfolio)"
              name="Portfólio"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="benchmark"
              stroke="hsl(var(--secondary))"
              fillOpacity={1}
              fill="url(#colorBenchmark)"
              name="Benchmark"
              strokeWidth={2}
            />
            <Brush
              dataKey="date"
              height={50}
              stroke="#3b82f6"
              fill="#f1f5f9"
              fillOpacity={0.8}
              travellerWidth={14}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear().toString().slice(2)}`
              }}
            >
              <AreaChart data={data}>
                <Area
                  type="monotone"
                  dataKey="portfolio"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.3}
                  strokeWidth={1.5}
                />
              </AreaChart>
            </Brush>
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
