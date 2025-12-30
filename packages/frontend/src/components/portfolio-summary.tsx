"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { motion } from "framer-motion"
import { useRefreshAnimation } from "@/hooks/use-refresh-animation"
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  TrendingUp, 
  TrendingDown,
  Shield,
  Target,
  PieChart,
  Lightbulb,
  BarChart3,
  Clock,
  Wallet,
  ArrowUpRight,
  ArrowDownRight,
  Info
} from "lucide-react"

type InsightType = "success" | "warning" | "error" | "info"

interface Insight {
  type: InsightType
  message: string
  icon: React.ElementType
}

interface PortfolioProfile {
  name: string
  description: string
  color: string
}

export function PortfolioSummary() {
  const { analysisResult } = useDashboardData()

  const desempenho = analysisResult?.desempenho || {}
  const alocacao = analysisResult?.alocacao || {}

  // Métricas principais
  const retornoTotal = desempenho["retorno_total_%"] || 0
  const retornoAnualizado = desempenho["retorno_anualizado_%"] || 0
  const volatilidade = desempenho["volatilidade_anual_%"] || 0
  const sharpe = desempenho["indice_sharpe"] || 0
  const maxDrawdown = desempenho["max_drawdown_%"] || 0
  const var95 = desempenho["var_95%_1d_%"] || 0
  const diasAnalisados = desempenho["dias_analisados"] || 0
  const valorTotal = alocacao?.valor_total || 0

  // Animation hooks
  const valorTotalControls = useRefreshAnimation(valorTotal)
  const retornoTotalControls = useRefreshAnimation(retornoTotal)
  const sharpeControls = useRefreshAnimation(sharpe)
  const diasControls = useRefreshAnimation(diasAnalisados)

  // Calcular maior posição
  const alocacaoAtivos = alocacao?.alocacao || {}
  const posicoes = Object.entries(alocacaoAtivos).map(([ticker, info]: [string, any]) => ({
    ticker,
    percentual: info?.percentual || 0
  })).sort((a, b) => b.percentual - a.percentual)
  
  const maiorPosicao = posicoes[0] || { ticker: "N/A", percentual: 0 }
  const concentracao = maiorPosicao.percentual

  // Determinar perfil da carteira
  const getPortfolioProfile = (): PortfolioProfile => {
    if (volatilidade > 25 || concentracao > 30) {
      return {
        name: "Agressivo",
        description: "Alto risco, potencial de retorno elevado",
        color: "text-red-500"
      }
    } else if (volatilidade > 15 || concentracao > 20) {
      return {
        name: "Moderado",
        description: "Equilíbrio entre risco e retorno",
        color: "text-yellow-500"
      }
    } else if (volatilidade > 8) {
      return {
        name: "Balanceado",
        description: "Diversificação adequada",
        color: "text-blue-500"
      }
    } else {
      return {
        name: "Conservador",
        description: "Baixo risco, retorno estável",
        color: "text-green-500"
      }
    }
  }

  // Gerar insights dinâmicos
  const generateInsights = (): Insight[] => {
    const insights: Insight[] = []

    // Análise de retorno
    if (retornoTotal > 100) {
      insights.push({
        type: "success",
        message: `Retorno excepcional de ${retornoTotal.toFixed(1)}% (${retornoAnualizado.toFixed(1)}% a.a.)`,
        icon: TrendingUp
      })
    } else if (retornoTotal > 50) {
      insights.push({
        type: "success",
        message: `Bom retorno de ${retornoTotal.toFixed(1)}% no período`,
        icon: TrendingUp
      })
    } else if (retornoTotal > 0) {
      insights.push({
        type: "info",
        message: `Retorno positivo de ${retornoTotal.toFixed(1)}%`,
        icon: TrendingUp
      })
    } else {
      insights.push({
        type: "error",
        message: `Retorno negativo de ${retornoTotal.toFixed(1)}% no período`,
        icon: TrendingDown
      })
    }

    // Análise de Sharpe
    if (sharpe >= 1.5) {
      insights.push({
        type: "success",
        message: `Sharpe Ratio excelente (${sharpe.toFixed(2)}) - retorno ajustado ao risco muito bom`,
        icon: Target
      })
    } else if (sharpe >= 1) {
      insights.push({
        type: "success",
        message: `Sharpe Ratio bom (${sharpe.toFixed(2)}) - retorno adequado para o risco`,
        icon: Target
      })
    } else if (sharpe >= 0.5) {
      insights.push({
        type: "warning",
        message: `Sharpe Ratio moderado (${sharpe.toFixed(2)}) - considere otimizar a relação risco/retorno`,
        icon: Target
      })
    } else if (sharpe > 0) {
      insights.push({
        type: "warning",
        message: `Sharpe Ratio baixo (${sharpe.toFixed(2)}) - retorno não compensa o risco`,
        icon: Target
      })
    } else {
      insights.push({
        type: "error",
        message: `Sharpe Ratio negativo (${sharpe.toFixed(2)}) - perdendo para ativo livre de risco`,
        icon: Target
      })
    }

    // Análise de Volatilidade
    if (volatilidade > 30) {
      insights.push({
        type: "error",
        message: `Volatilidade muito alta (${volatilidade.toFixed(1)}%) - oscilações extremas esperadas`,
        icon: BarChart3
      })
    } else if (volatilidade > 20) {
      insights.push({
        type: "warning",
        message: `Volatilidade alta (${volatilidade.toFixed(1)}%) - prepare-se para oscilações significativas`,
        icon: BarChart3
      })
    } else if (volatilidade > 10) {
      insights.push({
        type: "info",
        message: `Volatilidade moderada (${volatilidade.toFixed(1)}%)`,
        icon: BarChart3
      })
    } else {
      insights.push({
        type: "success",
        message: `Volatilidade baixa (${volatilidade.toFixed(1)}%) - carteira estável`,
        icon: BarChart3
      })
    }

    // Análise de Drawdown
    if (Math.abs(maxDrawdown) > 30) {
      insights.push({
        type: "error",
        message: `Drawdown máximo severo (${maxDrawdown.toFixed(1)}%) - queda acentuada do pico`,
        icon: TrendingDown
      })
    } else if (Math.abs(maxDrawdown) > 15) {
      insights.push({
        type: "warning",
        message: `Drawdown máximo de ${maxDrawdown.toFixed(1)}% - queda considerável do pico`,
        icon: TrendingDown
      })
    } else {
      insights.push({
        type: "success",
        message: `Drawdown máximo controlado (${maxDrawdown.toFixed(1)}%)`,
        icon: Shield
      })
    }

    // Análise de Concentração
    if (concentracao > 30) {
      insights.push({
        type: "warning",
        message: `Alta concentração em ${maiorPosicao.ticker} (${concentracao.toFixed(0)}%) - risco específico elevado`,
        icon: PieChart
      })
    } else if (concentracao > 20) {
      insights.push({
        type: "info",
        message: `Posição relevante em ${maiorPosicao.ticker} (${concentracao.toFixed(0)}%)`,
        icon: PieChart
      })
    } else {
      insights.push({
        type: "success",
        message: `Boa diversificação - maior posição é ${maiorPosicao.ticker} (${concentracao.toFixed(0)}%)`,
        icon: PieChart
      })
    }

    // VaR em valor monetário
    if (valorTotal > 0) {
      const varMonetario = (Math.abs(var95) / 100) * valorTotal
      insights.push({
        type: "info",
        message: `VaR 95% (1 dia): Em um dia ruim, pode perder até R$ ${varMonetario.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`,
        icon: Shield
      })
    }

    return insights
  }

  // Gerar sugestões
  const generateSuggestions = (): string[] => {
    const suggestions: string[] = []

    if (concentracao > 25) {
      suggestions.push(`Considere reduzir a posição em ${maiorPosicao.ticker} para diminuir o risco específico`)
    }

    if (sharpe < 0.8 && volatilidade > 15) {
      suggestions.push("A relação risco-retorno pode ser melhorada com ativos de menor volatilidade")
    }

    if (Math.abs(maxDrawdown) > 20) {
      suggestions.push("Considere usar stop-loss para limitar perdas em quedas acentuadas")
    }

    // Verificar se há "Caixa" na carteira
    const caixa = alocacaoAtivos["Caixa"] || alocacaoAtivos["caixa"]
    if (caixa && caixa.percentual > 15) {
      suggestions.push(`${caixa.percentual.toFixed(0)}% em caixa pode estar rendendo abaixo do potencial`)
    }

    if (posicoes.length < 5) {
      suggestions.push("Carteira com poucos ativos - diversificação pode reduzir riscos")
    }

    return suggestions
  }

  const profile = getPortfolioProfile()
  const insights = generateInsights()
  const suggestions = generateSuggestions()

  const getInsightIcon = (type: InsightType) => {
    switch (type) {
      case "success": return CheckCircle2
      case "warning": return AlertTriangle
      case "error": return XCircle
      case "info": return Info
    }
  }

  const getInsightColor = (type: InsightType) => {
    switch (type) {
      case "success": return "text-green-500"
      case "warning": return "text-yellow-500"
      case "error": return "text-red-500"
      case "info": return "text-blue-500"
    }
  }

  const getInsightBgColor = (type: InsightType) => {
    switch (type) {
      case "success": return "bg-green-500/10"
      case "warning": return "bg-yellow-500/10"
      case "error": return "bg-red-500/10"
      case "info": return "bg-blue-500/10"
    }
  }

  if (!analysisResult) {
    return null
  }

  return (
    <Card className="border-border hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-foreground flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Resumo da Análise
            </CardTitle>
            <CardDescription className="text-muted-foreground">
              Visão geral do desempenho da sua carteira
            </CardDescription>
          </div>
          <div className="text-right">
            <div className={`text-lg font-bold ${profile.color}`}>
              Perfil {profile.name}
            </div>
            <div className="text-sm text-muted-foreground">
              {profile.description}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Métricas Principais em Destaque */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-muted rounded-lg">
          <motion.div animate={valorTotalControls} className="text-center p-2 rounded-xl">
            <div className="flex items-center justify-center gap-1 text-muted-foreground text-sm mb-1">
              <Wallet className="h-4 w-4" />
              Valor Total
            </div>
            <div className="text-xl font-bold">
              R$ {valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
            </div>
          </motion.div>
          <motion.div animate={retornoTotalControls} className="text-center p-2 rounded-xl">
            <div className="flex items-center justify-center gap-1 text-muted-foreground text-sm mb-1">
              {retornoTotal >= 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
              Retorno Total
            </div>
            <div className={`text-xl font-bold ${retornoTotal >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {retornoTotal >= 0 ? '+' : ''}{retornoTotal.toFixed(2)}%
            </div>
          </motion.div>
          <motion.div animate={sharpeControls} className="text-center p-2 rounded-xl">
            <div className="flex items-center justify-center gap-1 text-muted-foreground text-sm mb-1">
              <Target className="h-4 w-4" />
              Sharpe Ratio
            </div>
            <div className="text-xl font-bold">
              {sharpe.toFixed(2)}
            </div>
          </motion.div>
          <motion.div animate={diasControls} className="text-center p-2 rounded-xl">
            <div className="flex items-center justify-center gap-1 text-muted-foreground text-sm mb-1">
              <Clock className="h-4 w-4" />
              Período
            </div>
            <div className="text-xl font-bold">
              {diasAnalisados} dias
            </div>
          </motion.div>
        </div>

        {/* Insights */}
        <div className="space-y-3">
          <h3 className="font-semibold text-foreground flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            Análise Detalhada
          </h3>
          <div className="space-y-2">
            {insights.map((insight, index) => {
              const IconComponent = insight.icon
              return (
                <div 
                  key={index} 
                  className={`flex items-start gap-3 p-3 rounded-lg ${getInsightBgColor(insight.type)}`}
                >
                  <IconComponent className={`h-5 w-5 mt-0.5 flex-shrink-0 ${getInsightColor(insight.type)}`} />
                  <span className="text-sm text-foreground">{insight.message}</span>
                </div>
              )
            })}
          </div>
        </div>

        {/* Sugestões */}
        {suggestions.length > 0 && (
          <div className="space-y-3">
            <h3 className="font-semibold text-foreground flex items-center gap-2">
              <Lightbulb className="h-4 w-4" />
              Sugestões
            </h3>
            <div className="space-y-2">
              {suggestions.map((suggestion, index) => (
                <div 
                  key={index} 
                  className="flex items-start gap-3 p-3 rounded-lg bg-primary/5 border border-primary/20"
                >
                  <Lightbulb className="h-5 w-5 mt-0.5 flex-shrink-0 text-primary" />
                  <span className="text-sm text-foreground">{suggestion}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

