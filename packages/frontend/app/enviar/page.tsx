"use client"

import { useState } from "react"
import { useDashboardData } from "@/lib/dashboard-data-context"
import { useRouter } from "next/navigation"

type Operacao = {
  data: string
  ticker: string
  tipo: "compra" | "venda"
  valor: number | ""
}

export default function EnviarOperacoesPage() {
  const [valorInicial, setValorInicial] = useState<string>("")
  const [dataInicial, setDataInicial] = useState<string>("")
  const [operacoes, setOperacoes] = useState<Operacao[]>([
    { data: "", ticker: "", tipo: "compra", valor: "" },
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { setAnalysisResult } = useDashboardData()
  const router = useRouter()

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
            <a href="/" className="rounded-md border px-4 py-2">Voltar ao dashboard</a>
          </div>
        </form>
      </div>
    </div>
  )
}
