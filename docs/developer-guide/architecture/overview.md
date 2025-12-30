# Documentação da Arquitetura

Este documento fornece uma visão detalhada da arquitetura, funcionalidades e configuração da plataforma de análise de investimentos.

## 1. Visão Geral

A plataforma é composta por um frontend moderno e um backend robusto de análise financeira.

**Backend (API & Análise):**
Construído com **FastAPI**, serve como o cérebro da plataforma, realizando análises financeiras complexas (Otimização de Portfólio, VaR, Monte Carlo) e fornecendo uma API RESTful.
*   **Tecnologias:** FastAPI, Pydantic, Pandas, NumPy, SciPy, scikit-learn.

**Frontend (Interface & Visualização):**
Uma Single-Page Application (SPA) construída com **Next.js** que oferece uma experiência de usuário interativa e rica em dados.
*   **Tecnologias:** Next.js (App Router), TypeScript, Tailwind CSS, Framer Motion (animações), Recharts (gráficos), Shadcn/ui (componentes).

## 2. Arquitetura do Backend

A arquitetura do backend é modular e organizada da seguinte forma:

```
packages/backend/
├── src/backend_projeto/
│   ├── api/                  # Endpoints da API (roteadores)
│   ├── domain/               # Lógica de negócio (DDD)
│   │   ├── analysis.py       # Entry point de análise (re-exports)
│   │   ├── risk_metrics.py   # VaR, ES, Drawdown
│   │   ├── stress_testing.py # Testes de estresse
│   │   ├── covariance.py     # Covariância, atribuição de risco
│   │   ├── fama_french.py    # Modelos FF3 e FF5
│   │   ├── risk_engine.py    # Orquestração de risco
│   │   ├── portfolio_analyzer.py # Análise de portfólio
│   │   ├── entities.py       # Entidades de domínio
│   │   ├── value_objects.py  # Value Objects
│   │   ├── services.py       # Serviços de domínio
│   │   └── repositories.py   # Interfaces de repositório
│   ├── infrastructure/       # Implementações concretas
│   │   ├── data_handling.py  # Processamento de dados
│   │   └── visualization/    # Geração de gráficos
│   ├── application/          # Casos de uso
│   ├── utils/                # Utilitários (config, logging)
│   ├── cache/                # Lógica de cache
│   └── main.py               # Ponto de entrada FastAPI
├── tests/                    # Testes Pytest
├── scripts/                  # Scripts de análise
├── requirements.txt          # Dependências Python
└── backend.Dockerfile        # Dockerfile
```

### 2.1. `src/backend_projeto/api/`

Este diretório contém os roteadores do FastAPI, onde cada arquivo corresponde a uma categoria de endpoints (e.g., `risk_endpoints.py`, `optimization_endpoints.py`). Esta estrutura modular facilita a organização e manutenção do código, permitindo que cada arquivo de roteador defina um conjunto de operações relacionadas. Cada endpoint é tipado usando Pydantic para validação de entrada e serialização de saída, garantindo a robustez da API.

### 2.2. `src/backend_projeto/domain/`

O coração da aplicação, contendo a lógica de negócio pura seguindo princípios de DDD:

**Módulos de Análise Financeira (v1.6.0):**

| Módulo | Responsabilidade |
|--------|------------------|
| `analysis.py` | Entry point - re-exporta funções para compatibilidade |
| `risk_metrics.py` | VaR (paramétrico, histórico, EVT), ES, Drawdown |
| `stress_testing.py` | Testes de estresse, backtesting de VaR |
| `covariance.py` | Matriz Ledoit-Wolf, atribuição de risco, VaR incremental/marginal |
| `fama_french.py` | Modelos Fama-French FF3 e FF5 |
| `risk_engine.py` | Classe `RiskEngine` - orquestração de análises |
| `portfolio_analyzer.py` | Classe `PortfolioAnalyzer` - análise completa de portfólio |

**Componentes DDD:**

| Componente | Arquivo | Descrição |
|------------|---------|-----------|
| **Entities** | `entities.py` | `Portfolio`, `Transaction`, `Position`, `User` |
| **Value Objects** | `value_objects.py` | `Money`, `Percentage`, `Ticker`, `DateRange` |
| **Services** | `services.py` | `RiskCalculationService`, `PortfolioOptimizationService` |
| **Repositories** | `repositories.py` | Interfaces: `IPortfolioRepository`, `IMarketDataRepository` |
| **Exceptions** | `exceptions.py` | `AppError`, `DataProviderError` |

### 2.3. `src/backend_projeto/infrastructure/`

Implementações concretas dos contratos do domínio:
- **data_handling.py**: Processamento de arquivos de transação
- **data_providers/**: APIs externas (yfinance, Alpha Vantage, Finnhub)
- **visualization/**: Geração de gráficos

### 2.4. `src/backend_projeto/utils/`

Contém módulos utilitários para tarefas como carregamento de configurações (`config.py`), logging, e rate limiting.

### 2.5. `src/backend_projeto/main.py`

Este é o ponto de entrada da aplicação FastAPI. Ele inicializa a aplicação, inclui os roteadores da API, e configura os middlewares (CORS, rate limiting, etc.).

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
