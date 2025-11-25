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
