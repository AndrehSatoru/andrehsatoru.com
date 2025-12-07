# 🚀 Plano de Otimização - AndrehSatoru.com

## Resumo Executivo

Análise completa identificou **45+ problemas** de performance e memória:
- **Backend**: 27 problemas (3 críticos, 8 altos)
- **Frontend**: 18 problemas (5 altos)

**Ganho estimado após otimizações:**
- ⏱️ Tempo de resposta: **-70%**
- 💾 Uso de memória: **-40%**
- 🌐 Chamadas API externas: **-90%**
- 📦 Bundle size: **-30%**

---

## 📅 Roadmap de Implementação

### Fase 1: Quick Wins (1-2 dias)
**Esforço: Baixo | Impacto: Alto**

### Fase 2: Otimizações Core (3-5 dias)
**Esforço: Médio | Impacto: Alto**

### Fase 3: Refinamentos (1 semana)
**Esforço: Alto | Impacto: Médio**

---

## 🔴 FASE 1: Quick Wins

### 1.1 Backend - Remover Debug Prints
**Arquivo:** `packages/backend/src/backend_projeto/infrastructure/data_handling.py`
```python
# REMOVER linha 19:
print("DEBUG: LOADING DATA HANDLING MODULE")
```

### 1.2 Backend - Batch de Tickers no Endpoint
**Arquivo:** `packages/backend/src/backend_projeto/api/transaction_endpoints.py`

**Antes (N chamadas à API):**
```python
for op in body.operacoes:
    prices_df = loader.fetch_stock_prices([op.ticker], start_date, end_date)
```

**Depois (1 chamada à API):**
```python
# Coletar todos os tickers primeiro
all_tickers = list(set(op.ticker for op in body.operacoes))
min_date = min(op.data for op in body.operacoes) - timedelta(days=7)
max_date = max(op.data for op in body.operacoes) + timedelta(days=7)

# Fetch único
all_prices = loader.fetch_stock_prices(all_tickers, min_date, max_date)

# Processar operações usando dados em memória
for op in body.operacoes:
    ticker_prices = all_prices[op.ticker] if op.ticker in all_prices.columns else all_prices
    # ... resto do processamento
```

### 1.3 Frontend - Remover Interceptors Duplicados
**Arquivo:** `packages/frontend/lib/axios.ts`

O arquivo tem interceptors duplicados nas linhas 24-56 e 61-118. Remover a duplicação.

### 1.4 Frontend - Remover `unoptimized: true`
**Arquivo:** `packages/frontend/next.config.mjs`

```javascript
// REMOVER:
images: {
  unoptimized: true,
}

// SUBSTITUIR POR:
images: {
  formats: ['image/avif', 'image/webp'],
  deviceSizes: [640, 750, 828, 1080, 1200],
}
```

### 1.5 Frontend - Remover console.logs
**Arquivos:**
- `packages/frontend/app/api/frontier-data/route.ts` (linhas 19-21)
- `packages/frontend/components/efficient-frontier.tsx` (linhas 228, 324)
- `packages/frontend/components/dashboard-context.tsx` (linhas 39-40)

---

## 🟡 FASE 2: Otimizações Core

### 2.1 Backend - Análise Sob Demanda
**Arquivo:** `packages/backend/src/backend_projeto/domain/portfolio_analyzer.py`

**Problema:** `run_analysis()` executa ~20 análises mesmo quando usuário precisa de apenas 1-2.

**Solução:**
```python
def run_analysis(self, analyses: List[str] = None) -> PortfolioAnalysisResponse:
    """
    Executa análises especificadas ou todas se None.
    
    Args:
        analyses: Lista de análises desejadas. Opções:
            - 'performance': Métricas de performance
            - 'allocation': Alocação atual
            - 'risk': Métricas de risco
            - 'monte_carlo': Simulação Monte Carlo
            - 'correlation': Matriz de correlação
            - 'drawdown': Análise de drawdown
            - 'fama_french': Análise Fama-French
            - 'capm': Análise CAPM
            - 'beta': Análise de Beta
            - 'tmfg': Grafo TMFG
            - 'efficient_frontier': Fronteira eficiente
    """
    available_analyses = {
        'performance': self._generate_performance_series,
        'allocation': self.analyze_allocation,
        'risk': self._calculate_risk_metrics,
        'monte_carlo': self._generate_monte_carlo_simulation,
        'correlation': self._generate_correlation_matrix,
        'drawdown': self._generate_drawdown_data,
        'fama_french': self._generate_fama_french_panel,
        'capm': self._calculate_capm_metrics,
        'beta': self._generate_beta_data,
        'tmfg': self._generate_tmfg_graph,
        'efficient_frontier': self._generate_efficient_frontier,
    }
    
    if analyses is None:
        analyses = list(available_analyses.keys())
    
    # Fetch dados uma única vez
    self._ensure_data_loaded()
    
    results = {}
    for name in analyses:
        if name in available_analyses:
            results[name] = available_analyses[name]()
    
    return self._build_response(results)
```

### 2.2 Backend - Cache Único de Dados
**Arquivo:** `packages/backend/src/backend_projeto/domain/portfolio_analyzer.py`

```python
class PortfolioAnalyzer:
    def __init__(self, ...):
        # ... existing code ...
        self._cached_prices = None
        self._cached_returns = None
        self._cached_benchmark = None
    
    def _ensure_data_loaded(self):
        """Carrega todos os dados necessários uma única vez."""
        if self._cached_prices is None:
            self._cached_prices = self._fetch_all_prices()
            self._cached_returns = self._cached_prices.pct_change().dropna()
        if self._cached_benchmark is None:
            self._cached_benchmark = self._fetch_benchmark()
    
    @property
    def prices(self):
        self._ensure_data_loaded()
        return self._cached_prices
    
    @property
    def returns(self):
        self._ensure_data_loaded()
        return self._cached_returns
```

### 2.3 Backend - Vetorizar Loops iterrows()
**Arquivo:** `packages/backend/src/backend_projeto/domain/portfolio_analyzer.py`

**Problema 1 - Total Investido (linhas 89-93):**
```python
# ANTES:
self.total_invested = sum(
    row['Preco'] * row['Quantidade'] 
    for _, row in self.transactions.iterrows() 
    if row['Quantidade'] > 0
)

# DEPOIS:
mask = self.transactions['Quantidade'] > 0
self.total_invested = (
    self.transactions.loc[mask, 'Preco'] * 
    self.transactions.loc[mask, 'Quantidade']
).sum()
```

**Problema 2 - Processamento de Transações (linhas 125-142):**
```python
# ANTES:
for _, tx in self.transactions.iterrows():
    tx_date = pd.to_datetime(tx['Data']).normalize()
    # ...

# DEPOIS:
# Pré-processar datas uma vez
self.transactions['Data'] = pd.to_datetime(self.transactions['Data']).dt.normalize()

# Usar groupby para processar por data/ativo
for (date, asset), group in self.transactions.groupby(['Data', 'Ativo']):
    total_qty = group['Quantidade'].sum()
    # ...
```

### 2.4 Backend - Vetorizar Monte Carlo
**Arquivo:** `packages/backend/src/backend_projeto/domain/portfolio_analyzer.py`

```python
def _generate_monte_carlo_simulation(self, n_paths: int = 10000, n_days: int = 252):
    """Monte Carlo vetorizado - 10x mais rápido."""
    historical_returns = self.returns.mean(axis=1).values
    initial_value = self.current_portfolio_value
    
    # Gerar todos os paths de uma vez
    sampled_indices = np.random.randint(
        0, len(historical_returns), 
        size=(n_days, n_paths)
    )
    sampled_returns = historical_returns[sampled_indices]
    
    # Calcular paths cumulativos
    cumulative_returns = np.cumprod(1 + sampled_returns, axis=0)
    paths = initial_value * cumulative_returns
    
    # Calcular percentis
    percentiles = [5, 25, 50, 75, 95]
    results = {
        f'p{p}': np.percentile(paths, p, axis=1).tolist()
        for p in percentiles
    }
    
    return results
```

### 2.5 Frontend - Lazy Loading de Componentes
**Arquivo:** `packages/frontend/app/page.tsx`

```tsx
import dynamic from 'next/dynamic'
import { Skeleton } from '@/components/ui/skeleton'

// Componentes pesados com lazy loading
const EfficientFrontier = dynamic(
  () => import('@/components/efficient-frontier'),
  { loading: () => <Skeleton className="h-[500px]" />, ssr: false }
)

const TMFGGraph = dynamic(
  () => import('@/components/tmfg-graph'),
  { loading: () => <Skeleton className="h-[400px]" />, ssr: false }
)

const MonteCarloChart = dynamic(
  () => import('@/components/monte-carlo-chart'),
  { loading: () => <Skeleton className="h-[400px]" />, ssr: false }
)

const CorrelationMatrix = dynamic(
  () => import('@/components/correlation-matrix'),
  { loading: () => <Skeleton className="h-[400px]" />, ssr: false }
)

const DistanceCorrelationMatrix = dynamic(
  () => import('@/components/distance-correlation-matrix'),
  { loading: () => <Skeleton className="h-[400px]" />, ssr: false }
)

const FamaFrenchPanel = dynamic(
  () => import('@/components/fama-french-panel'),
  { loading: () => <Skeleton className="h-[400px]" />, ssr: false }
)
```

### 2.6 Frontend - Dividir Context
**Arquivo:** `packages/frontend/components/dashboard-context.tsx`

```tsx
// Criar stores separadas com Zustand
import { create } from 'zustand'

interface PerformanceStore {
  data: PerformanceData | null
  setData: (data: PerformanceData) => void
}

interface RiskStore {
  data: RiskData | null
  setData: (data: RiskData) => void
}

export const usePerformanceStore = create<PerformanceStore>((set) => ({
  data: null,
  setData: (data) => set({ data }),
}))

export const useRiskStore = create<RiskStore>((set) => ({
  data: null,
  setData: (data) => set({ data }),
}))

// Componentes usam apenas o que precisam
// Não re-renderizam quando outra parte do estado muda
```

---

## 🟢 FASE 3: Refinamentos

### 3.1 Backend - Cache Inteligente
**Arquivo:** `packages/backend/src/backend_projeto/infrastructure/data_handling.py`

```python
class SmartCache:
    """Cache que aproveita dados parciais."""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.memory_cache = {}
    
    def get_prices(self, tickers: List[str], start: date, end: date):
        """Busca preços aproveitando cache parcial."""
        result = {}
        missing = []
        
        for ticker in tickers:
            cached = self._get_cached_range(ticker, start, end)
            if cached is not None:
                result[ticker] = cached
            else:
                missing.append(ticker)
        
        if missing:
            new_data = self._fetch_from_api(missing, start, end)
            for ticker, data in new_data.items():
                self._update_cache(ticker, data)
                result[ticker] = data
        
        return pd.DataFrame(result)
    
    def _get_cached_range(self, ticker, start, end):
        """Verifica se há dados em cache para o range."""
        key = f"prices:{ticker}"
        if key in self.memory_cache:
            df = self.memory_cache[key]
            if df.index.min() <= start and df.index.max() >= end:
                return df.loc[start:end]
        return None
```

### 3.2 Backend - Usar scipy.optimize para Markowitz
**Arquivo:** `packages/backend/src/backend_projeto/domain/portfolio_analyzer.py`

```python
from scipy.optimize import minimize

def _optimize_portfolio(self, target: str = 'sharpe'):
    """Otimização convexa ao invés de Monte Carlo."""
    n_assets = len(self.assets)
    mean_returns = self.returns.mean() * 252
    cov_matrix = self.returns.cov() * 252
    
    def neg_sharpe(weights):
        port_return = np.dot(weights, mean_returns)
        port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -(port_return - self.risk_free_rate) / port_vol
    
    constraints = [
        {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Soma = 1
    ]
    bounds = [(0, 1) for _ in range(n_assets)]  # Long only
    
    result = minimize(
        neg_sharpe,
        x0=np.ones(n_assets) / n_assets,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    return result.x
```

### 3.3 Frontend - React Query para Cache de API
**Arquivo:** `packages/frontend/lib/api-hooks.ts`

```tsx
import { useQuery, useMutation, QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutos
      cacheTime: 30 * 60 * 1000, // 30 minutos
    },
  },
})

export function usePortfolioAnalysis(portfolioId: string) {
  return useQuery({
    queryKey: ['portfolio', portfolioId],
    queryFn: () => fetchPortfolioAnalysis(portfolioId),
    enabled: !!portfolioId,
  })
}

export function useFrontierData(assets: string[]) {
  return useQuery({
    queryKey: ['frontier', assets.sort().join(',')],
    queryFn: () => fetchFrontierData(assets),
    staleTime: 10 * 60 * 1000, // 10 minutos
  })
}
```

### 3.4 Frontend - Remover Dependências Não Utilizadas
**Arquivo:** `packages/frontend/package.json`

Auditar e potencialmente remover:
```json
{
  "dependencies": {
    // Provavelmente não utilizados - verificar:
    "@radix-ui/react-hover-card": "...",      // Remover se não usado
    "@radix-ui/react-menubar": "...",         // Remover se não usado
    "@radix-ui/react-navigation-menu": "...", // Remover se não usado
    "@radix-ui/react-collapsible": "...",     // Remover se não usado
    "embla-carousel-react": "...",            // Remover se não usado
    "input-otp": "...",                       // Remover se não usado
    "vaul": "...",                            // Remover se não usado
  }
}
```

### 3.5 Backend - Implementar Fallback de Cache
**Arquivo:** `packages/backend/src/backend_projeto/infrastructure/cache.py`

```python
from functools import lru_cache
from cachetools import TTLCache

class HybridCache:
    """Cache com Redis + fallback em memória."""
    
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = None
        self.memory_cache = TTLCache(maxsize=100, ttl=3600)
        
        try:
            import redis
            self.redis = redis.Redis(host=redis_host, port=redis_port)
            self.redis.ping()
        except Exception as e:
            logger.warning(f"Redis não disponível, usando cache em memória: {e}")
    
    def get(self, key: str):
        # Tentar Redis primeiro
        if self.redis:
            try:
                value = self.redis.get(key)
                if value:
                    return json.loads(value)
            except:
                pass
        
        # Fallback para memória
        return self.memory_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        # Salvar em ambos
        self.memory_cache[key] = value
        
        if self.redis:
            try:
                self.redis.setex(key, ttl, json.dumps(value))
            except:
                pass
```

---

## 📊 Métricas de Sucesso

### Antes das Otimizações
| Métrica | Valor Atual |
|---------|-------------|
| Tempo `/processar_operacoes` | ~30-60s |
| Memória pico backend | ~2GB |
| Chamadas yfinance/análise | ~20+ |
| Bundle size frontend | ~1.5MB |
| Time to Interactive | ~5s |

### Depois das Otimizações (Estimado)
| Métrica | Valor Esperado | Melhoria |
|---------|----------------|----------|
| Tempo `/processar_operacoes` | ~8-15s | **-70%** |
| Memória pico backend | ~1.2GB | **-40%** |
| Chamadas yfinance/análise | ~2-3 | **-90%** |
| Bundle size frontend | ~1MB | **-30%** |
| Time to Interactive | ~2s | **-60%** |

---

## 🔧 Checklist de Implementação

### Fase 1 (Quick Wins)
- [ ] Remover print debug em data_handling.py
- [ ] Implementar batch de tickers em transaction_endpoints.py
- [ ] Remover interceptors duplicados em axios.ts
- [ ] Remover `unoptimized: true` em next.config.mjs
- [ ] Remover console.logs de produção

### Fase 2 (Core)
- [ ] Implementar análise sob demanda em portfolio_analyzer.py
- [ ] Criar cache único de dados no analyzer
- [ ] Vetorizar loops iterrows()
- [ ] Vetorizar Monte Carlo
- [ ] Implementar lazy loading no frontend
- [ ] Dividir context em stores menores

### Fase 3 (Refinamentos)
- [ ] Implementar cache inteligente
- [ ] Usar scipy.optimize para Markowitz
- [ ] Implementar React Query
- [ ] Auditar e remover dependências não utilizadas
- [ ] Implementar fallback de cache

---

## 🔒 FASE 4: Correções de Segurança (CRÍTICO)

### 4.1 JWT Secret Key - Remover Valor Padrão Inseguro
**Arquivo:** `docker-compose.yml`

**ANTES (INSEGURO):**
```yaml
- JWT_SECRET_KEY=${JWT_SECRET_KEY:-dev-secret-key-change-in-production}
```

**DEPOIS (SEGURO):**
```yaml
- JWT_SECRET_KEY=${JWT_SECRET_KEY:?JWT_SECRET_KEY must be set in .env}
```

**Gerar chave segura:**
```bash
# Linux/Mac
openssl rand -base64 32

# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 4.2 Remover Usuário de Teste Hardcoded
**Arquivo:** `packages/backend/src/backend_projeto/application/auth.py`

**ANTES (INSEGURO):**
```python
dummy_user_password = get_password_hash("testpass")
dummy_users_db = {
    "testuser": User("testuser", "test@example.com", dummy_user_password),
}
```

**DEPOIS (SEGURO):**
```python
import os

# Usuários de teste apenas em desenvolvimento
if os.getenv("ENVIRONMENT", "development") == "development":
    dummy_user_password = get_password_hash("testpass")
    dummy_users_db = {
        "testuser": User("testuser", "test@example.com", dummy_user_password),
    }
else:
    dummy_users_db = {}
```

---

### 4.3 CORS - Configurar Origens Específicas
**Arquivo:** `packages/backend/src/backend_projeto/main.py`

**ANTES (INSEGURO):**
```python
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**DEPOIS (SEGURO):**
```python
import os

# CORS seguro - origens específicas em produção
if os.getenv("ENVIRONMENT") == "production":
    origins = os.getenv("CORS_ORIGINS", "https://andrehsatoru.com").split(",")
else:
    origins = ["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)
```

---

### 4.4 Cache - Substituir Pickle por JSON
**Arquivo:** `packages/backend/src/backend_projeto/infrastructure/utils/cache.py`

**ANTES (INSEGURO - RCE potencial):**
```python
import pickle

def get_dataframe(self, ...):
    cached_data = self.redis_client.get(key)
    if cached_data:
        return pickle.loads(cached_data)

def set_dataframe(self, df, ...):
    serialized_df = pickle.dumps(df)
    self.redis_client.setex(key, ttl, serialized_df)
```

**DEPOIS (SEGURO):**
```python
import json

def get_dataframe(self, prefix: str, assets: List[str], start_date: str, end_date: str) -> Optional[pd.DataFrame]:
    """Carrega DataFrame do cache Redis de forma segura."""
    if not self.redis_client:
        return None
        
    key = self._generate_key(prefix, assets, start_date, end_date)
    try:
        cached_data = self.redis_client.get(key)
        if cached_data:
            logging.info(f"[CACHE] HIT: Carregando '{key}' do Redis.")
            data = json.loads(cached_data)
            return pd.DataFrame(data)
        return None
    except Exception as e:
        logging.warning(f"[CACHE] ERRO: Falha ao ler '{key}': {e}")
        return None

def set_dataframe(self, df: pd.DataFrame, prefix: str, assets: List[str], start_date: str, end_date: str, ttl_seconds: int = 86400):
    """Salva DataFrame no cache Redis de forma segura."""
    if df.empty or not self.redis_client:
        return
        
    key = self._generate_key(prefix, assets, start_date, end_date)
    try:
        # Converter para JSON (seguro)
        data = df.to_dict(orient='split')
        serialized = json.dumps(data, default=str)
        self.redis_client.setex(key, ttl_seconds, serialized)
        logging.info(f"[CACHE] WRITE: Salvando '{key}' no Redis.")
    except Exception as e:
        logging.error(f"[CACHE] ERRO: Falha ao salvar '{key}': {e}")
```

---

### 4.5 Rate Limiting - Habilitar em Produção
**Arquivo:** `packages/backend/src/backend_projeto/infrastructure/utils/config.py`

**ANTES:**
```python
RATE_LIMIT_ENABLED: bool = False
```

**DEPOIS:**
```python
import os

# Rate limiting habilitado por padrão em produção
RATE_LIMIT_ENABLED: bool = os.getenv("ENVIRONMENT") == "production" or os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
RATE_LIMIT_REQUESTS: int = 60  # 60 requests
RATE_LIMIT_WINDOW_SECONDS: int = 60  # por minuto
```

---

### 4.6 Redis - Adicionar Autenticação
**Arquivo:** `docker-compose.yml`

**ANTES:**
```yaml
redis:
  image: "redis:7-alpine"
  command: redis-server --appendonly yes
```

**DEPOIS:**
```yaml
redis:
  image: "redis:7-alpine"
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:?REDIS_PASSWORD must be set}
  environment:
    - REDIS_PASSWORD=${REDIS_PASSWORD}
```

**E no backend:**
```yaml
backend:
  environment:
    - REDIS_PASSWORD=${REDIS_PASSWORD}
```

---

### 4.7 JWT - Adicionar Validação de Audience/Issuer
**Arquivo:** `packages/backend/src/backend_projeto/application/auth.py`

**ANTES:**
```python
def verify_token(token: str) -> Optional[str]:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

**DEPOIS:**
```python
JWT_ISSUER = "andrehsatoru.com"
JWT_AUDIENCE = "andrehsatoru.com"

def verify_token(token: str) -> Optional[str]:
    """Verifica JWT com validação completa."""
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            issuer=JWT_ISSUER,
            audience=JWT_AUDIENCE,
            options={"require": ["exp", "sub", "iss", "aud"]}
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria token JWT com claims de segurança."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": datetime.utcnow(),
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

---

### 4.8 Refresh Token - Armazenar Hash ao invés do Token
**Arquivo:** `packages/backend/src/backend_projeto/application/auth.py`

**ANTES:**
```python
redis_key = f"refresh_token:{username}:{encoded_jwt}"
```

**DEPOIS:**
```python
import hashlib

def _hash_token(token: str) -> str:
    """Gera hash SHA-256 do token para armazenamento seguro."""
    return hashlib.sha256(token.encode()).hexdigest()

def create_refresh_token(data: dict) -> str:
    # ... existing code ...
    
    # Armazenar apenas hash do token (mais seguro)
    username = data.get("sub")
    if username:
        token_hash = _hash_token(encoded_jwt)
        redis_key = f"refresh_token:{username}:{token_hash}"
        redis_client.setex(redis_key, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "valid")
    
    return encoded_jwt

def verify_refresh_token(token: str) -> Optional[str]:
    """Verifica refresh token usando hash."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
        
        # Verificar se token está no Redis (usando hash)
        token_hash = _hash_token(token)
        redis_key = f"refresh_token:{username}:{token_hash}"
        if not redis_client.exists(redis_key):
            return None
        
        return username
    except JWTError:
        return None
```

---

### 4.9 Headers de Segurança
**Arquivo:** `packages/backend/src/backend_projeto/main.py`

**Adicionar após CORS middleware:**
```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

# Adicionar após outros middlewares
app.add_middleware(SecurityHeadersMiddleware)
```

---

### 4.10 TypeScript/ESLint - Habilitar Verificações
**Arquivo:** `packages/frontend/next.config.mjs`

**ANTES (INSEGURO):**
```javascript
typescript: {
  ignoreBuildErrors: true,
},
eslint: {
  ignoreDuringBuilds: true,
},
```

**DEPOIS (SEGURO):**
```javascript
typescript: {
  ignoreBuildErrors: false,
},
eslint: {
  ignoreDuringBuilds: false,
},
```

---

## 🔧 Checklist de Implementação (Atualizado)

### Fase 1 (Quick Wins)
- [ ] Remover print debug em data_handling.py
- [ ] Implementar batch de tickers em transaction_endpoints.py
- [ ] Remover interceptors duplicados em axios.ts
- [ ] Remover `unoptimized: true` em next.config.mjs
- [ ] Remover console.logs de produção

### Fase 2 (Core)
- [ ] Implementar análise sob demanda em portfolio_analyzer.py
- [ ] Criar cache único de dados no analyzer
- [ ] Vetorizar loops iterrows()
- [ ] Vetorizar Monte Carlo
- [ ] Implementar lazy loading no frontend
- [ ] Dividir context em stores menores

### Fase 3 (Refinamentos)
- [ ] Implementar cache inteligente
- [ ] Usar scipy.optimize para Markowitz
- [ ] Implementar React Query
- [ ] Auditar e remover dependências não utilizadas
- [ ] Implementar fallback de cache

### Fase 4 (Segurança - CRÍTICO)
- [ ] **4.1** Gerar JWT_SECRET_KEY forte e remover valor padrão
- [ ] **4.2** Remover/desabilitar usuário `testuser` em produção
- [ ] **4.3** Configurar CORS com origens específicas
- [ ] **4.4** Substituir pickle por JSON no cache
- [ ] **4.5** Habilitar rate limiting em produção
- [ ] **4.6** Adicionar senha no Redis
- [ ] **4.7** Validar audience/issuer nos tokens JWT
- [ ] **4.8** Usar hash para armazenar refresh tokens
- [ ] **4.9** Adicionar headers de segurança (CSP, X-Frame-Options)
- [ ] **4.10** Habilitar verificações TypeScript/ESLint

---

## 📊 Resumo de Segurança

| Severidade | Quantidade | Impacto |
|------------|------------|---------|
| 🔴 Crítica | 4 | JWT fraco, CORS aberto, pickle RCE, credenciais hardcoded |
| 🟡 Média | 4 | Rate limiting, Redis sem senha, refresh token inseguro |
| 🟢 Baixa | 2 | Console.logs, verificações desabilitadas |

---

## 📝 Notas Importantes

1. **Testes**: Rodar suite de testes após cada fase
2. **Benchmark**: Medir tempo antes/depois de cada otimização
3. **Rollback**: Manter branches separadas por fase
4. **Monitoramento**: Adicionar métricas de performance em produção
5. **Segurança**: Fase 4 deve ser priorizada ANTES de ir para produção

---

## 🔐 Variáveis de Ambiente Necessárias (.env)

```bash
# OBRIGATÓRIO - Gerar valores seguros!
JWT_SECRET_KEY=<gerar com: openssl rand -base64 32>
REDIS_PASSWORD=<gerar com: openssl rand -base64 24>

# Produção
ENVIRONMENT=production
CORS_ORIGINS=https://andrehsatoru.com,https://www.andrehsatoru.com

# APIs externas
FINNHUB_API_KEY=<sua_chave>
ALPHA_VANTAGE_API_KEY=<sua_chave>
```

---

*Documento gerado em: 07/12/2025*
*Versão: 2.0 - Incluindo correções de segurança*
