# Documentação do Backend

Este documento fornece uma visão detalhada da arquitetura, funcionalidades e configuração do backend da plataforma de análise de investimentos.

## 1. Visão Geral

O backend é construído com **FastAPI**, um framework web Python moderno e de alta performance. Ele serve como o cérebro da plataforma, fornecendo uma API RESTful para o frontend e realizando todas as análises financeiras complexas.

**Principais Tecnologias:**

*   **FastAPI:** Para a criação da API.
*   **Pydantic:** Para validação de dados e gerenciamento de configurações.
*   **Pandas, NumPy, SciPy:** Para manipulação e análise de dados.
*   **scikit-learn:** Para modelos de machine learning.
*   **yfinance:** Para obtenção de dados de mercado.
*   **Pytest:** Para testes unitários e de integração.
*   **Docker:** Para containerização e deploy.

## 2. Arquitetura

A arquitetura do backend segue os princípios de **Clean Architecture** e **Domain-Driven Design (DDD)**, organizando o código em camadas bem definidas:

```
packages/backend/
├── src/backend_projeto/
│   ├── api/                  # Interface Layer (Controllers/Endpoints)
│   ├── application/          # Application Layer (Use Cases)
│   ├── domain/               # Domain Layer (Core Business Logic)
│   │   ├── entities.py       # Entities (Portfolio, Transaction, User)
│   │   ├── value_objects.py  # Value Objects (Money, Percentage, Ticker)
│   │   ├── repositories.py   # Repository Interfaces (abstrações)
│   │   ├── services.py       # Domain Services (RiskCalculation, Optimization)
│   │   ├── exceptions.py     # Domain Exceptions
│   │   ├── analysis.py       # Legacy analysis functions
│   │   └── models/           # Pydantic DTOs
│   ├── infrastructure/       # Infrastructure Layer
│   │   ├── data_providers/   # External APIs (yfinance, BCB)
│   │   └── visualization/    # Chart generation
│   ├── cache/                # Caching implementation
│   ├── utils/                # Cross-cutting concerns
│   └── main.py               # FastAPI app entry point
├── tests/                    # Pytest tests
└── requirements.txt          # Python dependencies
```

### 2.1. Domain Layer (`domain/`)

O coração da aplicação, contendo a lógica de negócio pura:

| Componente | Arquivo | Descrição |
|------------|---------|-----------|
| **Value Objects** | `value_objects.py` | Objetos imutáveis: `Money`, `Percentage`, `Ticker`, `DateRange`, `RiskMetrics` |
| **Entities** | `entities.py` | Objetos com identidade: `Portfolio`, `Transaction`, `Position`, `User` |
| **Repository Interfaces** | `repositories.py` | Contratos para persistência: `IPortfolioRepository`, `IMarketDataRepository` |
| **Domain Services** | `services.py` | Lógica cross-entity: `RiskCalculationService`, `PortfolioOptimizationService` |
| **Exceptions** | `exceptions.py` | Exceções de domínio: `AppError`, `DataProviderError` |

### 2.2. Application Layer (`application/`)

Orquestra os casos de uso, coordenando Domain e Infrastructure:

| Arquivo | Responsabilidade |
|---------|------------------|
| `auth.py` | Autenticação e autorização |
| `dashboard_generator.py` | Geração de dados para dashboard |
| `portfolio_simulation.py` | Simulações de portfólio |

### 2.3. Infrastructure Layer (`infrastructure/`)

Implementações concretas dos contratos definidos no Domain:

| Diretório | Responsabilidade |
|-----------|------------------|
| `data_providers/` | APIs externas (Alpha Vantage, Finnhub, yfinance) |
| `data_handling.py` | Processamento de arquivos de transação |
| `visualization/` | Geração de gráficos |

### 2.4. API Layer (`api/`)

Controllers FastAPI que expõem os endpoints:

| Arquivo | Endpoints |
|---------|-----------|
| `transaction_endpoints.py` | `/processar-operacoes`, `/portfolio/*` |
| `risk_endpoints.py` | `/var`, `/cvar`, `/risk/*` |
| `optimization_endpoints.py` | `/frontier`, `/optimize/*` |
| `analysis_endpoints.py` | `/analysis/*` |

### 2.5. Diagrama de Dependências

```
┌─────────────────────────────────────────────────────────┐
│                      API Layer                          │
│              (FastAPI Controllers)                      │
└─────────────────────┬───────────────────────────────────┘
                      │ depends on
┌─────────────────────▼───────────────────────────────────┐
│                 Application Layer                       │
│                  (Use Cases)                            │
└─────────────────────┬───────────────────────────────────┘
                      │ depends on
┌─────────────────────▼───────────────────────────────────┐
│                   Domain Layer                          │
│    (Entities, Value Objects, Services, Interfaces)      │
└─────────────────────────────────────────────────────────┘
                      ▲
                      │ implements
┌─────────────────────┴───────────────────────────────────┐
│               Infrastructure Layer                      │
│        (Repositories, External APIs, Cache)             │
└─────────────────────────────────────────────────────────┘
```

## 3. Definição e Geração do Cliente da API

O backend utiliza o padrão OpenAPI (anteriormente Swagger) para descrever sua API.

### 3.1. `openapi.json`

Este arquivo é a especificação OpenAPI gerada automaticamente pelo FastAPI. Ele descreve todos os endpoints da API, seus parâmetros de entrada, modelos de resposta, tipos de dados e esquemas de autenticação. É a fonte da verdade para a estrutura da API e é utilizado para:
*   **Documentação Interativa:** Gerar a interface Swagger UI (`/docs`) e ReDoc (`/redoc`).
*   **Geração de Clientes:** Permitir que ferramentas gerem automaticamente clientes de API em diversas linguagens.

### 3.2. `openapi.json.client.ts`

Este arquivo é um cliente TypeScript gerado automaticamente a partir do `openapi.json`. Ele fornece funções tipadas para interagir com cada endpoint do backend, eliminando a necessidade de escrever manualmente as chamadas HTTP no frontend e garantindo a consistência entre frontend e backend. A geração é tipicamente feita por uma ferramenta como `openapi-typescript-codegen` ou similar, configurada para ler o `openapi.json` e produzir o cliente.

## 4. Funcionalidades

O backend oferece uma vasta gama de funcionalidades de análise financeira, expostas através da API. Consulte o arquivo `PLANO_INTEGRACAO.md` para uma lista completa dos endpoints.

**Principais Funcionalidades:**

*   **Análise de Risco:** Cálculo de VaR, ES, Drawdown, testes de estresse, etc.
*   **Otimização de Portfólio:** Otimização de Markowitz, Black-Litterman, e fronteira eficiente.
*   **Modelos de Fatores:** CAPM, Fama-French, etc.
*   **Análise Técnica:** Médias móveis, MACD, etc.
*   **Processamento de Transações:** Análise de portfólio baseada em operações de compra e venda.
*   **Rendimento do CDI:** Caixa não investido rende CDI automaticamente com dados reais do Banco Central do Brasil.

### 4.1. Geração de Dados para Gráficos (v1.5.0)

O `PortfolioAnalyzer` gera dados estruturados para os gráficos do dashboard:

| Método | Campo na Resposta | Descrição |
|--------|------------------|-----------|
| `_generate_risk_contribution()` | `risk_contribution` | Decomposição do risco por ativo |
| `_generate_beta_evolution()` | `beta_evolution` | Série temporal do beta rolante (60 dias) vs IBOVESPA |
| `_generate_monte_carlo_simulation()` | `monte_carlo` | Simulação com MGB e Bootstrap |

**Detalhes do Monte Carlo:**

- **MGB (Movimento Geométrico Browniano):** Usa volatilidade histórica (`returns.std()`) e drift baseado na média dos retornos
- **Bootstrap:** Reamostragem dos retornos históricos com reposição (252 dias × 1000 simulações)
- **Bins fixos:** 45 bins independente do tamanho do portfólio

**Cálculo do Beta:**

- Janela rolante de 60 dias
- Benchmark: IBOVESPA (^BVSP via yfinance)
- Agregação mensal (último valor do mês)

## 4. Configuração

A configuração do backend é gerenciada através de variáveis de ambiente. Crie um arquivo `.env` na raiz do diretório `packages/backend/` (baseado no `.env.example`) para configurar a aplicação.

**Variáveis de Ambiente Essenciais:**

*   `CORS_ORIGINS`: As origens permitidas para requisições CORS (e.g., `http://localhost:3000`).
*   `FINNHUB_API_KEY`: Sua chave de API do Finnhub.
*   `ALPHA_VANTAGE_API_KEY`: Sua chave de API do Alpha Vantage.

Consulte o arquivo `CONFIGURATION.md` para uma lista completa das variáveis de ambiente.

## 5. Executando o Backend

### 5.1. Com Docker (Recomendado)

A maneira mais fácil de executar o backend é com o Docker Compose.

```bash
# A partir da raiz do projeto
docker-compose up --build -d backend
```

A API estará disponível em `http://localhost:8001`, e a documentação interativa (Swagger UI) em `http://localhost:8001/docs`.

### 5.2. Manualmente

**Pré-requisitos:**

*   Python 3.9+
*   Um ambiente virtual (`venv`)

```bash
# A partir de packages/backend/
# 1. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Linux/macOS
# ou
.\venv\Scripts\Activate.ps1 # No Windows

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Crie o arquivo .env e adicione suas chaves de API

# 4. Inicie o servidor
uvicorn src.backend_projeto.main:app --reload --host 0.0.0.0 --port 8001
```

## 6. Testes

O projeto utiliza `pytest` para testes.

```bash
# A partir de packages/backend/
# Certifique-se de que seu ambiente virtual está ativado
pytest
```

Para executar os testes e gerar um relatório de cobertura:

```bash
pytest --cov=src/backend_projeto --cov-report=html
```
