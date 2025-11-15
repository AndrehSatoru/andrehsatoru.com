# Documentação do Projeto de Análise de Investimentos

## Visão Geral do Projeto

Este projeto é uma plataforma completa para análise de investimentos, projetada para ajudar usuários a tomar decisões informadas sobre seus portfólios. A arquitetura é baseada em um monorepo que contém um backend robusto para processamento de dados e um frontend moderno e interativo para visualização.

A plataforma oferece os seguintes recursos principais:
- Análise de portfólio com métricas de risco e retorno.
- Otimização de portfólio usando a Fronteira Eficiente.
- Visualizações avançadas, como matriz de correlação, gráficos de contribuição de risco e distribuições de retornos.
- Simulações de Monte Carlo para prever possíveis resultados do portfólio.

## Estrutura do Monorepo

O projeto está organizado como um monorepo, gerenciado por workspaces (npm, yarn ou pnpm). Essa abordagem centraliza o gerenciamento de dependências e facilita a integração entre o frontend e o backend.

A estrutura principal do diretório é a seguinte:

```
.
├── packages/
│   ├── backend/      # Projeto do Backend (Python/FastAPI)
│   │   └── examples/ # Scripts e dados de exemplo
│   ├── frontend/     # Projeto do Frontend (Next.js/React)
│   └── shared-types/ # Definições de tipos compartilhadas entre frontend e backend
└── package.json      # Arquivo de configuração do monorepo
```

- **`packages/`**: Contém os projetos individuais (workspaces) do monorepo.
  - **`backend/`**: O serviço de backend responsável pela lógica de negócios, análise de dados e fornecimento de APIs.
  - **`frontend/`**: A aplicação de frontend que consome as APIs do backend e apresenta os dados aos usuários.
  - **`shared-types/`**: Um pacote que contém definições de tipos TypeScript compartilhadas, garantindo consistência e segurança de tipo entre o frontend e o backend.
- **`package.json`**: Arquivo na raiz que define os workspaces e permite a execução de scripts que orquestram ambos os projetos.

---

## Plano de Integração Backend ↔ Frontend

Para garantir uma comunicação robusta e tipada entre o backend FastAPI e o frontend Next.js/React, um plano de integração detalhado foi estabelecido. Este plano descreve as fases, tecnologias e entregáveis para a sincronização de APIs e tipos compartilhados.

**Status Atual:** A **Fase 1: Contrato de API** foi **concluída**. Esta fase envolveu a formalização do contrato da API, a geração da especificação OpenAPI e a criação dos tipos compartilhados (TypeScript/Zod) para o frontend. Detalhes completos podem ser encontrados em [PLANO_INTEGRACAO.md](PLANO_INTEGRACAO.md).

---

## `packages/backend`

O backend é construído em **Python** com o framework **FastAPI**, que oferece alta performance e uma maneira fácil de criar APIs robustas. Para uma documentação mais detalhada sobre a arquitetura, funcionalidades e configuração do backend, consulte [packages/backend/DOCUMENTATION.md](packages/backend/DOCUMENTATION.md).

### Estrutura do Backend

```
packages/backend/
├── src/
│   └── backend_projeto/
│       ├── api/          # Módulos de endpoints da API
│       ├── core/         # Lógica de negócio principal
│       ├── utils/        # Funções utilitárias (logging, cache, etc.)
│       └── main.py       # Ponto de entrada da aplicação FastAPI
├── tests/              # Testes automatizados (unitários e de integração)
├── scripts/            # Scripts de automação (e.g., geração OpenAPI)
├── examples/           # Scripts e dados de exemplo
├── requirements.txt    # Dependências do Python
├── backend.Dockerfile  # Configuração para containerização com Docker
└── ...
```

#### `src/backend_projeto/`
Este é o coração do backend.

- **`api/`**: Define todos os endpoints da API REST. Os endpoints são agrupados por funcionalidade para manter a organização:
  - `portfolio_endpoints.py`: Endpoints para gerenciamento e análise de portfólios.
  - `risk_endpoints.py`: Endpoints para cálculos de métricas de risco (VaR, CVaR).
  - `data_endpoints.py`: Endpoints para busca de dados de mercado (preços de ativos, etc.).
  - `visualization_endpoints.py`: Endpoints que geram dados para as visualizações do frontend.
  - `main.py`: Ponto de entrada da aplicação FastAPI, onde a aplicação é instanciada e as rotas são configuradas.

- **`core/`**: Contém a lógica de negócio desacoplada da camada de API.
  - `analysis.py`: Funções para análise de séries temporais, cálculo de retornos, volatilidade, etc.
  - `optimization.py`: Implementação de algoritmos de otimização, como a Fronteira Eficiente de Markowitz.
  - `data_handling.py`: Lógica para buscar, limpar e gerenciar dados de fontes externas (ex: yfinance).
  - `visualization.py`: Módulos para gerar os dados necessários para os gráficos complexos exibidos no frontend.

- **`utils/`**: Ferramentas e utilitários compartilhados pelo backend.
  - `logging_setup.py`: Configuração centralizada de logs.
  - `cache.py`: Gerenciamento de cache para otimizar o tempo de resposta de requisições repetidas.

#### `tests/`
Contém os testes automatizados para garantir a qualidade e a estabilidade do backend.
- **`unit/`**: Testes que validam pequenas partes do código (funções, classes) de forma isolada.
- **`integration/`**: Testes que verificam a interação entre diferentes componentes do sistema, como a API e a lógica de negócio.

#### Arquivos Chave
- **`requirements.txt`**: Lista todas as bibliotecas Python necessárias para o projeto. Use `pip install -r requirements.txt` para instalar.
- **`backend.Dockerfile`** e **`docker-compose.yml`**: Permitem que o backend seja executado em um ambiente containerizado, garantindo consistência entre desenvolvimento e produção.

---

## `packages/frontend`

O frontend é uma aplicação web moderna construída com **Next.js**, **React** e **TypeScript**. Ele é responsável por fornecer uma interface de usuário rica e interativa para a visualização dos dados de análise de investimentos. Para uma documentação mais detalhada sobre a arquitetura, funcionalidades e configuração do frontend, consulte [packages/frontend/DOCUMENTATION.md](packages/frontend/DOCUMENTATION.md).

### Estrutura do Frontend

```
packages/frontend/
├── app/                  # Diretório principal do Next.js (App Router)
│   ├── (dashboard)/      # Rotas e páginas do dashboard
│   ├── api/              # API routes do Next.js (BFF)
│   └── layout.tsx        # Layout principal da aplicação
├── components/           # Componentes React reutilizáveis
│   ├── ui/               # Componentes de UI básicos (ex: botões, inputs)
│   └── ...               # Componentes de gráficos e tabelas
├── public/               # Arquivos estáticos (imagens, fontes)
├── package.json          # Dependências e scripts do frontend
└── next.config.mjs       # Arquivo de configuração do Next.js
```

#### `app/`
Este diretório segue a convenção do **App Router** do Next.js.
- **`(dashboard)/`**: Agrupa as páginas relacionadas ao dashboard principal, como a visualização de portfólio, análise de risco, etc.
- **`api/`**: Contém rotas de API do lado do servidor (Backend-for-Frontend). Pode ser usado para tarefas como autenticação ou para fazer proxy de requisições para o backend Python.
- **`layout.tsx`** e **`page.tsx`**: Componentes principais que definem a estrutura da página e a página inicial.

#### `components/`
Aqui ficam todos os componentes React, organizados para máxima reutilização.
- **`ui/`**: Componentes de interface de usuário genéricos, como botões, cards e modais, possivelmente de uma biblioteca como **Shadcn/UI**.
- **Componentes de Gráficos**: Uma vasta gama de componentes especializados para visualização de dados financeiros, como:
  - `allocation-chart.tsx`: Gráfico de alocação de ativos.
  - `correlation-matrix.tsx`: Matriz de correlação entre ativos.
  - `efficient-frontier.tsx`: Gráfico da fronteira eficiente.
  - `performance-chart.tsx`: Gráfico de desempenho histórico do portfólio.

#### Arquivos Chave
- **`package.json`**: Lista as dependências do Node.js (React, Next.js, bibliotecas de gráficos) e os scripts para rodar, testar e construir o projeto (`dev`, `build`, `start`).
- **`next.config.mjs`**: Arquivo de configuração do Next.js, onde são definidas regras de build, redirecionamentos, proxies e outras configurações avançadas.
- **`tsconfig.json`**: Arquivo de configuração do TypeScript, que define as regras de tipagem para o projeto.

## Como Começar

Para configurar e executar o projeto localmente, a maneira mais fácil e recomendada é utilizando Docker Compose.

### 1. Com Docker Compose (Recomendado)

Certifique-se de ter o Docker e o Docker Compose instalados em sua máquina.

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-repositorio>
    cd <nome-do-repositorio>
    ```
    *Nota: Scripts e dados de exemplo podem ser encontrados em `packages/backend/examples/`.*

2.  **Configure as variáveis de ambiente:**
    - Crie um arquivo `.env` na raiz do diretório `packages/backend/` a partir do `.env.example` (`cp packages/backend/.env.example packages/backend/.env`).
    - Crie um arquivo `.env.local` na raiz do diretório `packages/frontend/` a partir do `.env.example` (`cp packages/frontend/.env.example packages/frontend/.env.local`).
    - Edite esses arquivos para configurar as chaves de API e outras variáveis necessárias.

3.  **Inicie os serviços:**
    A partir da raiz do projeto, execute:
    ```bash
    docker-compose up --build -d
    ```
    Isso construirá as imagens do Docker para o backend e o frontend (se necessário) e iniciará ambos os serviços em segundo plano.

4.  **Acesse a aplicação:**
    - O frontend estará disponível em `http://localhost:3000`.
    - A documentação da API do backend (Swagger UI) estará em `http://localhost:8001/docs`.

### 2. Manualmente (Alternativa)

Se você preferir executar os serviços manualmente, siga os passos abaixo:

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-repositorio>
    cd <nome-do-repositorio>
    ```

2.  **Instale as dependências do monorepo:**
    Certifique-se de ter o `pnpm` (recomendado), `yarn` ou `npm` instalado. A partir do diretório raiz, instale todas as dependências do frontend e do `shared-types`.
    ```bash
    # Usando pnpm (recomendado)
    pnpm install
    ```

3.  **Configure e execute o Backend:**
    - Navegue até `packages/backend`.
    - Crie e ative um ambiente virtual Python:
      ```bash
      python -m venv venv
      # No Linux/macOS
      source venv/bin/activate
      # No Windows
      .\venv\Scripts\Activate.ps1
      ```
    - Instale as dependências do Python:
      ```bash
      pip install -r requirements.txt
      ```
    - Configure as variáveis de ambiente criando um arquivo `.env` a partir do `.env.example` e editando-o.
    - Inicie o servidor:
      ```bash
      uvicorn src.backend_projeto.main:app --reload --host 0.0.0.0 --port 8001
      ```
    - A documentação da API do backend (Swagger UI) estará em `http://localhost:8001/docs`.

4.  **Configure e execute o Frontend:**
    - Navegue até `packages/frontend`.
    - Configure as variáveis de ambiente criando um arquivo `.env.local` a partir do `.env.example` e editando-o (especialmente `NEXT_PUBLIC_API_URL` para apontar para o backend, e.g., `http://localhost:8001`).
    - Inicie o servidor de desenvolvimento:
      ```bash
      pnpm dev
      ```
    - O frontend estará disponível em `http://localhost:3000`.
