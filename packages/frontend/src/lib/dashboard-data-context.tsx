"use client"

import { createContext, useContext, useState, ReactNode, useEffect } from "react"

interface DashboardDataContextType {
  analysisResult: any
  setAnalysisResult: (data: any) => void
  clearAnalysisResult: () => void
}

const DashboardDataContext = createContext<DashboardDataContextType | undefined>(
  undefined
)

const STORAGE_KEY = "portfolio_analysis_result"

export function DashboardDataProvider({ children }: { children: ReactNode }) {
  const [analysisResult, setAnalysisResultState] = useState<any>(null)
  const [isHydrated, setIsHydrated] = useState(false)

  // Carregar dados do localStorage na inicialização
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        console.log("[DashboardData] Loaded from localStorage:", parsed)
        setAnalysisResultState(parsed)
      }
    } catch (e) {
      console.error("[DashboardData] Error loading from localStorage:", e)
    }
    setIsHydrated(true)
  }, [])

  // Função para salvar dados
  const setAnalysisResult = (data: any) => {
    console.log("[DashboardData] Setting analysis result:", data)
    setAnalysisResultState(data)
    try {
      if (data) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
        console.log("[DashboardData] Saved to localStorage")
      } else {
        localStorage.removeItem(STORAGE_KEY)
      }
    } catch (e) {
      console.error("[DashboardData] Error saving to localStorage:", e)
    }
  }

  // Função para limpar dados
  const clearAnalysisResult = () => {
    setAnalysisResultState(null)
    localStorage.removeItem(STORAGE_KEY)
  }

  return (
    <DashboardDataContext.Provider value={{ analysisResult, setAnalysisResult, clearAnalysisResult }}>
      {children}
    </DashboardDataContext.Provider>
  )
}

export function useDashboardData() {
  const context = useContext(DashboardDataContext)
  if (context === undefined) {
    throw new Error("useDashboardData must be used within a DashboardDataProvider")
  }
  return context
}
