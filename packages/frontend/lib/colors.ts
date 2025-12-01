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
  // Sucesso / Positivo / Ganho
  success: {
    DEFAULT: "#16a34a",  // verde-600
    light: "#22c55e",    // verde-500
    dark: "#15803d",     // verde-700
    bg: "#dcfce7",       // verde-100
  },
  
  // Erro / Negativo / Perda
  error: {
    DEFAULT: "#dc2626",  // vermelho-600
    light: "#ef4444",    // vermelho-500
    dark: "#b91c1c",     // vermelho-700
    bg: "#fee2e2",       // vermelho-100
  },
  
  // Alerta / Atenção
  warning: {
    DEFAULT: "#ca8a04",  // amarelo-600
    light: "#eab308",    // amarelo-500
    dark: "#a16207",     // amarelo-700
    bg: "#fef9c3",       // amarelo-100
  },
  
  // Informação / Neutro
  info: {
    DEFAULT: "#2563eb",  // azul-600
    light: "#3b82f6",    // azul-500
    dark: "#1d4ed8",     // azul-700
    bg: "#dbeafe",       // azul-100
  },
  
  // Neutro / Referência
  neutral: {
    DEFAULT: "#6b7280",  // cinza-500
    light: "#9ca3af",    // cinza-400
    dark: "#4b5563",     // cinza-600
    bg: "#f3f4f6",       // cinza-100
  },
} as const

// ============================================
// CORES PARA GRÁFICOS (paleta de 10 cores distintas)
// ============================================

export const CHART_COLORS = [
  "#16a34a", // verde (portfólio principal)
  "#2563eb", // azul
  "#dc2626", // vermelho
  "#ca8a04", // amarelo escuro
  "#9333ea", // roxo
  "#0891b2", // ciano
  "#ea580c", // laranja
  "#64748b", // cinza ardósia
  "#be185d", // rosa
  "#059669", // verde esmeralda
  "#7c3aed", // violeta
  "#0d9488", // teal
] as const

// ============================================
// CORES ESPECÍFICAS DO DASHBOARD
// ============================================

export const DASHBOARD_COLORS = {
  // Gráfico de Performance
  portfolio: "#16a34a",      // verde para portfólio
  benchmark: "#6b7280",      // cinza para benchmark
  
  // Métricas de risco
  volatility: "#f59e0b",     // âmbar
  sharpe: "#8b5cf6",         // violeta
  var: "#ef4444",            // vermelho
  drawdown: "#dc2626",       // vermelho escuro
  
  // Alocação
  cash: "#94a3b8",           // cinza claro para caixa
  equity: "#3b82f6",         // azul para ações
  fixedIncome: "#22c55e",    // verde para renda fixa
  
  // Comparativos
  positive: "#16a34a",       // verde para ganhos
  negative: "#dc2626",       // vermelho para perdas
  neutral: "#6b7280",        // cinza para neutro
} as const

// ============================================
// CORES PARA GRADIENTES
// ============================================

export const GRADIENT_COLORS = {
  portfolio: {
    start: "#16a34a",
    startOpacity: 0.3,
    end: "#16a34a",
    endOpacity: 0.05,
  },
  benchmark: {
    start: "#6b7280",
    startOpacity: 0.2,
    end: "#6b7280",
    endOpacity: 0.02,
  },
  positive: {
    start: "#22c55e",
    startOpacity: 0.3,
    end: "#22c55e",
    endOpacity: 0.05,
  },
  negative: {
    start: "#ef4444",
    startOpacity: 0.3,
    end: "#ef4444",
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
