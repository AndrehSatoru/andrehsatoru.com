"use client"

import { createContext, useContext, useState, ReactNode } from "react"

interface DashboardDataContextType {
  analysisResult: any
  setAnalysisResult: (data: any) => void
}

const DashboardDataContext = createContext<DashboardDataContextType | undefined>(
  undefined
)

export function DashboardDataProvider({ children }: { children: ReactNode }) {
  const [analysisResult, setAnalysisResult] = useState<any>(null)

  return (
    <DashboardDataContext.Provider value={{ analysisResult, setAnalysisResult }}>
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
