"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
} from "recharts"
import { usePeriod, filterDataByPeriod } from "@/lib/period-context"

const allRollingReturnsData = [
  { date: "2024-08", portfolio: 19, benchmark: 3 },
  { date: "2024-09", portfolio: 22, benchmark: 15 },
  { date: "2024-10", portfolio: 28, benchmark: 18 },
  { date: "2024-11", portfolio: 31, benchmark: 16 },
  { date: "2024-12", portfolio: 29, benchmark: 14 },
  { date: "2025-01", portfolio: 27, benchmark: 15 },
  { date: "2025-02", portfolio: 24, benchmark: 2 },
  { date: "2025-03", portfolio: 21, benchmark: -1 },
  { date: "2025-04", portfolio: 17, benchmark: -8 },
  { date: "2025-05", portfolio: 20, benchmark: -10 },
  { date: "2025-06", portfolio: 23, benchmark: -5 },
  { date: "2025-07", portfolio: 25, benchmark: 1 },
  { date: "2025-08", portfolio: 27, benchmark: 5 },
  { date: "2025-09", portfolio: 29, benchmark: 8 },
  { date: "2025-10", portfolio: 32, benchmark: 10 },
]

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg p-3">
        <p className="text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">{payload[0].payload.date}</p>
        <div className="space-y-1">
          <p className="text-sm text-gray-900 dark:text-gray-100">
            <span className="font-medium">Retorno Anualizado:</span>{" "}
            <span className="font-semibold">{payload[0].value.toFixed(1)}%</span>
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            <span className="font-medium">Benchmark:</span>{" "}
            <span className="font-semibold">{payload[1].value.toFixed(1)}%</span>
          </p>
        </div>
      </div>
    )
  }
  return null
}

export function RollingReturns() {
  const { period } = usePeriod()
  const rollingReturnsData = filterDataByPeriod(allRollingReturnsData, period)

  const currentReturn = rollingReturnsData[rollingReturnsData.length - 1]?.portfolio || 0
  const currentBenchmark = rollingReturnsData[rollingReturnsData.length - 1]?.benchmark || 0
  const outperformance = currentReturn - currentBenchmark

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-balance">Retorno Anualizado</CardTitle>
        <div className="flex flex-wrap gap-4 text-sm mt-2">
          <div>
            <span className="text-muted-foreground">Retorno Atual: </span>
            <span className="font-semibold text-foreground">{currentReturn.toFixed(1)}%</span>
          </div>
          <div>
            <span className="text-muted-foreground">Benchmark: </span>
            <span className="font-semibold">{currentBenchmark.toFixed(1)}%</span>
          </div>
          <div>
            <span className="text-muted-foreground">Outperformance: </span>
            <span className={`font-semibold ${outperformance >= 0 ? "text-green-600" : "text-red-600"}`}>
              {outperformance >= 0 ? "+" : ""}
              {outperformance.toFixed(1)}%
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div style={{ width: "100%", height: 450 }}>
          <ResponsiveContainer>
            <LineChart data={rollingReturnsData} margin={{ top: 10, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
              <XAxis
                dataKey="date"
                stroke="#6b7280"
                tick={{ fill: "#6b7280", fontSize: 12 }}
                tickLine={{ stroke: "#e5e7eb" }}
                label={{
                  value: "Data",
                  position: "insideBottom",
                  offset: -10,
                  style: { fill: "#6b7280", fontSize: 12 },
                }}
              />
              <YAxis
                stroke="#6b7280"
                tick={{ fill: "#6b7280", fontSize: 12 }}
                tickLine={{ stroke: "#e5e7eb" }}
                tickFormatter={(value) => `${value}%`}
                label={{
                  value: "Retorno Anualizado",
                  angle: -90,
                  position: "insideLeft",
                  style: { fill: "#6b7280", fontSize: 12 },
                }}
                domain={[-15, 35]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend
                wrapperStyle={{
                  paddingTop: "20px",
                }}
                iconType="line"
              />
              <ReferenceLine y={0} stroke="#9ca3af" strokeDasharray="3 3" strokeWidth={1} />
              <Line
                type="monotone"
                dataKey="portfolio"
                stroke="#000000"
                strokeWidth={2.5}
                dot={false}
                name="Retorno Anualizado"
                className="dark:stroke-white"
              />
              <Line
                type="monotone"
                dataKey="benchmark"
                stroke="#6b7280"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Retorno Anualizado Benchmark"
              />
              <Brush
                dataKey="date"
                height={50}
                stroke="#000000"
                fill="hsl(var(--background))"
                fillOpacity={0.3}
                travellerWidth={12}
              >
                <LineChart data={rollingReturnsData}>
                  <Line type="monotone" dataKey="portfolio" stroke="#000000" strokeWidth={1} dot={false} />
                </LineChart>
              </Brush>
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
