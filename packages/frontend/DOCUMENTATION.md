# Documentação do Frontend

Este documento fornece uma visão detalhada da arquitetura, funcionalidades e configuração do frontend da plataforma de análise de investimentos.

## 1. Visão Geral

O frontend é uma Single-Page Application (SPA) construída com **Next.js** (utilizando o App Router) e **TypeScript**. Ele fornece a interface de usuário para interagir com a plataforma, visualizar análises e gerenciar portfólios.

**Principais Tecnologias:**

*   **Next.js:** Framework React para construção de aplicações web.
*   **React:** Biblioteca para construção de interfaces de usuário.
*   **TypeScript:** Para tipagem estática e um desenvolvimento mais robusto.
*   **Tailwind CSS:** Para estilização.
*   **shadcn/ui:** Coleção de componentes de UI reutilizáveis.
*   **Recharts:** Para a criação de gráficos.
*   **Zustand:** Para gerenciamento de estado global.
*   **Axios:** Para realizar requisições HTTP para o backend.

## 2. Arquitetura

A arquitetura do frontend é baseada em componentes e segue as convenções do Next.js App Router.

```
packages/frontend/
├── app/                      # Rotas da aplicação
│   ├── (main)/               # Rotas principais (e.g., dashboard)
│   ├── login/                # Rota de login
│   ├── layout.tsx            # Layout principal da aplicação
│   └── globals.css           # Estilos globais
├── components/               # Componentes React reutilizáveis
│   ├── ui/                   # Componentes de UI (shadcn)
│   └── ...                   # Componentes específicos da aplicação
├── hooks/                    # Hooks React customizados
├── lib/                      # Funções utilitárias e cliente da API
├── public/                   # Arquivos estáticos (imagens, etc.)
├── styles/                   # Arquivos de estilo
├── .env.example              # Arquivo de exemplo para variáveis de ambiente
├── package.json              # Dependências e scripts do projeto
└── tsconfig.json             # Configuração do TypeScript
```

### 2.1. `app/`

Este diretório contém as rotas da aplicação, seguindo a estrutura do App Router do Next.js. Cada pasta representa um segmento da URL e pode conter arquivos `page.tsx` (para renderizar UI), `layout.tsx` (para layouts compartilhados), e `loading.tsx` (para estados de carregamento).

### 2.2. `components/`

Contém todos os componentes React da aplicação. A subpasta `ui/` é dedicada aos componentes do `shadcn/ui`, que são componentes de UI reutilizáveis e acessíveis. Os outros arquivos são componentes customizados para a aplicação (e.g., `allocation-chart.tsx`, `metrics-grid.tsx`), que encapsulam lógica e UI específicas.

### 2.3. `hooks/`

Este diretório armazena hooks customizados que encapsulam lógica reutilizável e específica do frontend. Exemplos incluem:
*   `useAuthStore.ts`: Gerencia o estado de autenticação do usuário, incluindo tokens e informações do perfil, utilizando Zustand para estado global.
*   `useApi.ts`: Um hook para simplificar chamadas à API do backend, lidando com estados de carregamento, erros e cache.
*   `useMobile.ts`: Hook para detectar se o usuário está em um dispositivo móvel, permitindo renderização condicional de componentes.

### 2.4. `lib/`

Contém a lógica de comunicação com o backend (`backend-api.ts`), que utiliza o `axios` para fazer requisições HTTP. Este módulo é responsável por configurar o cliente HTTP, adicionar interceptors (e.g., para tokens de autenticação) e tratar erros de forma centralizada. Também pode conter outras funções utilitárias gerais para o frontend.

## 3. Fluxo de Dados e Gerenciamento de Estado

O frontend gerencia o fluxo de dados e o estado da aplicação da seguinte forma:

*   **Requisições à API:** As chamadas ao backend são realizadas através do cliente de API gerado (`openapi.json.client.ts`) e encapsuladas por hooks customizados (`useApi`), que facilitam o tratamento de carregamento, erros e revalidação de dados.
*   **Gerenciamento de Estado Global:** O Zustand é utilizado para gerenciar o estado global da aplicação, como informações de autenticação (`useAuthStore`) e dados que precisam ser acessíveis por múltiplos componentes sem a necessidade de prop drilling.
*   **Estado Local:** O estado local dos componentes é gerenciado com `useState` e `useReducer` do React.

## 4. Tipos Compartilhados (`shared-types`)

O pacote `shared-types` (localizado em `packages/shared-types/`) é crucial para garantir a consistência e a segurança de tipo entre o frontend e o backend. Ele contém:
*   **Definições de Tipos:** Interfaces e tipos TypeScript que representam os modelos de dados utilizados tanto pelo backend (Pydantic) quanto pelo frontend.
*   **Esquemas de Validação:** Pode incluir esquemas de validação (e.g., Zod) que são usados para validar dados tanto no frontend quanto no backend.

Ao centralizar as definições de tipo, evitamos duplicação de código e garantimos que as estruturas de dados esperadas pelo frontend correspondam exatamente às estruturas fornecidas pelo backend, minimizando erros em tempo de execução.

## 5. Funcionalidades

O frontend implementa a interface de usuário para todas as funcionalidades oferecidas pelo backend.

*   **Dashboard Interativo:** Visualização de métricas de portfólio, gráficos de alocação, e evolução de performance.
*   **Envio de Operações:** Formulário para submeter transações de compra e venda de ativos.
*   **Visualização de Análises:** Gráficos de fronteira eficiente, distribuição de retornos, e outras análises de risco.
*   **Autenticação:** Página de login e gerenciamento de sessão do usuário.

## 4. Configuração

A configuração do frontend é gerenciada através de variáveis de ambiente. Crie um arquivo `.env.local` na raiz do diretório `packages/frontend/` (baseado no `.env.example`) para configurar a aplicação.

**Variáveis de Ambiente Essenciais:**

*   `NEXT_PUBLIC_API_URL`: A URL base da API do backend (e.g., `http://localhost:8001`).

## 5. Executando o Frontend

### 5.1. Com Docker (Recomendado)

A maneira mais fácil de executar o frontend é com o Docker Compose.

```bash
# A partir da raiz do projeto
docker-compose up --build -d frontend
```

A aplicação estará disponível em `http://localhost:3000`.

### 5.2. Manualmente

**Pré-requisitos:**

*   Node.js 18+
*   pnpm (ou npm/yarn)

```bash
# A partir de packages/frontend/
# 1. Instale as dependências
pnpm install

# 2. Crie o arquivo .env.local e configure a URL da API

# 3. Inicie o servidor de desenvolvimento
pnpm dev
```

A aplicação estará disponível em `http://localhost:3000`.

## 6. Testes

O projeto pode ser configurado para usar Jest e React Testing Library para testes unitários e de componentes, e Playwright ou Cypress para testes end-to-end. A configuração atual de testes não está especificada nos arquivos do projeto.
```