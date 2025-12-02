# Documentação da Plataforma de Análise de Investimentos

Bem-vindo à documentação oficial da Plataforma de Análise de Investimentos. Aqui você encontrará todas as informações necessárias para utilizar, desenvolver e operar a plataforma.

> 🗺️ **[Mapa da Documentação](SITEMAP.md)** - Encontre rapidamente o que você precisa!

## 📚 Estrutura da Documentação

A documentação está organizada em três guias principais, dependendo do seu perfil e objetivo:

### 👥 [Guia do Usuário](user-guide/getting-started.md)
Ideal para investidores e usuários finais da plataforma.
- **[Primeiros Passos](user-guide/getting-started.md):** Visão geral das funcionalidades e como começar.
- **Funcionalidades:** Detalhes sobre Análise de Risco, Otimização de Portfólio e Visualizações.
- **Tutoriais:** Guias passo-a-passo para realizar análises específicas.

### 👨‍💻 [Guia do Desenvolvedor](developer-guide/setup/local-development.md)
Para desenvolvedores que desejam contribuir com o código ou entender a arquitetura.
- **[Setup e Instalação](developer-guide/setup/local-development.md):** Como configurar o ambiente de desenvolvimento local.
- **[Arquitetura](developer-guide/architecture/overview.md):** Visão geral técnica, arquitetura backend e frontend.
- **[API](developer-guide/api/quickstart.md):** Documentação dos endpoints, autenticação e exemplos de uso.
- **[Deploy com Docker](developer-guide/deployment/docker-compose.md):** 🐳 Guia técnico de Docker Compose.
- **[Guia Docker Usuário](../README-DOCKER.md):** Guia completo de uso do Docker Compose.

### ⚙️ [Guia de Operações](operations/deployment.md)
Para engenheiros de DevOps e administradores de sistema.
- **[Deploy](operations/deployment.md):** Como fazer o deploy da aplicação em produção.
- **[Docker Compose](developer-guide/deployment/docker-compose.md):** Deploy e configuração com Docker.
- **[Guia Docker Completo](../README-DOCKER.md):** Guia do usuário para Docker Compose.
- **[Segurança](operations/security.md):** Práticas e configurações de segurança.

---

## 🚀 Links Rápidos

- **Repositório:** [GitHub](https://github.com/AndrehSatoru/andrehsatoru.com)
- **Issues:** [Reportar um problema](https://github.com/AndrehSatoru/andrehsatoru.com/issues)

---

## ✨ Novidades Recentes

### 💰 Melhorias na Página de Operações (v0.7.0 - Dez 2025)
- **Formatação de moeda brasileira**: Valores exibidos no formato R$ 100.000,00 com separadores corretos
- **Componente CurrencyInput**: Input inteligente que permite digitação livre e formata ao sair do campo
- **Tipos Compra/Venda capitalizados**: Labels exibidos como "Compra" e "Venda" (iniciais maiúsculas)
- **Exception handling robusto**: Sistema de erros tipados (validation, network, server, unknown)
- **Validações detalhadas**: Mensagens específicas por operação com erros listados
- **Tratamento HTTP completo**: Códigos 400, 401, 403, 404, 422, 500, 502, 503, 504 tratados
- **Timeout de requisição**: AbortController com 60s de timeout
- **UI de erros melhorada**: Cores por tipo, ícones, lista de detalhes e suporte dark mode
- **Navegação corrigida**: Botão "Voltar ao dashboard" usando Link do Next.js

### 📊 6 Novas Análises Avançadas (v1.7.0 / v0.6.0 - Nov 2025)
- **Análise CAPM**: Alpha, Beta, Sharpe, Treynor e R² por ativo com gráfico scatter
- **Otimização Markowitz**: Fronteira eficiente com 3 portfólios ótimos e pesos sugeridos
- **Fama-French 3 Fatores**: Exposição a MKT, SMB (tamanho) e HML (valor)
- **VaR Backtest**: Validação do modelo com teste de Kupiec e zonas Basel
- **Risk Attribution Detalhada**: MCR, contribuição ao risco e benefício de diversificação
- **Incremental VaR (IVaR)**: Impacto marginal de cada ativo no VaR do portfólio

### 🎯 Simulação Monte Carlo Aprimorada (v1.7.0 - Nov 2025)
- **100.000 simulações**: Distribuição mais suave e precisa
- **Fórmula MGB corrigida**: Drift calculado corretamente
- **Legendas explicativas**: Descrição dos métodos MGB e Bootstrap

### 🎨 Melhorias de UX para FHD (v0.6.0 - Nov 2025)
- **Container 1800px**: Melhor uso do espaço em telas grandes
- **Header sticky**: Navegação fixa ao rolar
- **Scrollbar visível**: Barra de rolagem sempre presente
- **Legendas em todos os gráficos técnicos**: Explicações detalhadas

### 🏗️ Refatoração Arquitetural (v1.6.0 - Nov 2025)
- **Módulos especializados**: `analysis.py` (2242 linhas) reorganizado em 7 módulos focados
- **Melhor manutenibilidade**: Cada módulo com responsabilidade única (SRP)
- **Backward compatibility**: Entry point mantido para compatibilidade
- **Novos módulos**: `risk_metrics.py`, `stress_testing.py`, `covariance.py`, `fama_french.py`, `risk_engine.py`, `portfolio_analyzer.py`

### 📊 Testes de Estresse Reais (v1.6.0 - Nov 2025)
- **Cenários históricos**: Crise 2008, COVID-19, Crise Subprime
- **Cenários hipotéticos**: Choque de taxa, recessão global, crise cambial
- **Impacto personalizado**: Baseado na volatilidade e correlação do portfólio

### 💵 Dividendos e Proventos (v1.4.0 - Nov 2025)
- **Dividendos automáticos**: Sistema busca e contabiliza dividendos de todas as ações
- **API Yahoo Finance direta**: Integração robusta para busca de proventos
- **Adição automática ao caixa**: Dividendos são creditados na data ex-dividend
- **Atualização dinâmica**: Saldo de caixa reflete CDI + dividendos recebidos
- **Cálculo de CDI corrigido**: Taxa CDI agora aplicada apenas em dias úteis (sem inflação)

### 💰 Rendimento do CDI no Caixa (Nov 2025)
- **Caixa rende CDI automaticamente**: Valor não investido agora gera retorno diário baseado no CDI
- **Dados reais do BCB**: Integração com Banco Central do Brasil para taxas CDI históricas
- **Cálculo preciso**: Rendimento composto aplicado dia-a-dia sobre o saldo disponível
- **Taxa livre de risco**: Implementação completa para análises Fama-French com fonte SELIC
- **Realismo financeiro**: Portfólio reflete melhor a realidade onde dinheiro parado rende juros

### 🐳 Docker Compose Integrado (Nov 2025)
- **Deploy simplificado** com backend, frontend e Redis em containers
- **Networking interno** otimizado para comunicação entre serviços
- **Variáveis de ambiente** configuradas automaticamente
- **Health checks** integrados para todos os serviços
- **Script PowerShell** para gerenciamento facilitado

### 📊 Análise de Portfólio com Cotações Reais (Nov 2025)
- **Busca automática** de cotações históricas via YFinance
- **Cálculo preciso** de quantidade de ações baseado em valor investido
- **Integração completa** entre frontend e backend
- **Processamento em tempo real** de operações financeiras

---

## 🛠️ Tecnologias Principais

| Categoria | Tecnologia |
| :--- | :--- |
| **Monorepo** | [pnpm](https://pnpm.io/) Workspaces |
| **Frontend** | [Next.js 15](https://nextjs.org/), [React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/), [Zodios](https://www.zodios.org/) |
| **Backend** | [Python 3.11](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://docs.pydantic.dev/), [YFinance](https://github.com/ranaroussi/yfinance) |
| **Cache** | [Redis 7](https://redis.io/) |
| **Infraestrutura**| [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) |
