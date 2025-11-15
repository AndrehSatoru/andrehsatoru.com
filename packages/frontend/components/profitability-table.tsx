"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const monthlyData = [
  {
    year: 2017,
    jan: null,
    fev: -1.54,
    mar: 1.49,
    abr: 0.11,
    mai: -3.35,
    jun: 1.86,
    jul: 4.44,
    ago: 5.12,
    set: 3.36,
    out: -1.65,
    nov: -2.05,
    dez: 3.88,
    acumAno: 11.85,
    cdi: 10.64,
    acumFdo: 11.85,
    acumCdi: 10.64,
  },
  {
    year: 2018,
    jan: 9.13,
    fev: -0.62,
    mar: 1.16,
    abr: -3.07,
    mai: -10.13,
    jun: -4.46,
    jul: 6.08,
    ago: -6.28,
    set: 1.52,
    out: 16.21,
    nov: 5.24,
    dez: 2.36,
    acumAno: 15.37,
    cdi: 15.03,
    acumFdo: 29.04,
    acumCdi: 27.28,
  },
  {
    year: 2019,
    jan: 9.21,
    fev: -3.27,
    mar: -3.03,
    abr: 1.65,
    mai: 3.43,
    jun: 4.23,
    jul: 2.73,
    ago: 2.21,
    set: 2.75,
    out: 1.78,
    nov: 0.58,
    dez: 7.57,
    acumAno: 33.37,
    cdi: 31.58,
    acumFdo: 72.1,
    acumCdi: 67.48,
  },
  {
    year: 2020,
    jan: 0.21,
    fev: -5.5,
    mar: -31.47,
    abr: 18.29,
    mai: 9.5,
    jun: 8.43,
    jul: 6.33,
    ago: -0.17,
    set: -5.09,
    out: -1.31,
    nov: 10.91,
    dez: 6.02,
    acumAno: 6.56,
    cdi: 2.92,
    acumFdo: 83.38,
    acumCdi: 72.36,
  },
  {
    year: 2021,
    jan: 0.28,
    fev: -5.28,
    mar: 2.4,
    abr: 3.57,
    mai: 2.7,
    jun: 2.59,
    jul: -3.28,
    ago: -0.77,
    set: -4.54,
    out: -13.51,
    nov: -4.64,
    dez: 2.19,
    acumAno: -18.03,
    cdi: -11.93,
    acumFdo: 50.31,
    acumCdi: 51.8,
  },
  {
    year: 2022,
    jan: 2.2,
    fev: -0.83,
    mar: 4.61,
    abr: -12.61,
    mai: -4.86,
    jun: -11.03,
    jul: 7.28,
    ago: 7.07,
    set: 1.5,
    out: 8.03,
    nov: -11.57,
    dez: -4.08,
    acumAno: -16.21,
    cdi: 4.69,
    acumFdo: 25.95,
    acumCdi: 58.92,
  },
  {
    year: 2023,
    jan: 0.46,
    fev: -4.37,
    mar: -1.94,
    abr: -1.63,
    mai: 4.86,
    jun: 7.67,
    jul: 1.92,
    ago: -2.43,
    set: -0.34,
    out: -6.17,
    nov: 8.14,
    dez: 3.91,
    acumAno: 9.33,
    cdi: 22.28,
    acumFdo: 37.7,
    acumCdi: 94.32,
  },
  {
    year: 2024,
    jan: -4.68,
    fev: -0.83,
    mar: 1.29,
    abr: -7.1,
    mai: -4.44,
    jun: 1.92,
    jul: 2.02,
    ago: 4.02,
    set: -2.14,
    out: 0.02,
    nov: -3.43,
    dez: -4.12,
    acumAno: -16.69,
    cdi: -10.36,
    acumFdo: 14.72,
    acumCdi: 74.19,
  },
  {
    year: 2025,
    jan: 5.8,
    fev: -2.07,
    mar: 3.86,
    abr: 7.53,
    mai: 3.5,
    jun: 0.92,
    jul: -5.21,
    ago: 7.84,
    set: 4.95,
    out: null,
    nov: null,
    dez: null,
    acumAno: 29.66,
    cdi: 21.58,
    acumFdo: 48.76,
    acumCdi: 111.78,
  },
]

export function ProfitabilityTable() {
  const formatValue = (value: number | null) => {
    if (value === null) return "-"
    return value.toFixed(2) + "%"
  }

  const getCellColor = (value: number | null) => {
    if (value === null) return ""
    if (value > 0) return "text-green-600 dark:text-green-400"
    if (value < 0) return "text-red-600 dark:text-red-400"
    return ""
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-balance">Rentabilidades (%)</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="px-2 py-2 text-left font-medium">Ano</th>
                <th className="px-2 py-2 text-right font-medium">Jan</th>
                <th className="px-2 py-2 text-right font-medium">Fev</th>
                <th className="px-2 py-2 text-right font-medium">Mar</th>
                <th className="px-2 py-2 text-right font-medium">Abr</th>
                <th className="px-2 py-2 text-right font-medium">Mai</th>
                <th className="px-2 py-2 text-right font-medium">Jun</th>
                <th className="px-2 py-2 text-right font-medium">Jul</th>
                <th className="px-2 py-2 text-right font-medium">Ago</th>
                <th className="px-2 py-2 text-right font-medium">Set</th>
                <th className="px-2 py-2 text-right font-medium">Out</th>
                <th className="px-2 py-2 text-right font-medium">Nov</th>
                <th className="px-2 py-2 text-right font-medium">Dez</th>
                <th className="px-2 py-2 text-right font-medium bg-muted">Acum. Ano</th>
                <th className="px-2 py-2 text-right font-medium bg-muted">CDI</th>
                <th className="px-2 py-2 text-right font-medium bg-muted">Acum. Fdo.</th>
                <th className="px-2 py-2 text-right font-medium bg-muted">Acum. CDI*</th>
              </tr>
            </thead>
            <tbody>
              {monthlyData.map((row) => (
                <tr key={row.year} className="border-b hover:bg-muted/50">
                  <td className="px-2 py-2 font-medium">{row.year}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.jan)}`}>{formatValue(row.jan)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.fev)}`}>{formatValue(row.fev)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.mar)}`}>{formatValue(row.mar)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.abr)}`}>{formatValue(row.abr)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.mai)}`}>{formatValue(row.mai)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.jun)}`}>{formatValue(row.jun)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.jul)}`}>{formatValue(row.jul)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.ago)}`}>{formatValue(row.ago)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.set)}`}>{formatValue(row.set)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.out)}`}>{formatValue(row.out)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.nov)}`}>{formatValue(row.nov)}</td>
                  <td className={`px-2 py-2 text-right ${getCellColor(row.dez)}`}>{formatValue(row.dez)}</td>
                  <td className={`px-2 py-2 text-right font-medium bg-muted ${getCellColor(row.acumAno)}`}>
                    {formatValue(row.acumAno)}
                  </td>
                  <td className={`px-2 py-2 text-right bg-muted ${getCellColor(row.cdi)}`}>{formatValue(row.cdi)}</td>
                  <td className={`px-2 py-2 text-right font-medium bg-muted ${getCellColor(row.acumFdo)}`}>
                    {formatValue(row.acumFdo)}
                  </td>
                  <td className={`px-2 py-2 text-right bg-muted ${getCellColor(row.acumCdi)}`}>
                    {formatValue(row.acumCdi)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-muted-foreground mt-4">* Calculado desde a constituição do fundo até 30/set/2025</p>
      </CardContent>
    </Card>
  )
}
