# Guia de Configuração - API de Análise de Investimentos

## Visão Geral

A API suporta configuração via:
1.  **Variáveis de ambiente** (arquivo `.env` ou variáveis de sistema)
2.  **Valores padrão** (definidos em `src/backend_projeto/utils/config.py`)

## Configuração Rápida

1.  **Copie o arquivo de exemplo**:
    ```bash
    cp .env.example .env
    ```

2.  **Edite o `.env`** com suas chaves de API e outras configurações desejadas.

3.  **Reinicie o servidor** para aplicar as mudanças.

## Variáveis de Ambiente

### Simulação

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `CAPITAL_INICIAL` | float | 100,000,000.0 | Capital inicial para simulações. |
| `DATA_FINAL_SIMULACAO` | str | "2025-10-01" | Data final para simulações. |
| `SLIPPAGE_PERCENTUAL` | float | 0.0005 | Percentual de slippage para simulações. |
| `ARQUIVO_TRANSACOES` | str | 'Carteira.xlsx' | Nome do arquivo de transações. |
| `INPUT_DIR` | str | 'inputs' | Diretório de entrada para arquivos. |
| `OUTPUT_DIR` | str | 'outputs' | Diretório de saída para arquivos. |

### Benchmark

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `BENCHMARK_TICKER` | str | '^BVSP' | Ticker do benchmark (Ibovespa). |

### Risco

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `VAR_CONFIDENCE_LEVEL` | float | 0.99 | Nível de confiança para o VaR. |
| `CONSECUTIVE_NAN_THRESHOLD` | int | 3 | Máximo de NaNs consecutivos tolerados. |

### Monte Carlo

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `MONTE_CARLO_SIMULATIONS` | int | 100000 | Número de simulações Monte Carlo. |
| `MONTE_CARLO_DAYS` | int | 252 | Dias para a simulação Monte Carlo. |
| `MONTE_CARLO_GBM_ANNUAL_DRIFT`| float | 0.0 | Drift anual para o GBM. |

### Modelos

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `USE_GARCH_VOL` | bool | True | Usar volatilidade GARCH. |
| `USE_BLACK_LITTERMAN` | bool | True | Usar o modelo Black-Litterman. |

### Calendário

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `DIAS_UTEIS_ANO` | int | 252 | Dias úteis no ano. |
| `DIAS_CALENDARIO_ANO` | float | 365.25 | Dias corridos no ano. |

### API

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `MAX_ASSETS_PER_REQUEST` | int | 100 | Máximo de ativos por requisição. |
| `REQUEST_TIMEOUT_SECONDS` | int | 300 | Timeout para requisições (5 min). |
| `GZIP_MINIMUM_SIZE` | int | 1000 | Tamanho mínimo para compressão gzip. |

### Cache

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `ENABLE_CACHE` | bool | False | Habilita o cache de dados. |
| `CACHE_TTL_SECONDS` | int | 3600 | Tempo de vida do cache (1 hora). |
| `CACHE_DIR` | str | 'cache' | Diretório para o cache. |

### Logging

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `LOG_LEVEL` | str | 'INFO' | Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL). |
| `LOG_FORMAT` | str | 'text' | Formato do log ('text' ou 'json'). |

### Rate Limiting

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `RATE_LIMIT_ENABLED` | bool | False | Habilita o rate limiting. |
| `RATE_LIMIT_REQUESTS` | int | 100 | Requisições por janela. |
| `RATE_LIMIT_WINDOW_SECONDS` | int | 60 | Janela de tempo em segundos. |
| `USE_REDIS_RATE_LIMITER` | bool | False | Usar Redis para rate limiting. |

### APIs Externas

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `YFINANCE_TIMEOUT` | int | 30 | Timeout para chamadas ao yfinance. |
| `YFINANCE_MAX_RETRIES` | int | 3 | Máximo de tentativas em caso de falha. |
| `YFINANCE_BACKOFF_FACTOR` | float | 2.0 | Fator de backoff exponencial. |
| `DATA_PROVIDER_MAX_RETRIES` | int | 3 | Máximo de tentativas para o provedor de dados. |
| `DATA_PROVIDER_BACKOFF_FACTOR`| float | 2.0 | Fator de backoff para o provedor de dados. |
| `DATA_PROVIDER_TIMEOUT` | int | 30 | Timeout para o provedor de dados. |

### CORS

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `CORS_ORIGINS` | List[str] | ['*'] | Lista de origens permitidas. |

### Taxa Livre de Risco

| Variável | Tipo | Padrão | Descrição |
|---|---|---|---|
| `RISK_FREE_RATE` | float | 0.0 | Taxa livre de risco. |

### Chaves de API

| Variável | Tipo | Descrição |
|---|---|---|
| `FINNHUB_API_KEY` | str | Sua chave de API do Finnhub. |
| `ALPHA_VANTAGE_API_KEY` | str | Sua chave de API do Alpha Vantage. |

## Endpoint de Configurações

Você pode consultar as configurações públicas via API:

```bash
curl http://localhost:8000/api/v1/system/config
```

## Validações

A classe `Settings` em `config.py` valida automaticamente as variáveis de ambiente. Se uma validação falhar, o servidor não iniciará e exibirá um erro detalhado.
