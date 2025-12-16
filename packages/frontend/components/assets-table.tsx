"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, ArrowDownRight } from "lucide-react"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { Empty } from "./ui/empty"

export function AssetsTable() {
  const { analysisResult } = useDashboardData()
  
  // Extrair dados de alocação do resultado
  const alocacaoData = analysisResult?.alocacao?.alocacao || {}
  const metadados = analysisResult?.metadados || {}
  
  // Converter para array de ativos
  const assets = Object.entries(alocacaoData).map(([name, info]: [string, any]) => ({
    name,
    allocation: info?.percentual?.toFixed(2) || 0,
    value: info?.valor_total || 0,
    quantidade: info?.quantidade || 0,
    precoUnitario: info?.preco_unitario || 0,
  }))

  if (!analysisResult || assets.length === 0) {
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
        <CardDescription className="text-muted-foreground">
          {metadados.transacoes} transação(ões) • {metadados.ativos?.length || 0} ativo(s)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="border-border">
              <TableHead className="text-muted-foreground">Ativo</TableHead>
              <TableHead className="text-right text-muted-foreground">Quantidade</TableHead>
              <TableHead className="text-right text-muted-foreground">Preço Unitário</TableHead>
              <TableHead className="text-right text-muted-foreground">Valor Total</TableHead>
              <TableHead className="text-right text-muted-foreground">Alocação</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {assets.map((asset: any) => (
              <TableRow key={asset.name} className="border-border">
                <TableCell className="font-medium text-foreground">{asset.name}</TableCell>
                <TableCell className="text-right font-mono text-foreground">
                  {asset.quantidade.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                </TableCell>
                <TableCell className="text-right font-mono text-foreground">
                  R$ {asset.precoUnitario.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                </TableCell>
                <TableCell className="text-right font-mono text-foreground">
                  R$ {asset.value.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}
                </TableCell>
                <TableCell className="text-right">
                  <Badge variant="secondary">
                    {asset.allocation}%
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
