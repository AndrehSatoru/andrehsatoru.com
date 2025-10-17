"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Brush } from "recharts"
import { usePeriod, filterDataByPeriod } from "@/lib/period-context"

const allAllocationData = [
  {
    date: "2024-07-01",
    "AURA33.SA": 8,
    "AZZA3.SA": 6,
    "CPFE3.SA": 7,
    "DIRR3.SA": 5,
    "EMBR3.SA": 4,
    EQIX: 8,
    "EQTL3.SA": 9,
    "ITX.MC": 3,
    "LAVV3.SA": 5,
    "MC.PA": 6,
    NEE: 7,
    "PRIO3.SA": 6,
    "SBSP3.SA": 5,
    "TFCO4.SA": 4,
    VAL: 3,
    "VALE3.SA": 6,
    Caixa: 8,
  },
  {
    date: "2024-07-06",
    "AURA33.SA": 8,
    "AZZA3.SA": 6,
    "CPFE3.SA": 7,
    "DIRR3.SA": 5,
    "EMBR3.SA": 4,
    EQIX: 8,
    "EQTL3.SA": 9,
    "ITX.MC": 3,
    "LAVV3.SA": 5,
    "MC.PA": 6,
    NEE: 7,
    "PRIO3.SA": 6,
    "SBSP3.SA": 5,
    "TFCO4.SA": 4,
    VAL: 3,
    "VALE3.SA": 6,
    Caixa: 8,
  },
  {
    date: "2024-07-11",
    "AURA33.SA": 7,
    "AZZA3.SA": 6,
    "CPFE3.SA": 7,
    "DIRR3.SA": 5,
    "EMBR3.SA": 5,
    EQIX: 8,
    "EQTL3.SA": 9,
    "ITX.MC": 3,
    "LAVV3.SA": 5,
    "MC.PA": 6,
    NEE: 7,
    "PRIO3.SA": 6,
    "SBSP3.SA": 5,
    "TFCO4.SA": 4,
    VAL: 3,
    "VALE3.SA": 6,
    Caixa: 7,
  },
  {
    date: "2024-07-16",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 7,
    "DIRR3.SA": 5,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 9,
    "ITX.MC": 4,
    "LAVV3.SA": 5,
    "MC.PA": 6,
    NEE: 7,
    "PRIO3.SA": 6,
    "SBSP3.SA": 5,
    "TFCO4.SA": 4,
    VAL: 3,
    "VALE3.SA": 6,
    Caixa: 7,
  },
  {
    date: "2024-07-21",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 4,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 5,
    "SBSP3.SA": 6,
    "TFCO4.SA": 5,
    VAL: 4,
    "VALE3.SA": 5,
    Caixa: 6,
  },
  {
    date: "2024-07-26",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 4,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 5,
    "SBSP3.SA": 6,
    "TFCO4.SA": 5,
    VAL: 4,
    "VALE3.SA": 5,
    Caixa: 6,
  },
  {
    date: "2024-07-31",
    "AURA33.SA": 8,
    "AZZA3.SA": 6,
    "CPFE3.SA": 7,
    "DIRR3.SA": 5,
    "EMBR3.SA": 6,
    EQIX: 6,
    "EQTL3.SA": 9,
    "ITX.MC": 5,
    "LAVV3.SA": 5,
    "MC.PA": 6,
    NEE: 7,
    "PRIO3.SA": 6,
    "SBSP3.SA": 5,
    "TFCO4.SA": 4,
    VAL: 5,
    "VALE3.SA": 6,
    Caixa: 4,
  },
  {
    date: "2024-08-05",
    "AURA33.SA": 8,
    "AZZA3.SA": 6,
    "CPFE3.SA": 7,
    "DIRR3.SA": 5,
    "EMBR3.SA": 6,
    EQIX: 6,
    "EQTL3.SA": 9,
    "ITX.MC": 5,
    "LAVV3.SA": 5,
    "MC.PA": 6,
    NEE: 7,
    "PRIO3.SA": 6,
    "SBSP3.SA": 5,
    "TFCO4.SA": 4,
    VAL: 5,
    "VALE3.SA": 6,
    Caixa: 4,
  },
  {
    date: "2024-08-10",
    "AURA33.SA": 8,
    "AZZA3.SA": 6,
    "CPFE3.SA": 7,
    "DIRR3.SA": 5,
    "EMBR3.SA": 6,
    EQIX: 6,
    "EQTL3.SA": 9,
    "ITX.MC": 5,
    "LAVV3.SA": 5,
    "MC.PA": 6,
    NEE: 7,
    "PRIO3.SA": 7,
    "SBSP3.SA": 5,
    "TFCO4.SA": 4,
    VAL: 5,
    "VALE3.SA": 5,
    Caixa: 4,
  },
  {
    date: "2024-08-15",
    "AURA33.SA": 8,
    "AZZA3.SA": 6,
    "CPFE3.SA": 7,
    "DIRR3.SA": 5,
    "EMBR3.SA": 6,
    EQIX: 6,
    "EQTL3.SA": 9,
    "ITX.MC": 5,
    "LAVV3.SA": 5,
    "MC.PA": 6,
    NEE: 7,
    "PRIO3.SA": 7,
    "SBSP3.SA": 5,
    "TFCO4.SA": 4,
    VAL: 5,
    "VALE3.SA": 5,
    Caixa: 4,
  },
  {
    date: "2024-08-20",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 6,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 6,
    "SBSP3.SA": 6,
    "TFCO4.SA": 5,
    VAL: 4,
    "VALE3.SA": 4,
    Caixa: 4,
  },
  {
    date: "2024-08-25",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 6,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 6,
    "SBSP3.SA": 6,
    "TFCO4.SA": 5,
    VAL: 4,
    "VALE3.SA": 4,
    Caixa: 4,
  },
  {
    date: "2024-08-30",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 6,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 6,
    "SBSP3.SA": 6,
    "TFCO4.SA": 5,
    VAL: 4,
    "VALE3.SA": 4,
    Caixa: 4,
  },
  {
    date: "2024-09-04",
    "AURA33.SA": 8,
    "AZZA3.SA": 6,
    "CPFE3.SA": 7,
    "DIRR3.SA": 5,
    "EMBR3.SA": 6,
    EQIX: 6,
    "EQTL3.SA": 9,
    "ITX.MC": 7,
    "LAVV3.SA": 5,
    "MC.PA": 6,
    NEE: 7,
    "PRIO3.SA": 7,
    "SBSP3.SA": 5,
    "TFCO4.SA": 4,
    VAL: 5,
    "VALE3.SA": 4,
    Caixa: 3,
  },
  {
    date: "2024-09-09",
    "AURA33.SA": 8,
    "AZZA3.SA": 6,
    "CPFE3.SA": 7,
    "DIRR3.SA": 5,
    "EMBR3.SA": 6,
    EQIX: 6,
    "EQTL3.SA": 9,
    "ITX.MC": 7,
    "LAVV3.SA": 5,
    "MC.PA": 6,
    NEE: 7,
    "PRIO3.SA": 7,
    "SBSP3.SA": 5,
    "TFCO4.SA": 4,
    VAL: 5,
    "VALE3.SA": 4,
    Caixa: 3,
  },
  {
    date: "2024-09-14",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 8,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 6,
    "SBSP3.SA": 6,
    "TFCO4.SA": 5,
    VAL: 4,
    "VALE3.SA": 3,
    Caixa: 3,
  },
  {
    date: "2024-09-19",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 8,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 6,
    "SBSP3.SA": 6,
    "TFCO4.SA": 5,
    VAL: 4,
    "VALE3.SA": 3,
    Caixa: 3,
  },
  {
    date: "2024-09-24",
    "AURA33.SA": 8,
    "AZZA3.SA": 6,
    "CPFE3.SA": 7,
    "DIRR3.SA": 5,
    "EMBR3.SA": 6,
    EQIX: 6,
    "EQTL3.SA": 9,
    "ITX.MC": 7,
    "LAVV3.SA": 5,
    "MC.PA": 6,
    NEE: 7,
    "PRIO3.SA": 7,
    "SBSP3.SA": 5,
    "TFCO4.SA": 6,
    VAL: 5,
    "VALE3.SA": 3,
    Caixa: 2,
  },
  {
    date: "2024-09-29",
    "AURA33.SA": 8,
    "AZZA3.SA": 6,
    "CPFE3.SA": 7,
    "DIRR3.SA": 5,
    "EMBR3.SA": 6,
    EQIX: 6,
    "EQTL3.SA": 9,
    "ITX.MC": 7,
    "LAVV3.SA": 5,
    "MC.PA": 6,
    NEE: 7,
    "PRIO3.SA": 7,
    "SBSP3.SA": 5,
    "TFCO4.SA": 6,
    VAL: 5,
    "VALE3.SA": 3,
    Caixa: 2,
  },
  {
    date: "2024-10-04",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 8,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 6,
    "SBSP3.SA": 6,
    "TFCO4.SA": 6,
    VAL: 4,
    "VALE3.SA": 3,
    Caixa: 2,
  },
  {
    date: "2024-10-09",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 8,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 6,
    "SBSP3.SA": 6,
    "TFCO4.SA": 6,
    VAL: 4,
    "VALE3.SA": 3,
    Caixa: 2,
  },
  {
    date: "2024-10-14",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 8,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 6,
    "SBSP3.SA": 6,
    "TFCO4.SA": 6,
    VAL: 4,
    "VALE3.SA": 3,
    Caixa: 2,
  },
  {
    date: "2024-10-19",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 8,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 6,
    "SBSP3.SA": 6,
    "TFCO4.SA": 6,
    VAL: 4,
    "VALE3.SA": 3,
    Caixa: 2,
  },
  {
    date: "2024-10-24",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 8,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 6,
    "SBSP3.SA": 6,
    "TFCO4.SA": 6,
    VAL: 4,
    "VALE3.SA": 3,
    Caixa: 2,
  },
  {
    date: "2024-10-29",
    "AURA33.SA": 7,
    "AZZA3.SA": 7,
    "CPFE3.SA": 6,
    "DIRR3.SA": 6,
    "EMBR3.SA": 5,
    EQIX: 7,
    "EQTL3.SA": 8,
    "ITX.MC": 8,
    "LAVV3.SA": 6,
    "MC.PA": 5,
    NEE: 8,
    "PRIO3.SA": 6,
    "SBSP3.SA": 6,
    "TFCO4.SA": 6,
    VAL: 4,
    "VALE3.SA": 3,
    Caixa: 2,
  },
]

const assets = [
  { key: "AURA33.SA", color: "#1e40af" },
  { key: "AZZA3.SA", color: "#ea580c" },
  { key: "CPFE3.SA", color: "#16a34a" },
  { key: "DIRR3.SA", color: "#dc2626" },
  { key: "EMBR3.SA", color: "#9333ea" },
  { key: "EQIX", color: "#78716c" },
  { key: "EQTL3.SA", color: "#ec4899" },
  { key: "ITX.MC", color: "#64748b" },
  { key: "LAVV3.SA", color: "#84cc16" },
  { key: "MC.PA", color: "#06b6d4" },
  { key: "NEE", color: "#0284c7" },
  { key: "PRIO3.SA", color: "#f97316" },
  { key: "SBSP3.SA", color: "#22c55e" },
  { key: "TFCO4.SA", color: "#ef4444" },
  { key: "VAL", color: "#8b5cf6" },
  { key: "VALE3.SA", color: "#92400e" },
  { key: "Caixa", color: "#db2777" },
]

export function AllocationEvolution() {
  const { period } = usePeriod()
  const allocationData = filterDataByPeriod(allAllocationData, period)

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">Evolução da Alocação Percentual da Carteira</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={550}>
          <AreaChart data={allocationData} stackOffset="expand" margin={{ top: 10, right: 120, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="date"
              className="text-xs"
              label={{ value: "Data", position: "insideBottom", offset: -5 }}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${date.getDate().toString().padStart(2, "0")}/${(date.getMonth() + 1).toString().padStart(2, "0")}`
              }}
            />
            <YAxis
              className="text-xs"
              tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
              label={{
                value: "Peso %",
                angle: -90,
                position: "insideLeft",
              }}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const date = new Date(payload[0].payload.date)
                  const formattedDate = `${date.getDate().toString().padStart(2, "0")}/${(date.getMonth() + 1).toString().padStart(2, "0")}/${date.getFullYear()}`

                  return (
                    <div className="rounded-lg border bg-background p-3 shadow-lg">
                      <p className="font-semibold mb-2">{formattedDate}</p>
                      <div className="space-y-1 max-h-64 overflow-y-auto">
                        {payload
                          .sort((a, b) => (b.value as number) - (a.value as number))
                          .map((entry) => (
                            <div key={entry.dataKey} className="flex items-center justify-between gap-4 text-sm">
                              <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: entry.color }} />
                                <span>{entry.name}</span>
                              </div>
                              <span className="font-medium">{((entry.value as number) * 100).toFixed(1)}%</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )
                }
                return null
              }}
            />
            <Legend
              layout="vertical"
              align="right"
              verticalAlign="middle"
              wrapperStyle={{ paddingLeft: "20px" }}
              content={({ payload }) => (
                <div className="space-y-1">
                  <p className="font-semibold text-sm mb-2">Ativos</p>
                  {payload?.map((entry) => (
                    <div key={entry.value} className="flex items-center gap-2 text-xs">
                      <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: entry.color }} />
                      <span>{entry.value}</span>
                    </div>
                  ))}
                </div>
              )}
            />
            {assets.map((asset) => (
              <Area
                key={asset.key}
                type="monotone"
                dataKey={asset.key}
                stackId="1"
                stroke={asset.color}
                fill={asset.color}
                strokeWidth={0.5}
              />
            ))}
            <Brush
              dataKey="date"
              height={50}
              stroke="hsl(var(--primary))"
              fill="hsl(var(--background))"
              fillOpacity={0.3}
              travellerWidth={12}
              tickFormatter={(value) => {
                const date = new Date(value)
                return `${date.getDate().toString().padStart(2, "0")}/${(date.getMonth() + 1).toString().padStart(2, "0")}`
              }}
            >
              <AreaChart data={allocationData} stackOffset="expand">
                {assets.map((asset) => (
                  <Area
                    key={asset.key}
                    type="monotone"
                    dataKey={asset.key}
                    stackId="1"
                    stroke="none"
                    fill={asset.color}
                    fillOpacity={0.6}
                  />
                ))}
              </AreaChart>
            </Brush>
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
