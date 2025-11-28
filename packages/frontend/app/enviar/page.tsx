"use client"

import { useState, useEffect, useCallback } from "react"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { useRouter } from "next/navigation"

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

export default function EnviarOperacoesPage() {
  const [valorInicial, setValorInicial] = useState<string>("")
  const [dataInicial, setDataInicial] = useState<string>("")
  const [operacoes, setOperacoes] = useState<Operacao[]>([
    { data: "", ticker: "", tipo: "compra", valor: "" },
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isHydrated, setIsHydrated] = useState(false)
  const { setAnalysisResult } = useDashboardData()
  const router = useRouter()

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

    // Validação mínima no client
    if (!dataInicial) {
      setError("Informe a data inicial")
      return
    }
    if (operacoes.length === 0) {
      setError("Inclua ao menos uma operação")
      return
    }
    for (const op of operacoes) {
      if (!op.data || !op.ticker || op.valor === "") {
        setError("Preencha todos os campos de todas as operações")
        return
      }
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
      const resp = await fetch("/api/enviar-operacoes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
      const data = await resp.json().catch(() => ({}))
      if (!resp.ok) {
        setError(data?.message || "Erro ao enviar")
      } else {
        setAnalysisResult(data)
        router.push("/")
      }
    } catch (err: any) {
      setError(String(err?.message || err))
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
              <input
                type="number"
                step="0.01"
                value={valorInicial}
                onChange={(e) => setValorInicial(e.target.value)}
                className="w-full rounded-md border px-3 py-2 bg-background"
                placeholder="0.00"
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
                      <option value="compra">compra</option>
                      <option value="venda">venda</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Valor</label>
                    <input
                      type="number"
                      step="0.01"
                      value={op.valor === "" ? "" : op.valor}
                      onChange={(e) => {
                        const v = e.target.value
                        updateOperacao(index, "valor", v === "" ? "" : parseFloat(v))
                      }}
                      className="w-full rounded-md border px-3 py-2 bg-background"
                      placeholder="0.00"
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
            <div className="rounded-md border border-red-300 bg-red-50 text-red-700 px-3 py-2 text-sm">
              {error}
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
            <a href="/" className="rounded-md border px-4 py-2">Voltar ao dashboard</a>
          </div>
        </form>
      </div>
    </div>
  )
}
