# Plataforma de Análise de Investimentos

Uma plataforma full-stack para análise de risco, otimização de portfólio e análise técnica de investimentos.

## ✨ Novidades

### 🎨 Versão 1.10.0 - Design System "Geometric STEM" (Dez 2025)

- ✨ **Visual Overhaul**: Nova identidade visual com conceito "Portfolio Canvas"
- 🎨 **Paleta Vibrante**: Cores de alto contraste e fundo "Graph Paper"
- 📐 **UI Moderna**: Componentes arredondados, cards flutuantes e animações
- 📊 **Gráficos High-Fidelity**: Visualizações aprimoradas com Framer Motion
- 🚀 **Performance**: Stack modernizada com React Query

### 📊 Versão 0.8.0 - Correções de Gráficos (Dez 2025)

- 📈 **Gráfico de Alocação corrigido**: Evolução percentual agora preenche de 0% a 100%
- 🔢 **Normalização robusta**: Soma exata = 1 para evitar erros de ponto flutuante
- ⏱️ **Timeout aumentado**: 30s → 120s para portfólios maiores
- 🎨 **Scroll bar padronizado**: Brush consistente em gráficos temporais

### 💰 Versão 0.7.0 - Melhorias na Página de Operações (Dez 2025)

- 💰 **Formatação de moeda brasileira**: R$ 100.000,00 com separadores corretos
- 🎯 **Sistema de erros tipados**: validation, network, server, unknown
- ⏱️ **Timeout de requisição**: AbortController com 60s

### 📊 Versão 1.7.0 / 0.6.0 - 6 Novas Análises Avançadas

Novos componentes de análise profissional para gestão de portfólio:

| Análise | Descrição |
|---------|-----------|
| **CAPM** | Alpha, Beta, Sharpe, Treynor e R² por ativo |
| **Markowitz** | Fronteira eficiente com portfólios ótimos |
| **Fama-French** | Exposição aos 3 fatores (MKT, SMB, HML) |
| **VaR Backtest** | Validação do modelo com zonas Basel |
| **Risk Attribution** | MCR e contribuição ao risco por ativo |
| **Incremental VaR** | Impacto marginal de cada ativo no VaR |

Também incluído:
- 🎯 **Monte Carlo com 100k simulações** para distribuição mais suave
- 📚 **Legendas explicativas** em todos os gráficos técnicos
- 🎨 **UX otimizada para FHD 16:9** com container 1800px

### 🏗️ Versão 1.6.0 - Refatoração Arquitetural

O módulo `analysis.py` foi reorganizado de um arquivo monolítico (2242 linhas) em módulos especializados:

| Módulo | Responsabilidade |
|--------|------------------|
| `risk_metrics.py` | VaR, ES, Drawdown |
| `stress_testing.py` | Testes de estresse, backtesting |
| `covariance.py` | Matriz de covariância, atribuição de risco |
| `fama_french.py` | Modelos FF3 e FF5 |
| `risk_engine.py` | Orquestração de análises |
| `portfolio_analyzer.py` | Análise completa de portfólio |

### 💰 Versão 1.3.0 - Rendimento do CDI no Caixa

- 💰 **Dados Reais**: Integração com Banco Central do Brasil
- 📈 **Rendimento Diário**: Juros compostos aplicados dia-a-dia
- 🎯 **Realismo**: Portfólio reflete melhor a realidade do mercado
- 📊 **Exemplo**: R$ 90.000 em caixa por 1 ano = +R$ 12.285 de rendimento (CDI ~13,65% a.a.)

[📖 Saiba mais sobre a integração CDI](docs/developer-guide/architecture/cdi-integration.md)

## 📚 Documentação

A documentação completa deste projeto está disponível no diretório [`docs/`](docs/).

- **[Página Inicial da Documentação](docs/README.md)**
- **[Guia do Usuário](docs/user-guide/getting-started.md)**
- **[Guia do Desenvolvedor](docs/developer-guide/setup/local-development.md)**
- **[Guia Docker](README-DOCKER.md)** 🐳

## 🚀 Quick Start

### Com Docker (Recomendado)

```powershell
# Build e iniciar todos os serviços (backend + frontend + redis)
.\start-docker.ps1 build
.\start-docker.ps1 start

# Acessar:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Desenvolvimento Manual

```powershell
# Instalar dependências
.\install_deps.ps1

# Rodar o servidor (backend + frontend)
.\run_server.ps1
```

📖 **[Guia completo do Docker](README-DOCKER.md)**
