# Plataforma de Análise de Investimentos

Este projeto é uma plataforma completa para análise de investimentos, projetada para ajudar usuários a tomar decisões informadas sobre seus portfólios. A arquitetura é baseada em um monorepo que contém um backend robusto para processamento de dados e um frontend moderno e interativo para visualização.

## ✨ Funcionalidades Principais

### Análise de Desempenho e Risco
Esta é a base para qualquer análise de investimento, permitindo uma avaliação completa da performance histórica de um portfólio. A plataforma vai além de simplesmente mostrar o retorno, oferecendo um conjunto rico de métricas para uma compreensão profunda da estratégia de investimento.

-   **Métricas de Desempenho:** Visualize o **Retorno Acumulado** para ver o crescimento total do seu investimento. Analise a **Volatilidade Anualizada** para entender o grau de oscilação dos seus ativos.
-   **Índices Ajustados ao Risco:** A plataforma calcula índices padrão da indústria, como o **Índice de Sharpe**, que mede o retorno que você obtém para cada unidade de risco assumida (volatilidade). O **Índice de Sortino** é similar, mas foca apenas na volatilidade negativa (o "risco ruim"), oferecendo uma perspectiva diferente sobre a eficiência do seu portfólio.
-   **Análise de Risco de Cauda (Tail Risk):** Para entender os riscos em cenários mais extremos, a ferramenta calcula o **Value at Risk (VaR)**, que estima a perda máxima esperada para um determinado nível de confiança (ex: "há 95% de chance de que as perdas não excedam X em um dia"). Indo um passo além, o **Conditional Value at Risk (CVaR)** calcula a média das perdas que ocorrem *além* do VaR, dando uma imagem mais clara do prejuízo potencial durante os piores cenários de mercado.

### Otimização de Portfólio com Fronteira Eficiente
Esta ferramenta poderosa, baseada no trabalho do prêmio Nobel Harry Markowitz, resolve um dos problemas centrais do investimento: como construir a carteira "perfeita". Em vez de tentar adivinhar a melhor alocação, a Fronteira Eficiente usa a matemática para encontrar as combinações ideais de ativos.

-   **Conceito:** A ferramenta calcula e desenha uma curva em um gráfico de risco vs. retorno. Cada ponto nesta curva representa um portfólio "ótimo", ou seja, uma carteira que oferece o maior retorno possível para um determinado nível de risco.
-   **Tomada de Decisão:** Com essa visualização, o investidor pode tomar decisões informadas. Ele pode, por exemplo, identificar o **Portfólio de Variância Mínima** (o ponto de menor risco na curva) ou o **Portfólio de Máximo Sharpe** (a melhor combinação de risco e retorno). Isso permite ajustar a carteira de acordo com o seu perfil de risco pessoal, seja para minimizar o risco para um retorno desejado, ou para maximizar o retorno para um risco que você está disposto a correr.

### Visualizações Avançadas e Interativas
Para realmente entender a dinâmica interna de um portfólio, é preciso ir além dos números e observar o comportamento dos ativos. Esta plataforma oferece um conjunto de gráficos interativos para fornecer insights profundos.

-   **Matriz de Correlação:** Essencial para a diversificação. Este gráfico mostra visualmente como cada ativo se move em relação aos outros. O objetivo é construir uma carteira com ativos de baixa correlação, pois isso significa que quando um ativo cai, o outro pode subir ou permanecer estável, suavizando as oscilações do portfólio.
-   **Contribuição de Risco por Ativo:** Nem todo ativo contribui igualmente para o risco total da carteira. Este gráfico decompõe a volatilidade do portfólio e mostra exatamente qual porcentagem do risco vem de cada ativo. Isso é crucial para identificar se um único ativo está dominando o risco da carteira, permitindo um rebalanceamento mais inteligente.
-   **Rolling Returns e Drawdown:** O desempenho passado não é uma linha reta. **Rolling Returns** (retornos móveis) mostram a performance do portfólio em diferentes janelas de tempo (ex: o retorno anualizado em cada um dos últimos 5 anos), revelando a consistência da estratégia. **Drawdown** mostra os períodos de queda, destacando a magnitude e a duração das piores perdas que o portfólio sofreu, um teste de estresse essencial para entender a resiliência do investimento.

### Simulação de Monte Carlo
Enquanto as outras ferramentas analisam o passado, a Simulação de Monte Carlo olha para o futuro. É uma técnica estatística que ajuda a responder à pergunta: "Dado o comportamento histórico dos meus ativos, qual é a gama de resultados possíveis para o meu portfólio no futuro?"

-   **Processo:** A ferramenta executa milhares (ou dezenas de milhares) de simulações, gerando caminhos aleatórios para os preços dos ativos com base em suas volatilidades e retornos históricos.
-   **Resultado:** O resultado não é uma única previsão, mas uma distribuição de probabilidade de todos os resultados possíveis. Isso permite ao investidor visualizar, por exemplo, a probabilidade de atingir uma meta financeira em 10 anos, ou as chances de o portfólio cair abaixo de um certo valor, oferecendo uma maneira quantitativa de avaliar o risco futuro.

### Autenticação Segura
A segurança e a privacidade dos dados financeiros são primordiais. A plataforma garante que todas as informações do usuário sejam protegidas por um sistema de autenticação robusto.

-   **Tecnologia:** Utiliza o padrão de mercado **JSON Web Tokens (JWT)**. Após um login bem-sucedido com nome de usuário e senha, o backend gera um token digital assinado e o envia ao frontend.
-   **Proteção:** O frontend anexa este token a cada requisição subsequente à API. O backend então verifica a assinatura do token para garantir que a requisição é autêntica e vem de um usuário logado. Isso impede o acesso não autorizado aos dados e funcionalidades da plataforma, garantindo que a análise de cada usuário permaneça confidencial.

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
