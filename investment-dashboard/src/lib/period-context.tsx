// src/lib/period-context.tsx
"use client";

import React, { createContext, useState, useContext, ReactNode } from 'react';

// Define a estrutura do que será compartilhado pelo contexto
interface PeriodContextType {
  period: string; // Ex: '1M', '6M', '1Y'
  setPeriod: (period: string) => void;
}

// Cria o contexto
const PeriodContext = createContext<PeriodContextType | undefined>(undefined);

// Cria o componente Provedor
export function PeriodProvider({ children }: { children: ReactNode }) {
  const [period, setPeriod] = useState('1Y'); // Define '1 Ano' como o período padrão

  return (
    <PeriodContext.Provider value={{ period, setPeriod }}>
      {children}
    </PeriodContext.Provider>
  );
}

// Cria um hook customizado para usar o contexto facilmente nos componentes
export function usePeriod() {
  const context = useContext(PeriodContext);
  if (context === undefined) {
    throw new Error('usePeriod must be used within a PeriodProvider');
  }
  return context;
}

// Você também tentou importar `filterDataByPeriod`.
// Adicione essa função utilitária aqui também.
// (Esta é uma função de exemplo, ajuste a lógica conforme seus dados)
export const filterDataByPeriod = (data: any[], period: string) => {
  // Lógica de filtro aqui...
  console.log(`Filtrando dados para o período: ${period}`);
  return data; // Por enquanto, apenas retorna os dados originais
};
