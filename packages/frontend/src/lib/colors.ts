/**
 * Padrão de Cores do Site - AndrehSatoru Portfolio
 * 
 * Este arquivo define todas as cores usadas no projeto para manter consistência.
 * Use estas constantes em vez de cores hardcoded.
 */

// ============================================
// CORES SEMÂNTICAS (para indicar status/estados)
// ============================================

export const SEMANTIC_COLORS = {
  // Sucesso / Positivo / Ganho (Emerald)
  success: {
    DEFAULT: "#10b981",  // emerald-500
    light: "#34d399",    // emerald-400
    dark: "#059669",     // emerald-600
    bg: "#d1fae5",       // emerald-100
  },
  
  // Erro / Negativo / Perda (Rose)
  error: {
    DEFAULT: "#f43f5e",  // rose-500
    light: "#fb7185",    // rose-400
    dark: "#e11d48",     // rose-600
    bg: "#ffe4e6",       // rose-100
  },
  
  // Alerta / Atenção (Yellow/Amber)
  warning: {
    DEFAULT: "#eab308",  // yellow-500
    light: "#facc15",    // yellow-400
    dark: "#ca8a04",     // yellow-600
    bg: "#fef9c3",       // yellow-100
  },
  
  // Informação / Neutro (Blue)
  info: {
    DEFAULT: "#2563eb",  // blue-600
    light: "#60a5fa",    // blue-400
    dark: "#1d4ed8",     // blue-700
    bg: "#dbeafe",       // blue-100
  },
  
  // Neutro / Referência
  neutral: {
    DEFAULT: "#6b7280",  // gray-500
    light: "#9ca3af",    // gray-400
    dark: "#4b5563",     // gray-600
    bg: "#f3f4f6",       // gray-100
  },
} as const

// ============================================
// CORES PARA GRÁFICOS (paleta de 10 cores distintas)
// ============================================

export const CHART_COLORS = [
  "#10b981", // Emerald (Portfolio)
  "#2563eb", // Blue
  "#f43f5e", // Rose
  "#eab308", // Yellow
  "#9333ea", // Purple
  "#06b6d4", // Cyan
  "#f97316", // Orange
  "#64748b", // Slate
  "#db2777", // Pink
  "#059669", // Dark Emerald
] as const

// ============================================
// CORES ESPECÍFICAS DO DASHBOARD
// ============================================

export const DASHBOARD_COLORS = {
  // Gráfico de Performance
  portfolio: "#10b981",      // emerald-500
  benchmark: "#6b7280",      // gray-500
  ibovespa: "#3b82f6",       // blue-500
  
  // Métricas de risco
  volatility: "#eab308",     // yellow-500
  sharpe: "#9333ea",         // purple-600
  var: "#f43f5e",            // rose-500
  drawdown: "#e11d48",       // rose-600
  
  // Alocação
  cash: "#94a3b8",           // slate-400
  equity: "#2563eb",         // blue-600
  fixedIncome: "#10b981",    // emerald-500
  
  // Comparativos
  positive: "#10b981",       // emerald-500
  negative: "#f43f5e",       // rose-500
  neutral: "#6b7280",        // gray-500
} as const

// ============================================
// CORES PARA GRADIENTES
// ============================================

export const GRADIENT_COLORS = {
  portfolio: {
    start: "#10b981",
    startOpacity: 0.3,
    end: "#10b981",
    endOpacity: 0.05,
  },
  benchmark: {
    start: "#6b7280",
    startOpacity: 0.2,
    end: "#6b7280",
    endOpacity: 0.02,
  },
  positive: {
    start: "#34d399",
    startOpacity: 0.3,
    end: "#34d399",
    endOpacity: 0.05,
  },
  negative: {
    start: "#fb7185",
    startOpacity: 0.3,
    end: "#fb7185",
    endOpacity: 0.05,
  },
} as const

// ============================================
// CORES PARA UI (backgrounds, borders, etc.)
// ============================================

export const UI_COLORS = {
  // Backgrounds
  cardBg: "#ffffff",
  cardBgHover: "#fafafa",
  tooltipBg: "#ffffff",
  brushBg: "#f5f5f5",
  
  // Borders
  border: "#e5e7eb",
  borderLight: "#f3f4f6",
  borderDark: "#d1d5db",
  
  // Text
  textPrimary: "#111827",
  textSecondary: "#6b7280",
  textMuted: "#9ca3af",
  
  // Shadows
  shadow: "rgba(0, 0, 0, 0.1)",
  shadowLight: "rgba(0, 0, 0, 0.05)",
} as const

// ============================================
// FUNÇÕES UTILITÁRIAS
// ============================================

/**
 * Retorna a cor apropriada baseada em um valor (positivo/negativo)
 */
export function getValueColor(value: number): string {
  if (value > 0) return SEMANTIC_COLORS.success.DEFAULT
  if (value < 0) return SEMANTIC_COLORS.error.DEFAULT
  return SEMANTIC_COLORS.neutral.DEFAULT
}

/**
 * Retorna a cor de background apropriada baseada em um valor
 */
export function getValueBgColor(value: number): string {
  if (value > 0) return SEMANTIC_COLORS.success.bg
  if (value < 0) return SEMANTIC_COLORS.error.bg
  return SEMANTIC_COLORS.neutral.bg
}

/**
 * Retorna uma cor do array de cores para gráficos baseado no índice
 */
export function getChartColor(index: number): string {
  return CHART_COLORS[index % CHART_COLORS.length]
}

/**
 * Retorna cor baseada em classificação de risco
 */
export function getRiskColor(riskLevel: 'low' | 'medium' | 'high' | 'extreme'): string {
  switch (riskLevel) {
    case 'low': return SEMANTIC_COLORS.success.DEFAULT
    case 'medium': return SEMANTIC_COLORS.warning.DEFAULT
    case 'high': return SEMANTIC_COLORS.error.light
    case 'extreme': return SEMANTIC_COLORS.error.dark
    default: return SEMANTIC_COLORS.neutral.DEFAULT
  }
}

/**
 * Retorna cor baseada no Sharpe Ratio
 */
export function getSharpeColor(sharpe: number): string {
  if (sharpe >= 1.5) return SEMANTIC_COLORS.success.DEFAULT
  if (sharpe >= 1) return SEMANTIC_COLORS.success.light
  if (sharpe >= 0.5) return SEMANTIC_COLORS.warning.DEFAULT
  if (sharpe >= 0) return SEMANTIC_COLORS.warning.dark
  return SEMANTIC_COLORS.error.DEFAULT
}

/**
 * Retorna cor baseada na volatilidade
 */
export function getVolatilityColor(volatility: number): string {
  if (volatility <= 10) return SEMANTIC_COLORS.success.DEFAULT
  if (volatility <= 20) return SEMANTIC_COLORS.warning.light
  if (volatility <= 30) return SEMANTIC_COLORS.warning.DEFAULT
  return SEMANTIC_COLORS.error.DEFAULT
}
