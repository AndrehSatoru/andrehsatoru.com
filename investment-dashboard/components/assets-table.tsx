import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { ArrowUpRight, ArrowDownRight } from "lucide-react"

const assets = [
  {
    name: "Tesouro IPCA+ 2035",
    type: "Renda Fixa",
    allocation: 25.5,
    value: 414750,
    return: 8.2,
    risk: "Baixo",
  },
  {
    name: "PETR4",
    type: "Ações",
    allocation: 12.3,
    value: 199890,
    return: 15.7,
    risk: "Alto",
  },
  {
    name: "HGLG11",
    type: "FII",
    allocation: 8.7,
    value: 141390,
    return: 11.2,
    risk: "Médio",
  },
  {
    name: "Verde AM",
    type: "Multimercado",
    allocation: 7.0,
    value: 113750,
    return: 9.8,
    risk: "Médio",
  },
  {
    name: "VALE3",
    type: "Ações",
    allocation: 9.2,
    value: 149480,
    return: -3.5,
    risk: "Alto",
  },
  {
    name: "CDB Banco XYZ",
    type: "Renda Fixa",
    allocation: 15.8,
    value: 256820,
    return: 7.5,
    risk: "Baixo",
  },
]

export function AssetsTable() {
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
            {assets.map((asset) => (
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
