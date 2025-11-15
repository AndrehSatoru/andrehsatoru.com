"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"

const riskContributionData = [
  { asset: "AURA33.SA", contribution: 30.7 },
  { asset: "EMBR3.SA", contribution: 22.2 },
  { asset: "DIRR3.SA", contribution: 9.9 },
  { asset: "LAVV3.SA", contribution: 7.2 },
  { asset: "SBSP3.SA", contribution: 6.2 },
  { asset: "TFCO4.SA", contribution: 4.3 },
  { asset: "EQTL3.SA", contribution: 2.9 },
  { asset: "NEE", contribution: 2.6 },
  { asset: "VAL", contribution: 2.5 },
  { asset: "EQIX", contribution: 2.3 },
  { asset: "ITX.MC", contribution: 1.8 },
  { asset: "VALE3.SA", contribution: 1.8 },
  { asset: "CPFE3.SA", contribution: 1.8 },
  { asset: "PRIO3.SA", contribution: 1.7 },
  { asset: "AZZA3.SA", contribution: 1.5 },
  { asset: "MC.PA", contribution: 0.6 },
]

export function RiskContribution() {
  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="text-balance">Decomposição da Contribuição de Risco (Volatilidade)</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={500}>
          <BarChart data={riskContributionData} layout="vertical" margin={{ top: 5, right: 60, left: 80, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              type="number"
              domain={[0, 35]}
              tickFormatter={(value) => `${value.toFixed(1)}%`}
              stroke="hsl(var(--foreground))"
              label={{
                value: "Contribuição Percentual para a Volatilidade Total",
                position: "insideBottom",
                offset: -5,
                style: { fill: "hsl(var(--foreground))" },
              }}
            />
            <YAxis type="category" dataKey="asset" stroke="hsl(var(--foreground))" width={80} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--popover))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "var(--radius)",
              }}
              formatter={(value: number) => [`${value.toFixed(1)}%`, "Contribuição"]}
            />
            <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
              {riskContributionData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill="hsl(var(--chart-1))" />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Maior Contribuidor</p>
            <p className="font-semibold">
              {riskContributionData[0].asset} ({riskContributionData[0].contribution}%)
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Top 3 Contribuição</p>
            <p className="font-semibold">
              {(
                riskContributionData[0].contribution +
                riskContributionData[1].contribution +
                riskContributionData[2].contribution
              ).toFixed(1)}
              %
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Concentração de Risco</p>
            <p className="font-semibold">{riskContributionData[0].contribution > 25 ? "Alta" : "Moderada"}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
