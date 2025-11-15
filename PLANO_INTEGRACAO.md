# 📋 Plano de Integração Backend ↔ Frontend

**Data:** 12 de Novembro de 2025  
**Status:** Planejamento Estruturado  
**Versão:** 1.0

---

## 📑 Índice

1. [Visão Geral](#visão-geral)
2. [Mapeamento da Arquitetura](#mapeamento-da-arquitetura)
3. [Mapeamento de Endpoints](#mapeamento-de-endpoints)
4. [Estrutura de Tipos Compartilhados](#estrutura-de-tipos-compartilhados)
5. [Fases de Implementação](#fases-de-implementação)
6. [Configurações de Ambiente](#configurações-de-ambiente)
7. [Segurança e Autenticação](#segurança-e-autenticação)
8. [Padrão de Tratamento de Erros](#padrão-de-tratamento-de-erros)
9. [Testes de Integração](#testes-de-integração)
10. [Checklist de Deploy](#checklist-de-deploy)

---

## 🎯 Visão Geral

### Objetivo
Estabelecer uma integração robusta e tipada entre o backend FastAPI (`packages/backend`) e o frontend Next.js/React (`packages/frontend`), com tipos compartilhados via `packages/shared-types`.

### Stack Atual
- **Backend:** FastAPI 0.109.0, Pydantic 2.12.4, Python 3.9+
- **Frontend:** Next.js (React 18), TypeScript, Axios 1.12.2, Zod
- **Tipos Compartilhados:** TypeScript, Zod
- **Comunicação:** REST API (HTTP/JSON)

### Problemas a Resolver
- ✅ Contrato de API não formalizado
- ✅ Cliente API do frontend desatualizado
- ✅ Tipos duplicados (backend Pydantic + frontend Zod)
- ✅ Variáveis de ambiente não centralizadas
- ✅ Sem autenticação/autorização estruturada
- ✅ Falta de tratamento de erros padronizado
- ✅ Sem testes de contrato/integração

---

## 📦 Mapeamento da Arquitetura

### Estrutura do Workspace (Monorepo)

```
AndrehSatoru.com/
├── package.json (root - pnpm workspace)
├── pnpm-workspace.yaml
├── README.md
│
├── packages/
│   ├── backend/
│   │   ├── src/backend_projeto/
│   │   │   ├── main.py               ← FastAPI app + middlewares
│   │   │   ├── run.py                ← Entry point
│   │   │   ├── api/                  ← Routers modulares
│   │   │   ├── core/                 ← Lógica de negócio
│   │   │   ├── utils/                ← Config, logging, rate limiting
│   │   │   └── cache/                ← Cache em memória/Redis
│   │   ├── tests/                    ← Pytest fixtures
│   │   ├── requirements.txt
│   │   ├── pytest.ini
│   │   ├── docker-compose.yml
│   │   ├── backend.Dockerfile
│   │   ├── README.md
│   │   └── scripts/                  ← Análises e demos
│   │
│   ├── frontend/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx              ← Dashboard principal
│   │   │   ├── enviar/page.tsx       ← Form envio operações
│   │   │   ├── api/                  ← API routes (if needed)
│   │   │   └── globals.css
│   │   ├── components/               ← ~24 componentes visuais
│   │   ├── hooks/                    ← use-mobile, use-toast
│   │   ├── lib/
│   │   │   └── backend-api.ts        ← CLIENT API (atualmente simples)
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── next.config.mjs
│   │
│   └── shared-types/
│       ├── src/index.ts              ← Tipos compartilhados (Zod + TS)
│       └── package.json
```

### Fluxo de Dados Atual

```
Frontend (Next.js)
    ↓
[axios.post] → http://localhost:8000/api/v1/...
    ↓
Backend (FastAPI)
    ├── CORSMiddleware
    ├── RateLimiter
    ├── LoggingMiddleware
    └── [Routers] → Response (JSON)
    ↓
[Frontend] recebe JSON + tipa manualmente
```

---

## 🔌 Mapeamento de Endpoints

### Categorias de Endpoints

#### 1️⃣ **Sistema (`/system`)**
| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| GET | `/system/health` | Health check | ✓ Existe |
| GET | `/system/config` | Configurações públicas | ✓ Existe |
| POST | `/system/ping` | Ping com latência | ✓ Existe |

#### 2️⃣ **Dados (`/data`)**
| Método | Endpoint | Descrição | Arquivo |
|--------|----------|-----------|---------|
| POST | `/data/prices` | Fetch preços históricos | `data_endpoints.py` |
| POST | `/data/dividends` | Fetch dividendos | `data_endpoints.py` |
| POST | `/data/splits` | Fetch splits | `data_endpoints.py` |

#### 3️⃣ **Risco (`/risk`)** - Core
| Método | Endpoint | Descrição | Arquivo |
|--------|----------|-----------|---------|
| POST | `/risk/var` | Value at Risk | `risk_endpoints.py` |
| POST | `/risk/es` | Expected Shortfall / CVaR | `risk_endpoints.py` |
| POST | `/risk/drawdown` | Máximo Drawdown | `risk_endpoints.py` |
| POST | `/risk/stress` | Teste de Estresse | `risk_endpoints.py` |
| POST | `/risk/backtest` | Backtesting VaR | `risk_endpoints.py` |

#### 4️⃣ **Risco (`/risk`)** - Avançado
| Método | Endpoint | Descrição | Arquivo |
|--------|----------|-----------|---------|
| POST | `/risk/ivar` | Incremental VaR | `risk_endpoints.py` |
| POST | `/risk/mvar` | Marginal VaR | `risk_endpoints.py` |
| POST | `/risk/relvar` | VaR Relativo (vs benchmark) | `risk_endpoints.py` |
| POST | `/risk/monte-carlo` | Simulação Monte Carlo | `risk_endpoints.py` |

#### 5️⃣ **Otimização (`/optimization`)**
| Método | Endpoint | Descrição | Arquivo |
|--------|----------|-----------|---------|
| POST | `/optimization/markowitz` | Portfólio ótimo Markowitz | `optimization_endpoints.py` |
| POST | `/optimization/bl` | Black-Litterman | `optimization_endpoints.py` |
| POST | `/optimization/frontier` | Fronteira Eficiente | `optimization_endpoints.py` |
| POST | `/optimization/bl-frontier` | BL Fronteira Eficiente | `optimization_endpoints.py` |

#### 6️⃣ **Análise Técnica (`/technical-analysis`)**
| Método | Endpoint | Descrição | Arquivo |
|--------|----------|-----------|---------|
| POST | `/technical-analysis/ma` | Médias Móveis (SMA/EMA) | `technical_analysis_endpoints.py` |
| POST | `/technical-analysis/macd` | MACD | `technical_analysis_endpoints.py` |
| POST | `/technical-analysis/plot-ta` | Gráfico TA (PNG) | `technical_analysis_endpoints.py` |

#### 7️⃣ **Portfólio (`/portfolio`)**
| Método | Endpoint | Descrição | Arquivo |
|--------|----------|-----------|---------|
| POST | `/portfolio/weights-series` | Série de pesos (buy-hold) | `portfolio_endpoints.py` |
| POST | `/portfolio/processar_operacoes` | Processar transações | `transaction_endpoints.py` |

#### 8️⃣ **Visualizações (`/visualization`)**
| Método | Endpoint | Descrição | Arquivo |
|--------|----------|-----------|---------|
| POST | `/visualization/efficient-frontier` | Gráfico Fronteira | `visualization_endpoints.py` |
| POST | `/visualization/comprehensive-charts` | Múltiplos gráficos | `visualization_endpoints.py` |
| POST | `/visualization/stress-test` | Gráfico Teste Estresse | `visualization_endpoints.py` |

#### 9️⃣ **Fatores (`/factors`)**
| Método | Endpoint | Descrição | Arquivo |
|--------|----------|-----------|---------|
| POST | `/factors/ff3` | Fama-French 3 | `factor_endpoints.py` |
| POST | `/factors/ff5` | Fama-French 5 | `factor_endpoints.py` |
| POST | `/factors/capm` | CAPM | `factor_endpoints.py` |
| POST | `/factors/apt` | APT (multifatorial) | `factor_endpoints.py` |
| POST | `/factors/ff3-plot` | FF3 Plot (PNG) | `factor_endpoints.py` |

#### 🔟 **Dashboard (`/dashboard`)**
| Método | Endpoint | Descrição | Arquivo |
|--------|----------|-----------|---------|
| POST | `/dashboard/summary` | Resumo geral | `dashboard_endpoints.py` |
| POST | `/dashboard/full` | Dashboard completo | `dashboard_endpoints.py` |

---

## 📝 Estrutura de Tipos Compartilhados

### Localização Atual

**Arquivo:** `packages/shared-types/src/index.ts`

```typescript
// Operações (transações)
OperacaoSchema = {
  data: string
  ticker: string
  tipo: "compra" | "venda"
  valor: number
}

BodySchema = {
  valorInicial: number
  dataInicial: string
  operacoes: Operacao[]
}
```

### Tipos a Sincronizar com Backend

Mapear todos os Pydantic models do backend → Zod schemas no `shared-types`:

**Backend Models** (`src/backend_projeto/api/models.py`):
- `PricesRequest` / `PricesResponse`
- `VarRequest` / `VarResponse`
- `EsRequest` / `RiskResponse`
- `DrawdownRequest` / `StressRequest` / `BacktestRequest`
- `MonteCarloRequest` / `MonteCarloSamplesRequest`
- `OptimizeRequest` / `BLRequest` / `FrontierRequest`
- `TAMovingAveragesRequest` / `TAMacdRequest`
- `IVaRRequest` / `MVaRRequest` / `RelVaRRequest`
- `FF3Request` / `FF5Request` / `FFFactorsPlotRequest`
- `WeightsSeriesRequest` / `WeightsSeriesResponse`
- `FrontierDataResponse`
- `ComprehensiveChartsRequest` / `ComprehensiveChartsResponse`

### Novo Padrão de Organização

```
shared-types/src/
├── index.ts                  ← Re-export de tudo
├── types/
│   ├── common.ts             ← Tipos base, erros
│   ├── risk.ts               ← VaR, ES, Drawdown, etc
│   ├── optimization.ts       ← Markowitz, BL, Frontier
│   ├── portfolio.ts          ← Portfólio, transações
│   ├── technical-analysis.ts ← MA, MACD
│   └── factors.ts            ← FF3, FF5, CAPM, APT
└── schemas/
    ├── risk.ts               ← Zod schemas para validação
    ├── portfolio.ts
    └── ...
```

---

## 🚀 Fases de Implementação

### **Fase 1: Contrato de API (Semana 1)**

**Objetivo:** Formalizar o contrato entre backend e frontend.

#### 1.1 Revisar e Documentar Endpoints
- [x] Ler completamente `endpoints.py` (812 linhas)
- [x] Ler todos os routers: `risk_`, `optimization_`, `visualization_`, etc.
- [x] Documentar inputs/outputs de cada endpoint
- [x] Mapear status codes esperados (200, 400, 422, 500)

#### 1.2 Gerar OpenAPI/Swagger
- [x] FastAPI já gera `/docs` automático → revisar em `http://localhost:8000/docs`
- [x] Exportar OpenAPI spec: `http://localhost:8000/openapi.json`
- [x] Salvar em `packages/backend/openapi.json`

#### 1.3 Criar Tipos Compartilhados (TypeScript/Zod)
- [x] Sincronizar todos os Pydantic models → Zod schemas
- [x] Organizar em `packages/shared-types/src/types/` por categoria
- [x] Adicionar exemplos de payload/response
- [x] Gerar tipos TS para cada request/response

**Deliverable:** `shared-types/src/index.ts` com 100% dos tipos do backend

---

### **Fase 2: Cliente API Tipado (Semana 2)**

**Objetivo:** Gerar/implementar cliente HTTP tipado no frontend.

#### 2.1 Setup de Variáveis de Ambiente
- [x] Criar `.env.example` no frontend:
  ```
  NEXT_PUBLIC_API_URL=http://localhost:8000
  NEXT_PUBLIC_API_TIMEOUT=30000
  ```
- [x] Atualizar `next.config.mjs` se necessário
- [x] Documentar em `FRONTEND_INTEGRATION.md`

#### 2.2 Implementar Backend API Client
- [x] Implementar cliente API tipado usando `Zodios` e os `endpoints` gerados.
- [x] Manter interceptors de autenticação, tratamento de erros e retry.

#### 2.3 Implementar Hook Customizado
- [x] Implementar `useApi` hook para gerenciar estados de requisição (loading, error, data).

**Deliverable:** `backend-api.ts` + `use-api.ts` totalmente tipados

---

### **Fase 3: Autenticação & Autorização (Semana 3)**

**Objetivo:** Implementar fluxo seguro de autenticação.

#### 3.1 Backend - Setup JWT
- [x] Adicionar middleware de autenticação em `main.py`
- [x] Implementar endpoints `/auth/login` e `/auth/refresh`
- [x] Usar `python-jose` + `passlib` (já em requirements.txt)
- [x] Armazenar tokens em Redis com TTL

#### 3.2 Frontend - Secure Token Storage
- [x] Implementar `useAuthStore` (Zustand ou Context API)
- [x] Armazenar token em httpOnly cookie OU localStorage com proteção
- [x] Implementar interceptor automático no axios
- [x] Proteger rotas: `/dashboard` requer token válido

#### 3.3 Refresh Token Flow
- [x] Detectar token expirado (status 401)
- [x] Chamar `/auth/refresh` automaticamente
- [x] Retry request original
- [x] Logout se refresh falhar

**Deliverable:** Login funcional end-to-end com refresh automático

---

### **Fase 4: Tratamento de Erros Padrão (Semana 3)**

**Objetivo:** Padronizar respostas de erro.

#### 4.1 Backend - Error Response Schema
- [x] Definir `ApiErrorResponse` em `backend_projeto/core/exceptions.py`.

#### 4.2 Mapear Exceções Python → HTTP
- [x] `DataProviderError` → 503 Service Unavailable
- [x] `DataValidationError` → 422 Unprocessable Entity
- [x] `InvalidTransactionFileError` → 400 Bad Request
- [x] `AppError` → 500 Internal Server Error

#### 4.3 Frontend - Error Handling
- [x] Implementar tratamento de erros padronizado no `backend-api.ts` usando `toast` para exibir mensagens.

**Deliverable:** Tratamento de erros consistente backend ↔ frontend

---

### **Fase 5: Testes de Integração (Semana 4)**

**Objetivo:** Validar contrato e fluxos E2E.

#### 5.1 Testes de Contrato (Pact)
```bash
# Em packages/backend/tests/
pytest tests/test_api_contracts.py
```
- [ ] Validar cada endpoint contra schema OpenAPI
- [ ] Verificar tipos de campos
- [ ] Testar status codes

#### 5.2 Testes E2E (Playwright)
```bash
# Em packages/frontend/
pnpm test:e2e
```
- [ ] Fluxo: Dashboard → Enviar Operações → Processar
- [ ] Fluxo: Autenticação → Acesso Dashboard
- [ ] Fluxo: Erro no backend → Toast de erro no frontend

**Deliverable:** Suite de testes com >80% cobertura

---

### **Fase 6: CI/CD e Staging (Semana 4-5)**

**Objetivo:** Automatizar deploy e testes.

#### 6.1 GitHub Actions / Pipeline
- [ ] Rodar testes backend (pytest)
- [ ] Rodar testes frontend (Jest/Playwright)
- [ ] Build Docker images
- [ ] Deploy para staging

#### 6.2 Smoke Tests Pós-Deploy
```python
# scripts/smoke_tests.py
POST /system/health → 200 OK
POST /data/prices (sample) → 200 OK
POST /risk/var (sample) → 200 OK
```

**Deliverable:** Staging environment com backend + frontend integrados

---

## ⚙️ Configurações de Ambiente

### Backend (`.env` ou `docker-compose.yml`)

```ini
# API
CORS_ORIGINS=http://localhost:3000,http://frontend:3000
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60

# Cache
CACHE_ENABLED=true
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET_KEY=<random-secret-key-32-chars>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Data Providers
FINNHUB_API_KEY=<your-key>
ALPHA_VANTAGE_API_KEY=<your-key>
```

### Frontend (`.env.local` no gitignore)

```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_LOG_LEVEL=debug
```

### Root (pnpm monorepo)

```ini
# pnpm-workspace.yaml
packages:
  - "packages/*"
```

---

## 🔐 Segurança e Autenticação

### 1. CORS (Content-Origin Resource Sharing)
✓ **Já configurado em `main.py`**
```python
origins = [o.strip() for o in config.CORS_ORIGINS if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, ...)
```

### 2. Rate Limiting
✓ **Já implementado em `main.py`**
```python
if config.RATE_LIMIT_ENABLED:
    app.state.rate_limiter = InMemoryRateLimiter(...)
```

### 3. JWT Authentication (A IMPLEMENTAR)
- [ ] Backend: Gerar JWT em `/auth/login`
- [ ] Frontend: Enviar `Authorization: Bearer <token>` em headers
- [ ] Backend: Validar JWT em middleware
- [ ] Frontend: Armazenar em httpOnly cookie (seguro contra XSS)

### 4. HTTPS em Produção
- [ ] Usar certificados Let's Encrypt
- [ ] Redirecionar HTTP → HTTPS
- [ ] Configurar HSTS header

### 5. Rate Limiting por IP/Usuário
- [ ] Usar Redis para contador distribuído
- [ ] Limite: 100 req/min por IP; 1000 req/dia por usuário

---

## 📊 Padrão de Tratamento de Erros

### Response de Sucesso

```json
{
  "result": {
    "var": 0.0342,
    "method": "historical",
    "alpha": 0.05
  }
}
```

### Response de Erro (400-level)

```json
{
  "error": "validation_error",
  "message": "Validação de dados falhou",
  "status_code": 422,
  "details": {
    "assets": ["assets não pode ser vazio"],
    "start_date": ["start_date > end_date"]
  },
  "request_id": "req-1731415200000"
}
```

### Response de Erro (500-level)

```json
{
  "error": "data_provider_error",
  "message": "Falha ao buscar dados do Yahoo Finance",
  "status_code": 503,
  "details": {
    "provider": "yfinance",
    "retry_after": 60
  },
  "request_id": "req-1731415201000"
}
```

### Códigos de Erro Padrão

| Código | HTTP | Descrição |
|--------|------|-----------|
| `validation_error` | 422 | Falha na validação de input |
| `invalid_request` | 400 | Request malformado |
| `data_provider_error` | 503 | Falha ao buscar dados |
| `data_validation_error` | 422 | Dados inconsistentes |
| `invalid_transaction_file` | 400 | Arquivo de transações inválido |
| `unauthorized` | 401 | Token inválido/expirado |
| `forbidden` | 403 | Sem permissão |
| `internal_server_error` | 500 | Erro interno |

---

## 🧪 Testes de Integração

### Backend (pytest)

```bash
# Rodar testes
cd packages/backend
pytest tests/ -v --cov=src --cov-report=html

# Testes específicos
pytest tests/test_api_contracts.py -k "test_risk_var"
pytest tests/integration/ -k "test_portfolio_processing"
```

### Frontend (Playwright + Jest)

```bash
# Testes unitários
cd packages/frontend
pnpm test

# Testes E2E
pnpm test:e2e

# Com headless UI
pnpm test:e2e --headed
```

### Contrato (OpenAPI Validator)

```bash
# Validar responses contra spec OpenAPI
pnpm test:contract

# Gerar relatório
pnpm test:contract --report json
```

---

## ✅ Checklist de Deploy

### Pré-Deploy (Staging)

- [ ] Todos os testes passando (frontend + backend)
- [ ] Cobertura de testes ≥ 80%
- [ ] Código revisado (pull request)
- [ ] Variáveis de ambiente configuradas
- [ ] CORS liberado para staging domain
- [ ] SSL/HTTPS habilitado
- [ ] Rate limiting ativo
- [ ] Logging centralizado (ex: CloudWatch)
- [ ] Backups de banco de dados configurados
- [ ] Performance: API responde em < 2s (P95)

### Deploy para Produção

- [ ] Health check verde em staging por 24h
- [ ] Smoke tests passando
- [ ] Plano de rollback preparado
- [ ] Logs e alertas monitorados
- [ ] CDN configurado (se aplicável)
- [ ] WAF (Web Application Firewall) ativo
- [ ] Rate limiting ajustado para prod
- [ ] Backup banco antes de deploy
- [ ] Comunicação com stakeholders
- [ ] Feature flags para rollback rápido

### Pós-Deploy

- [ ] Monitorar CPU/Memória/Disco
- [ ] Monitorar latência das requisições
- [ ] Verificar logs de erro (0 erros críticos esperado)
- [ ] Testar principais fluxos manualmente
- [ ] Validar métricas de negócio

---

## 📚 Arquivos a Criar/Modificar

### Novos Arquivos

```
packages/
├── shared-types/
│   └── src/
│       ├── types/
│       │   ├── common.ts
│       │   ├── risk.ts
│       │   ├── optimization.ts
│       │   ├── portfolio.ts
│       │   ├── technical-analysis.ts
│       │   └── factors.ts
│       └── schemas/
│           ├── risk.ts
│           ├── portfolio.ts
│           └── common.ts
│
├── frontend/
│   ├── hooks/
│   │   ├── use-api.ts (NEW)
│   │   ├── use-auth.ts (NEW)
│   │   └── use-toast.ts (existing)
│   ├── lib/
│   │   ├── backend-api.ts (UPDATE)
│   │   ├── auth.ts (NEW)
│   │   └── errors.ts (NEW)
│   ├── .env.example (NEW)
│   └── INTEGRATION.md (NEW)
│
└── backend/
    ├── src/backend_projeto/
    │   ├── api/
    │   │   ├── auth_endpoints.py (NEW)
    │   │   ├── models.py (UPDATE)
    │   │   └── deps.py (UPDATE)
    │   ├── core/
    │   │   ├── auth.py (NEW)
    │   │   └── exceptions.py (UPDATE)
    │   └── utils/
    │       └── config.py (UPDATE)
    ├── tests/
    │   ├── test_api_contracts.py (NEW)
    │   └── integration/
    │       └── test_e2e.py (NEW)
    ├── .env.example (UPDATE)
    └── FRONTEND_INTEGRATION.md (NEW)
```

### Arquivos a Atualizar

1. `packages/shared-types/src/index.ts` → Sincronizar tipos
2. `packages/frontend/lib/backend-api.ts` → Novo client
3. `packages/frontend/package.json` → Adicionar deps (zod se necessário)
4. `packages/backend/src/backend_projeto/main.py` → Auth middleware
5. `packages/backend/requirements.txt` → Se necessário adicionar
6. Root `package.json` → Scripts de test integrado

---

## 🔄 Fluxo de Trabalho Recomendado

```
1. PLANNNG (atual)
   └─→ Revisar este documento
       └─→ Validar com stakeholders

2. FASE 1: Tipos & Contrato
   ├─→ Sync shared-types/
   ├─→ Exportar OpenAPI spec
   └─→ PR: "feat: definir contrato API"

3. FASE 2: Cliente Tipado
   ├─→ Impl backend-api.ts
   ├─→ Impl use-api hook
   └─→ PR: "feat: cliente API tipado"

4. FASE 3: Autenticação
   ├─→ Backend JWT
   ├─→ Frontend Auth Store
   └─→ PR: "feat: autenticação JWT"

5. FASE 4: Erros & Logging
   ├─→ Padronizar respostas
   ├─→ Logging centralizado
   └─→ PR: "feat: tratamento erros padronizado"

6. FASE 5: Testes
   ├─→ Testes contrato (pact)
   ├─→ Testes E2E (playwright)
   └─→ PR: "test: suite testes integração"

7. FASE 6: CI/CD
   ├─→ GitHub Actions
   ├─→ Deploy staging
   └─→ PR: "ci: setup CI/CD pipeline"

8. DEPLOY PRODUÇÃO
   ├─→ Smoke tests OK
   ├─→ Monitoramento OK
   └─→ Release 🚀
```

---

## 📞 Contatos & Referências

- **Backend FastAPI Docs:** http://localhost:8000/docs
- **Frontend Dev Server:** http://localhost:3000
- **OpenAPI Spec:** http://localhost:8000/openapi.json

### Documentação Existente

- `packages/backend/README.md` - Setup backend
- `packages/backend/API_QUICKSTART.md` - Exemplos de uso
- `packages/backend/CONFIGURATION.md` - Variáveis de ambiente
- `packages/backend/DEPLOYMENT.md` - Deploy em produção

---

## 📊 Progresso

- [x] Levantamento de requisitos
- [x] Mapeamento de endpoints
- [x] Planejamento de fases
- [x] Fase 1: Contrato (Concluído)
- [x] Fase 2: Cliente (Concluído)
- [x] Fase 3: Autenticação (Concluído)
- [x] Fase 4: Erros (Concluído)
- [ ] Fase 5: Testes (Próxima)
- [ ] Fase 6: CI/CD
- [ ] Deploy produção

---

**Documento criado em:** 12/11/2025  
**Próxima revisão:** Após Fase 1
