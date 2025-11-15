"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, ArrowDownRight } from "lucide-react"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { Empty } from "./ui/empty"

export function AssetsTable() {
  const { analysisResult } = useDashboardData()
  const assets = analysisResult?.assets || []

  if (!analysisResult) {
    return (
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Ativos da Carteira</CardTitle>
          <CardDescription className="text-muted-foreground">Detalhamento dos principais investimentos</CardDescription>
        </CardHeader>
        <CardContent>
          <Empty title="Nenhum dado para exibir" description="Por favor, envie suas operações na página 'Enviar' para ver os ativos." />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">Ativos da Carteira</CardTitle>
        <CardDescription className="text-muted-foreground">Detalhamento dos principais investimentos</CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="border-border">
              <TableHead className="text-muted-foreground">Ativo</TableHead>
              <TableHead className="text-muted-foreground">Tipo</TableHead>
              <TableHead className="text-right text-muted-foreground">Alocação</TableHead>
              <TableHead className="text-right text-muted-foreground">Valor</TableHead>
              <TableHead className="text-right text-muted-foreground">Retorno</TableHead>
              <TableHead className="text-muted-foreground">Risco</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {assets.map((asset: any) => (
              <TableRow key={asset.name} className="border-border">
                <TableCell className="font-medium text-foreground">{asset.name}</TableCell>
                <TableCell className="text-muted-foreground">{asset.type}</TableCell>
                <TableCell className="text-right text-foreground">{asset.allocation}%</TableCell>
                <TableCell className="text-right font-mono text-foreground">
                  R$ {asset.value.toLocaleString("pt-BR")}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    {asset.return > 0 ? (
                      <ArrowUpRight className="h-4 w-4 text-success" />
                    ) : (
                      <ArrowDownRight className="h-4 w-4 text-destructive" />
                    )}
                    <span className={asset.return > 0 ? "text-success" : "text-destructive"}>
                      {asset.return > 0 ? "+" : ""}
                      {asset.return}%
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge
                    variant={asset.risk === "Baixo" ? "secondary" : asset.risk === "Médio" ? "default" : "destructive"}
                  >
                    {asset.risk}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
