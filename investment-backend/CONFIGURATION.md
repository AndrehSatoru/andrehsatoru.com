# Guia de Configuração - Investment Backend API

## Visão Geral

A API suporta configuração via:
1. **Variáveis de ambiente** (`.env` file ou system env vars)
2. **Valores padrão** (definidos em `utils/config.py`)

## Configuração Rápida

1. **Copie o arquivo de exemplo**:
   ```bash
   cp .env.example .env
   ```

2. **Edite `.env`** conforme necessário

3. **Reinicie o servidor** para aplicar mudanças

## Variáveis de Ambiente

### API Configuration

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `MAX_ASSETS_PER_REQUEST` | int | 100 | Máximo de ativos por requisição |
| `REQUEST_TIMEOUT_SECONDS` | int | 300 | Timeout para requisições (5 min) |

**Exemplo**:
```bash
MAX_ASSETS_PER_REQUEST=50
REQUEST_TIMEOUT_SECONDS=600
```

---

### Cache

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `ENABLE_CACHE` | bool | true | Habilita cache de dados históricos |
| `CACHE_TTL_SECONDS` | int | 3600 | TTL do cache (1 hora) |

**Quando usar**:
- **Produção**: `ENABLE_CACHE=true` (recomendado)
- **Desenvolvimento**: `ENABLE_CACHE=false` (para sempre buscar dados frescos)

**Exemplo**:
```bash
ENABLE_CACHE=true
CACHE_TTL_SECONDS=7200  # 2 horas
```

---

### Logging

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `LOG_LEVEL` | str | INFO | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `LOG_FORMAT` | str | text | 'text' ou 'json' (para parsing estruturado) |

**Exemplo**:
```bash
LOG_LEVEL=DEBUG
LOG_FORMAT=json
```

**Uso em produção**:
```bash
LOG_LEVEL=WARNING
LOG_FORMAT=json  # Para integração com ELK, Datadog, etc.
```

---

### Rate Limiting

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `RATE_LIMIT_ENABLED` | bool | false | Habilita rate limiting |
| `RATE_LIMIT_REQUESTS` | int | 100 | Requisições permitidas por janela |
| `RATE_LIMIT_WINDOW_SECONDS` | int | 60 | Janela de tempo (1 min) |

**Exemplo**:
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW_SECONDS=60
```

**Nota**: Requer implementação de middleware adicional (não incluído por padrão).

---

### External APIs (YFinance)

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `YFINANCE_TIMEOUT` | int | 30 | Timeout para chamadas YFinance (segundos) |
| `YFINANCE_MAX_RETRIES` | int | 3 | Máximo de tentativas em caso de falha |
| `YFINANCE_BACKOFF_FACTOR` | float | 2.0 | Fator de backoff exponencial |

**Exemplo**:
```bash
YFINANCE_TIMEOUT=60
YFINANCE_MAX_RETRIES=5
YFINANCE_BACKOFF_FACTOR=1.5
```

**Backoff**: Com fator 2.0, as tentativas ocorrem em: 0s, 2s, 4s, 8s...

---

## Configurações Internas (Não Sobrescritíveis por Env Vars)

Estas são definidas em `utils/config.py` e não podem ser alteradas via `.env`:

| Configuração | Valor | Descrição |
|--------------|-------|-----------|
| `DIAS_UTEIS_ANO` | 252 | Dias úteis por ano (para anualização) |
| `VAR_CONFIDENCE_LEVEL` | 0.99 | Nível de confiança padrão para VaR |
| `CONSECUTIVE_NAN_THRESHOLD` | 3 | Máximo de NaNs consecutivos tolerados |
| `MONTE_CARLO_SIMULATIONS` | 100000 | Simulações Monte Carlo padrão |
| `BENCHMARK_TICKER` | ^BVSP | Benchmark padrão (IBOVESPA) |

Para alterar estas, edite `utils/config.py` diretamente.

---

## Endpoint de Configurações

Você pode consultar as configurações públicas via API:

```bash
curl http://localhost:8000/config
```

**Resposta**:
```json
{
  "DIAS_UTEIS_ANO": 252,
  "VAR_CONFIDENCE_LEVEL": 0.99,
  "CONSECUTIVE_NAN_THRESHOLD": 3,
  "MAX_ASSETS_PER_REQUEST": 100,
  "CACHE_ENABLED": true,
  "CACHE_TTL_SECONDS": 3600
}
```

---

## Cenários de Configuração

### Desenvolvimento Local

```bash
# .env
ENABLE_CACHE=false
LOG_LEVEL=DEBUG
LOG_FORMAT=text
YFINANCE_TIMEOUT=60
```

### Staging

```bash
# .env
ENABLE_CACHE=true
CACHE_TTL_SECONDS=1800  # 30 min
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=200
```

### Produção

```bash
# .env
ENABLE_CACHE=true
CACHE_TTL_SECONDS=3600  # 1 hora
LOG_LEVEL=WARNING
LOG_FORMAT=json
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
YFINANCE_MAX_RETRIES=5
MAX_ASSETS_PER_REQUEST=50  # Limitar para evitar sobrecarga
```

---

## Validações

A classe `Config` valida automaticamente:

- `MAX_ASSETS_PER_REQUEST >= 1`
- `0 < VAR_CONFIDENCE_LEVEL < 1`
- `DIAS_UTEIS_ANO > 0`

Se uma validação falhar, o servidor não iniciará e exibirá erro detalhado.

---

## Integrações Opcionais

### Redis (Cache Distribuído)

```bash
# .env
REDIS_URL=redis://localhost:6379/0
```

**Nota**: Requer implementação de `RedisCacheManager` (não incluído por padrão).

### PostgreSQL (Persistência)

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/investment_db
```

### Sentry (Error Tracking)

```bash
# .env
SENTRY_DSN=https://your-key@sentry.io/project-id
```

**Integração**:
```python
# main.py
import sentry_sdk
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))
```

### CORS (Frontend)

```bash
# .env
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

**Integração**:
```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Troubleshooting

### Configuração não está sendo aplicada

1. **Verifique se o arquivo `.env` está no diretório correto**:
   ```bash
   ls -la .env
   ```

2. **Reinicie o servidor** após alterar `.env`

3. **Verifique logs de inicialização** para erros de validação

### Cache não está funcionando

1. **Verifique se `ENABLE_CACHE=true`**:
   ```bash
   curl http://localhost:8000/config | grep CACHE_ENABLED
   ```

2. **Limpe o cache manualmente** (se necessário):
   ```bash
   rm -rf src/backend_projeto/cache/*
   ```

### Timeout em requisições

1. **Aumente `REQUEST_TIMEOUT_SECONDS`**:
   ```bash
   REQUEST_TIMEOUT_SECONDS=600  # 10 minutos
   ```

2. **Aumente `YFINANCE_TIMEOUT`** se o problema for com dados externos

---

## Boas Práticas

1. **Nunca commite `.env`** no Git (já está no `.gitignore`)
2. **Use `.env.example`** como template para novos ambientes
3. **Documente** mudanças em configurações críticas
4. **Teste** configurações em staging antes de produção
5. **Monitore** logs após mudanças de configuração

---

## Referências

- FastAPI Settings: https://fastapi.tiangolo.com/advanced/settings/
- 12-Factor App: https://12factor.net/config
- Environment Variables Best Practices: https://blog.doppler.com/environment-variables-best-practices
