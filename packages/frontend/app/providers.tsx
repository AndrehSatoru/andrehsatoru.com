'use client'

import React from 'react'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '@/lib/api-hooks'
import { PeriodProvider } from '@/lib/period-context'
import { DashboardDataProvider } from '@/lib/dashboard-data-context'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <DashboardDataProvider>
        <PeriodProvider>
          {children}
        </PeriodProvider>
      </DashboardDataProvider>
    </QueryClientProvider>
  )
}
