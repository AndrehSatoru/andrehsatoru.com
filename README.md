# Plataforma de Análise de Investimentos

Este projeto é uma plataforma completa para análise de investimentos, projetada para ajudar usuários a tomar decisões informadas sobre seus portfólios. A arquitetura é baseada em um monorepo que contém um backend robusto para processamento de dados e um frontend moderno e interativo para visualização.

Este documento é dividido em duas partes principais:
1.  **Visão Geral do Produto**: Descreve as funcionalidades da plataforma do ponto de vista do usuário.
2.  **Guia do Desenvolvedor**: Um manual técnico sobre a arquitetura, configuração e fluxo de trabalho para contribuidores do projeto.

---

## Parte 1: Visão Geral do Produto

### Tecnologias Utilizadas
| Categoria | Tecnologia |
| :--- | :--- |
| **Monorepo** | [pnpm](https://pnpm.io/) |
| **Frontend** | [Next.js](https://nextjs.org/), [React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/), [Shadcn/UI](https://ui.shadcn.com/) |
| **Backend** | [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://docs.pydantic.dev/) |
| **Testes** | [Pytest](https://docs.pytest.org/) (Backend) |
| **Containerização**| [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) |
| **Integração** | [OpenAPI](https://www.openapis.org/), Geração de cliente API |

### Funcionalidades Principais

#### Análise de Desempenho e Risco
Esta é a base para qualquer análise de investimento, permitindo uma avaliação completa da performance histórica de um portfólio. A plataforma vai além de simplesmente mostrar o retorno, oferecendo um conjunto rico de métricas para uma compreensão profunda da estratégia de investimento.

-   **Métricas de Desempenho:** Visualize o **Retorno Acumulado** para ver o crescimento total do seu investimento. Analise a **Volatilidade Anualizada** para entender o grau de oscilação dos seus ativos.
-   **Índices Ajustados ao Risco:** A plataforma calcula índices padrão da indústria, como o **Índice de Sharpe**, que mede o retorno que você obtém para cada unidade de risco assumida (volatilidade). O **Índice de Sortino** é similar, mas foca apenas na volatilidade negativa (o "risco ruim"), oferecendo uma perspectiva diferente sobre a eficiência do seu portfólio.
-   **Análise de Risco de Cauda (Tail Risk):** Para entender os riscos em cenários mais extremos, a ferramenta calcula o **Value at Risk (VaR)**, que estima a perda máxima esperada para um determinado nível de confiança (ex: "há 95% de chance de que as perdas não excedam X em um dia"). Indo um passo além, o **Conditional Value at Risk (CVaR)** calcula a média das perdas que ocorrem *além* do VaR, dando uma imagem mais clara do prejuízo potencial durante os piores cenários de mercado.

#### Otimização de Portfólio com Fronteira Eficiente
Esta ferramenta poderosa, baseada no trabalho do prêmio Nobel Harry Markowitz, resolve um dos problemas centrais do investimento: como construir a carteira "perfeita". Em vez de tentar adivinhar a melhor alocação, a Fronteira Eficiente usa a matemática para encontrar as combinações ideais de ativos.

-   **Conceito:** A ferramenta calcula e desenha uma curva em um gráfico de risco vs. retorno. Cada ponto nesta curva representa um portfólio "ótimo", ou seja, uma carteira que oferece o maior retorno possível para um determinado nível de risco.
-   **Tomada de Decisão:** Com essa visualização, o investidor pode tomar decisões informadas. Ele pode, por exemplo, identificar o **Portfólio de Variância Mínima** (o ponto de menor risco na curva) ou o **Portfólio de Máximo Sharpe** (a melhor combinação de risco e retorno). Isso permite ajustar a carteira de acordo com o seu perfil de risco pessoal.

#### Visualizações Avançadas e Interativas
Para realmente entender a dinâmica interna de um portfólio, é preciso ir além dos números e observar o comportamento dos ativos.

-   **Matriz de Correlação:** Essencial para a diversificação. Este gráfico mostra visualmente como cada ativo se move em relação aos outros, ajudando a construir uma carteira com ativos de baixa correlação para suavizar as oscilações.
-   **Contribuição de Risco por Ativo:** Decompõe a volatilidade do portfólio e mostra exatamente qual porcentagem do risco vem de cada ativo. Isso é crucial para identificar se um único ativo está dominando o risco da carteira.
-   **Rolling Returns e Drawdown:** **Rolling Returns** (retornos móveis) mostram a consistência da performance em diferentes janelas de tempo. **Drawdown** mostra os períodos de queda, destacando a magnitude e a duração das piores perdas que o portfólio sofreu.

#### Simulação de Monte Carlo
Enquanto as outras ferramentas analisam o passado, a Simulação de Monte Carlo olha para o futuro, ajudando a responder: "Qual é a gama de resultados possíveis para o meu portfólio?"

-   **Processo:** A ferramenta executa milhares de simulações, gerando caminhos aleatórios para os preços dos ativos com base em suas volatilidades e retornos históricos.
-   **Resultado:** O resultado é uma distribuição de probabilidade de todos os resultados possíveis, permitindo ao investidor visualizar a probabilidade de atingir metas financeiras.

#### Autenticação Segura
A segurança e a privacidade dos dados financeiros são primordiais, garantidas por um sistema de autenticação robusto que utiliza o padrão de mercado **JSON Web Tokens (JWT)** para proteger as sessões dos usuários.

---

## Parte 2: Guia do Desenvolvedor

Esta seção é o manual técnico do projeto. O objetivo é que, após a leitura, um desenvolvedor tenha uma compreensão profunda da arquitetura e do fluxo de trabalho.

### 1. Filosofia de Arquitetura

As decisões arquiteturais foram tomadas para maximizar a produtividade, a segurança e a manutenibilidade do projeto.

#### a. Monorepo com `pnpm` Workspaces
-   **O quê**: Todo o código-fonte (`backend`, `frontend`, `shared-types`) reside em um único repositório Git, e os pacotes são interligados usando `pnpm` workspaces, definidos no arquivo `pnpm-workspace.yaml`.
-   **Por quê**:
    -   **Visibilidade e Consistência**: Um único `pnpm-lock.yaml` na raiz garante que todos os desenvolvedores e ambientes de CI/CD usem exatamente as mesmas versões de todas as dependências, eliminando problemas de "funciona na minha máquina".
    -   **Desenvolvimento Integrado**: `pnpm` cria links simbólicos (symlinks) entre os pacotes do workspace. Isso significa que quando você faz uma alteração no pacote `shared-types`, o `frontend` instantaneamente recebe essa atualização sem a necessidade de publicar o pacote em um registro como o NPM.
    -   **Eficiência**: Comandos como `pnpm install` podem ser executados na raiz para instalar dependências de todos os pacotes de uma só vez.

#### b. A Ponte de Tipagem Segura: O Coração do Projeto
-   **O Problema**: Em aplicações full-stack tradicionais, o frontend não "sabe" quando o backend muda a estrutura de uma API. Uma alteração no backend pode causar um erro silencioso no frontend que só é descoberto em produção.
-   **A Solução**: Implementamos um fluxo de trabalho que garante que o frontend e o backend falem sempre a mesma língua, movendo os erros do ambiente de produção para o ambiente de desenvolvimento (em tempo de compilação).
-   **O Fluxo em Detalhe**:
    1.  **Backend Define o Contrato**: No FastAPI, definimos um modelo de resposta usando Pydantic.
        ```python
        # packages/backend/src/backend_projeto/api/models.py
        from pydantic import BaseModel

        class UserProfile(BaseModel):
            user_id: int
            full_name: str
            risk_score: float
        ```
    2.  **FastAPI Gera a Especificação OpenAPI**: Com base nesse modelo, o FastAPI gera um trecho no `openapi.json` que se parece com isto:
        ```json
        "UserProfile": {
            "title": "UserProfile",
            "type": "object",
            "properties": {
                "user_id": { "title": "User Id", "type": "integer" },
                "full_name": { "title": "Full Name", "type": "string" },
                "risk_score": { "title": "Risk Score", "type": "number" }
            }
        }
        ```
    3.  **Geração de Tipos TypeScript**: O script `scripts/generate_openapi.py` usa uma ferramenta que lê o `openapi.json` e o converte para uma interface TypeScript no pacote `shared-types`.
        ```typescript
        // packages/shared-types/src/generated.d.ts
        export interface UserProfile {
            user_id: number;
            full_name: string;
            risk_score: number;
        }
        ```
    -   **O Resultado**: Se um desenvolvedor do backend renomear `full_name` para `name`, o `pnpm dev` do frontend falhará imediatamente, apontando todos os locais onde `full_name` era usado. **O bug é corrigido em segundos, não em dias.**

#### c. Backend com FastAPI: Performance e Validação
-   **Por que FastAPI?**:
    -   **Validação de Dados com Pydantic**: FastAPI usa Pydantic para declarar os modelos de dados. Isso significa que cada requisição que chega é automaticamente validada. Se um tipo de dado estiver errado, o FastAPI retorna um erro 422 claro e descritivo, em vez de deixar o erro se propagar pela lógica de negócio.
    -   **Injeção de Dependências**: O sistema de `Depends` do FastAPI facilita a escrita de código modular e testável. Dependências como acesso ao banco de dados, autenticação de usuário ou gerenciadores de cache podem ser "injetadas" nos endpoints, permitindo que sejam facilmente substituídas por mocks durante os testes.
    -   **Performance**: Por ser assíncrono (ASGI) desde a sua concepção, o FastAPI oferece uma performance extremamente alta, ideal para endpoints de dados que podem envolver I/O (entrada/saída) demorado.

#### d. Frontend com Next.js: Foco na Experiência do Desenvolvedor e do Usuário
-   **Por que Next.js?**:
    -   **App Router**: A estrutura de roteamento baseada em diretórios (`app/`) é intuitiva e organiza o projeto de forma lógica.
    -   **Component-First com Shadcn/UI**: A biblioteca `shadcn/ui` foi escolhida por não ser uma biblioteca de componentes tradicional. Em vez disso, ela fornece "receitas" de componentes acessíveis e não estilizados que copiamos para o nosso projeto (`components/ui`). Isso nos dá total controle sobre a aparência e o comportamento, evitando o "bloat" de bibliotecas de UI monolíticas.
    -   **Estilização com Tailwind CSS**: O Tailwind permite uma estilização rápida e consistente através de classes de utilitário, mantendo o CSS próximo ao HTML e evitando a necessidade de arquivos de estilo separados para cada componente.

### 2. Estrutura Detalhada do Projeto

-   `packages/backend`
    -   `src/backend_projeto/api/`: Camada de entrada da aplicação. Define os endpoints HTTP, valida os dados da requisição (usando Pydantic) e formata a resposta. **A lógica de negócio aqui deve ser mínima**, limitando-se a chamar os serviços do `core`.
    -   `src/backend_projeto/core/`: O cérebro da aplicação. Contém os módulos de Python puros com toda a lógica de negócio (cálculos financeiros, algoritmos de otimização). **Este código não deve ter conhecimento do FastAPI**; ele poderia, teoricamente, ser importado em qualquer outro projeto Python.
    -   `src/backend_projeto/utils/`: Funções e classes utilitárias compartilhadas por todo o backend, como configuração de logging, gerenciadores de cache, etc.
    -   `tests/`: Contém os testes automatizados. `tests/unit` para testar a lógica do `core` de forma isolada e `tests/integration` para testar os endpoints da API.

-   `packages/frontend`
    -   `app/`: Estrutura do App Router do Next.js. Cada pasta aqui (que não esteja entre parênteses) corresponde a uma rota na URL da aplicação.
    -   `components/`: O coração da UI.
        -   `components/ui/`: Componentes de base, não estilizados, provenientes do `shadcn/ui` (ex: `Button`, `Card`).
        -   `components/*.tsx`: Componentes de "features" que compõem a aplicação, como `allocation-chart.tsx` ou `metrics-grid.tsx`. Eles combinam os componentes de `ui` com a lógica de busca de dados.
    -   `lib/`: Funções utilitárias do lado do cliente. O arquivo mais importante aqui é `lib/backend-api.ts`, que instancia o cliente de API gerado.
    -   `hooks/`: Custom React Hooks que encapsulam lógica reutilizável, como `use-api.ts` (para chamadas de API com estado de loading/error) ou `useAuthStore.ts` (para gerenciamento de estado de autenticação com Zustand).

-   `packages/shared-types`
    -   **NÃO EDITE MANUALMENTE!** Este pacote é um artefato de build. Seu único propósito é conter as definições de tipo TypeScript e o cliente de API que são gerados pelo processo da "Ponte de Tipagem Segura".

### 3. Fluxo de Trabalho do Desenvolvedor (Exemplo Concreto)

Adicionar um novo gráfico de "Evolução do Beta":

1.  **Backend - Definir Modelo e Lógica**:
    -   Em `packages/backend/src/backend_projeto/api/models.py`, defina a estrutura da resposta: `class BetaPoint(BaseModel): date: date; beta_value: float`.
    -   Em `packages/backend/src/backend_projeto/core/analysis_engine.py`, crie a função: `def calculate_rolling_beta(...) -> List[BetaPoint]:`.
2.  **Backend - Criar Endpoint**:
    -   Em `packages/backend/src/backend_projeto/api/analysis_endpoints.py`, adicione a rota:
        ```python
        @router.post("/rolling-beta", response_model=List[BetaPoint])
        def get_rolling_beta(request: PortfolioRequest):
            # ...chama a função do core...
            return result
        ```
3.  **Sincronizar Tipos**:
    -   No terminal, na pasta `packages/backend`, rode `python ./scripts/generate_openapi.py`. Você verá `packages/shared-types` ser modificado.
4.  **Frontend - Criar Componente**:
    -   Crie o arquivo `packages/frontend/components/beta-evolution-chart.tsx`.
    -   Dentro dele, importe o tipo recém-gerado: `import { BetaPoint } from 'shared-types';`.
    -   Use o hook `use-api` para chamar o novo endpoint, que já estará disponível no cliente da API com autocomplete e tipagem.
        ```tsx
        const { data, loading } = useApi(() => apiClient.get_rolling_beta_api_v1_analysis_rolling_beta_post({ body: ... }));
        ```
    -   Renderize o gráfico usando `data`. O TypeScript garantirá que você está acessando `beta_value` e não `beta_val`, por exemplo.

### 4. Configuração do Ambiente (Windows)

#### Pré-requisitos
-   [Node.js (LTS)](https://nodejs.org/en/download/)
-   [pnpm](https://pnpm.io/installation) (após instalar Node.js, rode `npm install -g pnpm`)
-   [Python (3.9+)] (https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads/)

#### Passos
1.  **Instalar Dependências**: O script `install_deps.ps1` automatiza todo o processo. Ele executa `pnpm install` na raiz (que cuida do `frontend` e `shared-types`) e depois cria um ambiente virtual Python em `packages/backend/.venv` e instala as dependências do `requirements.txt` nele.
    ```powershell
    .ill_deps.ps1
    ```
2.  **Configurar Variáveis de Ambiente**:
    -   **Backend**: Copie `packages/backend/.env.example` para `packages/backend/.env`. Este arquivo é usado para segredos do lado do servidor, como chaves de API para fontes de dados externas.
    -   **Frontend**: Copie `packages/frontend/.env.example` para `packages/frontend/.env.local`. A variável mais importante é `NEXT_PUBLIC_API_URL`, que diz ao seu navegador para onde enviar as requisições da API (ex: `http://localhost:8001`).
3.  **Executar Servidores**:
    -   **Backend**: O script `run_server.ps1` ativa o ambiente virtual do backend e inicia o servidor `uvicorn`.
        ```powershell
        .un_server.ps1
        ```
        -   Backend API: `http://localhost:8001`
        -   Documentação Interativa (Swagger): `http://localhost:8001/docs`
    -   **Frontend**: Em um **novo terminal**, inicie o servidor de desenvolvimento do Next.js.
        ```bash
        cd packages/frontend
        pnpm dev
        ```
        -   Frontend UI: `http://localhost:3000`

### 5. Testes

A estratégia de testes é focada no backend para garantir a precisão dos cálculos e a estabilidade da API.

-   **Filosofia**:
    -   **Testes Unitários (`tests/unit`)**: Devem ser rápidos e testar a lógica pura dos módulos em `core/`. Eles não devem fazer requisições de rede ou acessar bancos de dados. Use mocks para simular dependências externas.
    -   **Testes de Integração (`tests/integration`)**: São mais lentos e testam a aplicação de ponta a ponta (no nível da API). Eles fazem requisições HTTP reais para a aplicação de teste e verificam se a resposta (código de status, corpo do JSON) está correta. Isso garante que o contrato da API está sendo cumprido.
-   **Como Executar**:
    1.  Navegue até a pasta do backend: `cd packages/backend`
    2.  Ative o ambiente virtual: `.illinun_server.ps1`
    3.  Execute todos os testes:
        ```bash
        pytest
        ```
    4.  Execute um arquivo de teste específico:
        ```bash
        pytest tests/unit/test_analysis_engine.py
        ```