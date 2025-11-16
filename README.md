# Plataforma de Análise de Investimentos

Este projeto é uma plataforma completa para análise de investimentos, projetada para ajudar usuários a tomar decisões informadas sobre seus portfólios. A arquitetura é baseada em um monorepo que contém um backend robusto para processamento de dados e um frontend moderno e interativo para visualização.

## ✨ Funcionalidades Principais

-   **Análise de Portfólio:** Métricas completas de risco e retorno.
-   **Otimização de Fronteira Eficiente:** Encontre a alocação ótima de ativos.
-   **Visualizações Avançadas:** Matriz de correlação, contribuição de risco, rolling returns e mais.
-   **Simulação de Monte Carlo:** Projete possíveis resultados futuros do portfólio.
-   **Autenticação Segura:** Acesso protegido à plataforma.

## 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologia |
| :--- | :--- |
| **Monorepo** | [pnpm](https://pnpm.io/) |
| **Frontend** | [Next.js](https://nextjs.org/), [React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/), [Shadcn/UI](https://ui.shadcn.com/) |
| **Backend** | [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://docs.pydantic.dev/) |
| **Testes** | [Pytest](https://docs.pytest.org/) (Backend) |
| **Containerização**| [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) |
| **Integração** | [OpenAPI](https://www.openapis.org/), Geração de cliente API |

## 🚀 Como Começar (Ambiente Windows)

A forma mais simples de configurar o ambiente de desenvolvimento é usando os scripts PowerShell fornecidos.

1.  **Instale as Dependências:**
    Execute o script na raiz do projeto para instalar todas as dependências do frontend e backend.
    ```powershell
    .\install_deps.ps1
    ```

2.  **Execute os Servidores:**
    Abra um novo terminal e execute o script para iniciar o servidor do backend (FastAPI).
    ```powershell
    .\run_server.ps1
    ```
    *   O backend estará disponível em `http://localhost:8001`.
    *   Para o frontend, navegue até `packages/frontend` e rode `pnpm dev`. O frontend estará disponível em `http://localhost:3000`.

3.  **Gere o Cliente da API (se necessário):**
    Após qualquer alteração na API do backend, regenere o cliente TypeScript para o frontend:
    ```powershell
    # Navegue até a pasta do backend
    cd packages/backend

    # Execute o script de geração
    python .\scripts\generate_openapi.py
    ```

## Estrutura do Monorepo

O projeto está organizado como um monorepo, gerenciado por `pnpm`. Essa abordagem centraliza o gerenciamento de dependências e facilita a integração entre o frontend e o backend.

```
.
├── packages/
│   ├── backend/      # Projeto do Backend (Python/FastAPI)
│   ├── frontend/     # Projeto do Frontend (Next.js/React)
│   └── shared-types/ # Definições de tipos compartilhadas
└── pnpm-workspace.yaml # Arquivo de configuração do monorepo
```

---


## `packages/backend`

O backend é construído em **Python** com o framework **FastAPI**. Para uma documentação mais detalhada, consulte `packages/backend/DOCUMENTATION.md`.

### Estrutura do Backend

```
packages/backend/
├── src/
│   └── backend_projeto/
│       ├── api/          # Módulos de endpoints da API
│       ├── core/         # Lógica de negócio principal
│       ├── utils/        # Funções utilitárias
│       └── main.py       # Ponto de entrada da aplicação FastAPI
├── tests/              # Testes automatizados
├── scripts/            # Scripts de automação (ex: geração OpenAPI)
└── requirements.txt    # Dependências do Python
```

---


## `packages/frontend`

O frontend é uma aplicação web moderna construída com **Next.js**, **React** e **TypeScript**. Para uma documentação mais detalhada, consulte `packages/frontend/DOCUMENTATION.md`.

### Estrutura do Frontend

```
packages/frontend/
├── app/                  # Diretório principal do Next.js (App Router)
│   ├── (dashboard)/      # Rotas e páginas do dashboard
│   └── layout.tsx        # Layout principal da aplicação
├── components/           # Componentes React reutilizáveis
│   ├── ui/               # Componentes de UI básicos (Shadcn/UI)
│   └── ...               # Componentes de gráficos e tabelas
├── lib/                  # Funções utilitárias e cliente da API
└── package.json          # Dependências e scripts do frontend
```