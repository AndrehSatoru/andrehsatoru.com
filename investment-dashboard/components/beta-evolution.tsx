"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts"

const data = [
  { date: "2023-07", beta: 0.85 },
  { date: "2023-08", beta: 0.88 },
  { date: "2023-09", beta: 0.92 },
  { date: "2023-10", beta: 0.95 },
  { date: "2023-11", beta: 0.98 },
  { date: "2023-12", beta: 1.02 },
  { date: "2024-01", beta: 1.05 },
  { date: "2024-02", beta: 1.08 },
  { date: "2024-03", beta: 1.12 },
  { date: "2024-04", beta: 1.15 },
  { date: "2024-05", beta: 1.18 },
  { date: "2024-06", beta: 1.22 },
  { date: "2024-07", beta: 1.25 },
  { date: "2024-08", beta: 1.28 },
  { date: "2024-09", beta: 1.32 },
  { date: "2024-10", beta: 1.35 },
  { date: "2024-11", beta: 1.38 },
  { date: "2024-12", beta: 1.42 },
  { date: "2025-01", beta: 1.45 },
  { date: "2025-02", beta: 1.42 },
  { date: "2025-03", beta: 1.38 },
  { date: "2025-04", beta: 1.35 },
  { date: "2025-05", beta: 1.32 },
  { date: "2025-06", beta: 1.28 },
  { date: "2025-07", beta: 1.25 },
  { date: "2025-08", beta: 1.22 },
  { date: "2025-09", beta: 1.18 },
  { date: "2025-10", beta: 1.15 },
]

export function BetaEvolution() {
  const currentBeta = data[data.length - 1].beta
  const avgBeta = (data.reduce((sum, d) => sum + d.beta, 0) / data.length).toFixed(2)
  const minBeta = Math.min(...data.map((d) => d.beta)).toFixed(2)
  const maxBeta = Math.max(...data.map((d) => d.beta)).toFixed(2)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-balance">Evolução do Beta da Carteira</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4 grid grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Beta Atual</p>
            <p className="text-2xl font-bold">{currentBeta.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Beta Médio</p>
            <p className="text-2xl font-bold">{avgBeta}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Beta Mínimo</p>
            <p className="text-2xl font-bold text-green-600">{minBeta}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Beta Máximo</p>
            <p className="text-2xl font-bold text-red-600">{maxBeta}</p>
          </div>
        </div>

        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="date" stroke="#6b7280" tick={{ fill: "#6b7280" }} />
              <YAxis stroke="#6b7280" tick={{ fill: "#6b7280" }} domain={[0.5, 1.8]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(255, 255, 255, 0.95)",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                }}
                formatter={(value: number) => [value.toFixed(2), "Beta"]}
              />
              <ReferenceLine
                y={1.0}
                stroke="#9ca3af"
                strokeDasharray="5 5"
                label={{ value: "Beta = 1.0 (Mercado)", position: "right", fill: "#6b7280" }}
              />
              <Line
                type="monotone"
                dataKey="beta"
                stroke="#2563eb"
                strokeWidth={3}
                dot={{ fill: "#2563eb", r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-4 rounded-lg bg-muted p-4">
          <p className="text-sm text-muted-foreground">
            <strong>Interpretação:</strong> Beta mede a sensibilidade da carteira em relação ao mercado. Beta = 1.0
            significa que a carteira se move igual ao mercado. Beta {">"} 1.0 indica maior volatilidade, enquanto Beta{" "}
            {"<"} 1.0 indica menor volatilidade que o mercado.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
