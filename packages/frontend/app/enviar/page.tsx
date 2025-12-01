"use client"

import { useState, useEffect, useCallback } from "react"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { useRouter } from "next/navigation"
import Link from "next/link"

// Tipos de erro para melhor categorização
type ErrorType = "validation" | "network" | "server" | "unknown"

interface FormError {
  type: ErrorType
  message: string
  details?: string[]
}

type Operacao = {
  data: string
  ticker: string
  tipo: "compra" | "venda"
  valor: number | ""
}

type FormData = {
  valorInicial: string
  dataInicial: string
  operacoes: Operacao[]
}

const STORAGE_KEY = "enviar_operacoes_form"

function getStoredFormData(): FormData | null {
  if (typeof window === "undefined") return null
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (e) {
    console.error("Erro ao carregar dados salvos:", e)
  }
  return null
}

function saveFormData(data: FormData) {
  if (typeof window === "undefined") return
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  } catch (e) {
    console.error("Erro ao salvar dados:", e)
  }
}

function clearStoredFormData() {
  if (typeof window === "undefined") return
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (e) {
    console.error("Erro ao limpar dados:", e)
  }
}

function formatCurrency(value: number | string): string {
  const numValue = typeof value === "string" ? parseFloat(value) : value
  if (isNaN(numValue) || numValue === 0) return ""
  return numValue.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function parseCurrencyToNumber(value: string): number {
  if (!value) return 0
  // Remove "R$", espaços e pontos de milhar, troca vírgula por ponto
  const cleaned = value
    .replace(/R\$\s?/g, "")
    .replace(/\./g, "")
    .replace(",", ".")
    .trim()
  const parsed = parseFloat(cleaned)
  return isNaN(parsed) ? 0 : parsed
}

// Componente de input de moeda que permite digitação livre
function CurrencyInput({
  value,
  onChange,
  placeholder = "R$ 0,00",
  className = "",
}: {
  value: number | string
  onChange: (value: number | "") => void
  placeholder?: string
  className?: string
}) {
  const [displayValue, setDisplayValue] = useState<string>("")
  const [isFocused, setIsFocused] = useState(false)

  // Atualiza o valor exibido quando o valor externo muda (e não está focado)
  useEffect(() => {
    if (!isFocused) {
      const numValue = typeof value === "string" ? parseFloat(value) : value
      if (isNaN(numValue) || numValue === 0 || value === "") {
        setDisplayValue("")
      } else {
        setDisplayValue(formatCurrency(numValue))
      }
    }
  }, [value, isFocused])

  const handleFocus = () => {
    setIsFocused(true)
    // Ao focar, mostra o valor numérico puro para fácil edição
    const numValue = typeof value === "string" ? parseFloat(value) : value
    if (!isNaN(numValue) && numValue !== 0) {
      setDisplayValue(numValue.toString().replace(".", ","))
    } else {
      setDisplayValue("")
    }
  }

  const handleBlur = () => {
    setIsFocused(false)
    // Ao sair do campo, parseia e formata
    const parsed = parseCurrencyToNumber(displayValue)
    if (parsed > 0) {
      setDisplayValue(formatCurrency(parsed))
      onChange(parsed)
    } else {
      setDisplayValue("")
      onChange("")
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = e.target.value
    // Permite apenas números, vírgula e ponto
    const sanitized = rawValue.replace(/[^0-9,.]/g, "")
    setDisplayValue(sanitized)
  }

  return (
    <input
      type="text"
      value={displayValue}
      onChange={handleChange}
      onFocus={handleFocus}
      onBlur={handleBlur}
      className={className}
      placeholder={placeholder}
    />
  )
}

export default function EnviarOperacoesPage() {
  const [valorInicial, setValorInicial] = useState<string>("")
  const [dataInicial, setDataInicial] = useState<string>("")
  const [operacoes, setOperacoes] = useState<Operacao[]>([
    { data: "", ticker: "", tipo: "compra", valor: "" },
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<FormError | null>(null)
  const [isHydrated, setIsHydrated] = useState(false)
  const { setAnalysisResult } = useDashboardData()
  const router = useRouter()

  // Helper para criar erros de validação
  const createValidationError = (message: string, details?: string[]): FormError => ({
    type: "validation",
    message,
    details,
  })

  // Helper para criar erros de rede
  const createNetworkError = (message: string): FormError => ({
    type: "network",
    message,
  })

  // Helper para criar erros de servidor
  const createServerError = (message: string, details?: string[]): FormError => ({
    type: "server",
    message,
    details,
  })

  // Carregar dados salvos do localStorage na inicialização
  useEffect(() => {
    const stored = getStoredFormData()
    if (stored) {
      setValorInicial(stored.valorInicial)
      setDataInicial(stored.dataInicial)
      if (stored.operacoes && stored.operacoes.length > 0) {
        setOperacoes(stored.operacoes)
      }
    }
    setIsHydrated(true)
  }, [])

  // Salvar dados no localStorage sempre que mudarem
  useEffect(() => {
    if (!isHydrated) return
    saveFormData({ valorInicial, dataInicial, operacoes })
  }, [valorInicial, dataInicial, operacoes, isHydrated])

  // Função para limpar todo o formulário
  const clearForm = useCallback(() => {
    setValorInicial("")
    setDataInicial("")
    setOperacoes([{ data: "", ticker: "", tipo: "compra", valor: "" }])
    clearStoredFormData()
    setError(null)
  }, [])

  function addOperacao() {
    setOperacoes((ops) => [...ops, { data: "", ticker: "", tipo: "compra", valor: "" }])
  }

  function removeOperacao(index: number) {
    setOperacoes((ops) => ops.filter((_, i) => i !== index))
  }

  function updateOperacao<K extends keyof Operacao>(index: number, key: K, value: Operacao[K]) {
    setOperacoes((ops) => {
      const copy = [...ops]
      copy[index] = { ...copy[index], [key]: value }
      return copy
    })
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    // Validações detalhadas
    const validationErrors: string[] = []

    // Validar data inicial
    if (!dataInicial) {
      validationErrors.push("Data inicial é obrigatória")
    } else {
      const dataInicialDate = new Date(dataInicial)
      const hoje = new Date()
      if (isNaN(dataInicialDate.getTime())) {
        validationErrors.push("Data inicial inválida")
      } else if (dataInicialDate > hoje) {
        validationErrors.push("Data inicial não pode ser no futuro")
      }
    }

    // Validar operações
    if (operacoes.length === 0) {
      validationErrors.push("Inclua ao menos uma operação")
    } else {
      operacoes.forEach((op, index) => {
        const opNum = index + 1
        if (!op.data) {
          validationErrors.push(`Operação ${opNum}: Data é obrigatória`)
        } else {
          const opDate = new Date(op.data)
          if (isNaN(opDate.getTime())) {
            validationErrors.push(`Operação ${opNum}: Data inválida`)
          } else if (dataInicial && opDate < new Date(dataInicial)) {
            validationErrors.push(`Operação ${opNum}: Data não pode ser anterior à data inicial`)
          }
        }
        if (!op.ticker || op.ticker.trim().length === 0) {
          validationErrors.push(`Operação ${opNum}: Ticker é obrigatório`)
        } else if (!/^[A-Z0-9]{4,6}$/.test(op.ticker.trim())) {
          validationErrors.push(`Operação ${opNum}: Ticker "${op.ticker}" parece inválido (ex: PETR4, VALE3)`)
        }
        if (op.valor === "" || op.valor === 0) {
          validationErrors.push(`Operação ${opNum}: Valor é obrigatório e deve ser maior que zero`)
        } else if (typeof op.valor === "number" && op.valor < 0) {
          validationErrors.push(`Operação ${opNum}: Valor não pode ser negativo`)
        }
      })
    }

    // Se houver erros de validação, exibir todos
    if (validationErrors.length > 0) {
      setError(createValidationError(
        validationErrors.length === 1 
          ? validationErrors[0] 
          : "Corrija os seguintes erros:",
        validationErrors.length > 1 ? validationErrors : undefined
      ))
      return
    }

    const payload = {
      valorInicial: valorInicial === "" ? 0 : Number(valorInicial),
      dataInicial,
      operacoes: operacoes.map((op) => ({
        data: op.data,
        ticker: op.ticker.trim(),
        tipo: op.tipo,
        valor: op.valor === "" ? 0 : Number(op.valor),
      })),
    }

    setLoading(true)
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 60000) // 60s timeout

      const resp = await fetch("/api/enviar-operacoes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      // Tentar parsear resposta JSON
      let data: any = {}
      try {
        const text = await resp.text()
        if (text) {
          data = JSON.parse(text)
        }
      } catch (parseError) {
        console.error("Erro ao parsear resposta:", parseError)
      }

      if (!resp.ok) {
        // Tratar diferentes códigos de status
        switch (resp.status) {
          case 400:
            setError(createValidationError(
              data?.message || "Dados inválidos enviados ao servidor",
              data?.errors ? Object.values(data.errors).flat() as string[] : undefined
            ))
            break
          case 401:
          case 403:
            setError(createServerError("Acesso não autorizado. Faça login novamente."))
            break
          case 404:
            setError(createServerError("Serviço não encontrado. Verifique se o servidor está ativo."))
            break
          case 422:
            const zodErrors = data?.errors?.fieldErrors
            const errorMessages = zodErrors 
              ? Object.entries(zodErrors).map(([field, msgs]) => `${field}: ${(msgs as string[]).join(", ")}`)
              : undefined
            setError(createValidationError(
              data?.message || "Erro de validação no servidor",
              errorMessages
            ))
            break
          case 500:
            setError(createServerError(
              "Erro interno do servidor. Tente novamente em alguns minutos.",
              data?.detail ? [data.detail] : undefined
            ))
            break
          case 502:
          case 503:
          case 504:
            setError(createServerError(
              "Servidor temporariamente indisponível. Tente novamente em alguns minutos."
            ))
            break
          default:
            setError(createServerError(
              data?.message || `Erro inesperado (código ${resp.status})`
            ))
        }
        return
      }

      // Sucesso
      setAnalysisResult(data)
      router.push("/")

    } catch (err: unknown) {
      // Tratar diferentes tipos de erro
      if (err instanceof Error) {
        if (err.name === "AbortError") {
          setError(createNetworkError(
            "A requisição demorou muito e foi cancelada. Verifique sua conexão e tente novamente."
          ))
        } else if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
          setError(createNetworkError(
            "Não foi possível conectar ao servidor. Verifique sua conexão com a internet."
          ))
        } else if (err.message.includes("CORS")) {
          setError(createNetworkError(
            "Erro de configuração do servidor (CORS). Contate o suporte."
          ))
        } else {
          setError({
            type: "unknown",
            message: "Ocorreu um erro inesperado",
            details: [err.message],
          })
        }
      } else {
        setError({
          type: "unknown",
          message: "Ocorreu um erro desconhecido. Tente novamente.",
        })
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-6">
        <h1 className="text-2xl font-semibold mb-6">Enviar Operações</h1>

        <form onSubmit={onSubmit} className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium mb-1">Valor inicial</label>
              <CurrencyInput
                value={valorInicial}
                onChange={(val) => setValorInicial(val === "" ? "" : String(val))}
                className="w-full rounded-md border px-3 py-2 bg-background"
                placeholder="R$ 0,00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Data inicial</label>
              <input
                type="date"
                value={dataInicial}
                onChange={(e) => setDataInicial(e.target.value)}
                className="w-full rounded-md border px-3 py-2 bg-background"
              />
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium">Operações</h2>
              <button
                type="button"
                onClick={addOperacao}
                className="rounded-md bg-primary text-primary-foreground px-3 py-1.5 text-sm"
              >
                Adicionar
              </button>
            </div>

            <div className="space-y-4">
              {operacoes.map((op, index) => (
                <div key={index} className="grid gap-3 sm:grid-cols-5 border rounded-md p-3">
                  <div>
                    <label className="block text-sm font-medium mb-1">Data</label>
                    <input
                      type="date"
                      value={op.data}
                      onChange={(e) => updateOperacao(index, "data", e.target.value)}
                      className="w-full rounded-md border px-3 py-2 bg-background"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Ticker</label>
                    <input
                      type="text"
                      value={op.ticker}
                      onChange={(e) => updateOperacao(index, "ticker", e.target.value.toUpperCase())}
                      className="w-full rounded-md border px-3 py-2 bg-background"
                      placeholder="PETR4"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Tipo</label>
                    <select
                      value={op.tipo}
                      onChange={(e) => updateOperacao(index, "tipo", e.target.value as Operacao["tipo"])}
                      className="w-full rounded-md border px-3 py-2 bg-background"
                    >
                      <option value="compra">Compra</option>
                      <option value="venda">Venda</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Valor</label>
                    <CurrencyInput
                      value={op.valor}
                      onChange={(val) => updateOperacao(index, "valor", val)}
                      className="w-full rounded-md border px-3 py-2 bg-background"
                      placeholder="R$ 0,00"
                    />
                  </div>

                  <div className="flex items-end">
                    <button
                      type="button"
                      onClick={() => removeOperacao(index)}
                      className="w-full rounded-md border px-3 py-2 text-sm"
                      disabled={operacoes.length <= 1}
                    >
                      Remover
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {error && (
            <div className={`rounded-md border px-4 py-3 text-sm ${
              error.type === "validation" 
                ? "border-yellow-300 bg-yellow-50 text-yellow-800 dark:border-yellow-700 dark:bg-yellow-950 dark:text-yellow-200"
                : error.type === "network"
                ? "border-orange-300 bg-orange-50 text-orange-800 dark:border-orange-700 dark:bg-orange-950 dark:text-orange-200"
                : "border-red-300 bg-red-50 text-red-700 dark:border-red-700 dark:bg-red-950 dark:text-red-200"
            }`}>
              <div className="flex items-start gap-2">
                <span className="flex-shrink-0 mt-0.5">
                  {error.type === "validation" && "⚠️"}
                  {error.type === "network" && "🌐"}
                  {error.type === "server" && "🔧"}
                  {error.type === "unknown" && "❌"}
                </span>
                <div className="flex-1">
                  <p className="font-medium">{error.message}</p>
                  {error.details && error.details.length > 0 && (
                    <ul className="mt-2 list-disc list-inside space-y-1 text-sm opacity-90">
                      {error.details.map((detail, idx) => (
                        <li key={idx}>{detail}</li>
                      ))}
                    </ul>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => setError(null)}
                  className="flex-shrink-0 text-current opacity-60 hover:opacity-100"
                  aria-label="Fechar mensagem de erro"
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading}
              className="rounded-md bg-primary text-primary-foreground px-4 py-2"
            >
              {loading ? "Enviando..." : "Enviar"}
            </button>
            <button
              type="button"
              onClick={clearForm}
              className="rounded-md border border-destructive text-destructive px-4 py-2 hover:bg-destructive hover:text-destructive-foreground transition-colors"
            >
              Limpar Tudo
            </button>
            <Link href="/" className="rounded-md border px-4 py-2 inline-flex items-center justify-center hover:bg-muted transition-colors">Voltar ao dashboard</Link>
          </div>
        </form>
      </div>
    </div>
  )
}
