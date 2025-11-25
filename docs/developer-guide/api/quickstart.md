# Guia de Início Rápido da API

## Iniciar o Servidor

```bash
cd investment-backend/src/backend_projeto
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Acesse a documentação interativa:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Exemplos de Uso

### 1. Status da API

```bash
curl http://localhost:8000/api/v1/system/status
```

**Resposta**:
```json
{"status": "ok"}
```

---

### 2. Obter Preços Históricos

**Endpoint**: `POST /api/v1/prices`

```bash
curl -X POST http://localhost:8000/api/v1/prices \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA", "VALE3.SA"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

**Resposta**:
```json
{
  "columns": ["PETR4.SA", "VALE3.SA"],
  "index": ["2024-01-02", "2024-01-03", ...],
  "data": [[35.50, 68.20], [35.80, 68.50], ...]
}
```

---

### 3. Médias Móveis (SMA/EMA)

**Endpoint**: `POST /api/v1/ta/moving-averages`

```bash
curl -X POST http://localhost:8000/api/v1/ta/moving-averages \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "method": "sma",
    "windows": [5, 21],
    "include_original": false,
    "only_columns": ["PETR4.SA_SMA_21"]
  }'
```

**Resposta** (apenas SMA 21):
```json
{
  "columns": ["PETR4.SA_SMA_21"],
  "index": ["2024-01-02", ...],
  "data": [[35.45], [35.52], ...]
}
```

---

### 4. MACD

**Endpoint**: `POST /api/v1/ta/macd`

```bash
curl -X POST http://localhost:8000/api/v1/ta/macd \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["VALE3.SA"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "fast": 12,
    "slow": 26,
    "signal": 9,
    "include_original": true
  }'
```

**Resposta**:
```json
{
  "columns": ["VALE3.SA", "VALE3.SA_MACD", "VALE3.SA_MACD_SIGNAL", "VALE3.SA_MACD_HIST"],
  "index": [...],
  "data": [[68.20, 0.15, 0.12, 0.03], ...]
}
```

---

### 5. Value at Risk (VaR)

**Endpoint**: `POST /api/v1/risk/var`

```bash
curl -X POST http://localhost:8000/api/v1/risk/var \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA", "VALE3.SA"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "weights": [0.6, 0.4],
    "alpha": 0.99,
    "method": "historical"
  }'
```

**Resposta**:
```json
{
  "result": {
    "var": 0.0523,
    "alpha": 0.99,
    "method": "historical",
    "details": {"quantile": -0.0523}
  }
}
```

**Métodos disponíveis**: `historical`, `std`, `ewma`, `garch`, `evt`

---

### 6. Expected Shortfall (ES/CVaR)

**Endpoint**: `POST /api/v1/risk/es`

```bash
curl -X POST http://localhost:8000/api/v1/risk/es \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA", "VALE3.SA"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "weights": [0.5, 0.5],
    "alpha": 0.95,
    "method": "std",
    "ewma_lambda": 0.94
  }'
```

---

### 7. Incremental VaR (IVaR)

**Endpoint**: `POST /api/v1/risk/ivar`

```bash
curl -X POST http://localhost:8000/api/v1/risk/ivar \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "weights": [0.4, 0.3, 0.3],
    "alpha": 0.99,
    "method": "historical",
    "delta": 0.01
  }'
```

**Resposta**:
```json
{
  "result": {
    "alpha": 0.99,
    "method": "historical",
    "delta": 0.01,
    "base_var": 0.0485,
    "base_weights": [0.4, 0.3, 0.3],
    "ivar": {
      "PETR4.SA": 0.0012,
      "VALE3.SA": 0.0008,
      "ITUB4.SA": 0.0005
    },
    "assets": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
  }
}
```

**Interpretação**: Aumentar 1% o peso de PETR4.SA aumenta o VaR em 0.12%.

---

### 8. Marginal VaR (MVaR)

**Endpoint**: `POST /api/v1/risk/mvar`

```bash
curl -X POST http://localhost:8000/api/v1/risk/mvar \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA", "VALE3.SA"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "weights": [0.6, 0.4],
    "alpha": 0.99,
    "method": "std"
  }'
```

**Resposta**:
```json
{
  "result": {
    "alpha": 0.99,
    "method": "std",
    "base_var": 0.0485,
    "base_weights": [0.6, 0.4],
    "mvar": {
      "PETR4.SA": -0.0025,
      "VALE3.SA": 0.0018
    },
    "assets": ["PETR4.SA", "VALE3.SA"]
  }
}
```

**Interpretação**: Remover PETR4.SA reduz o VaR em 0.25%. Remover VALE3.SA aumenta o VaR em 0.18%.

---

### 9. VaR Relativo (vs Benchmark)

**Endpoint**: `POST /api/v1/risk/relvar`

```bash
curl -X POST http://localhost:8000/api/v1/risk/relvar \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA", "VALE3.SA"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "weights": [0.5, 0.5],
    "alpha": 0.95,
    "method": "ewma",
    "ewma_lambda": 0.94,
    "benchmark": "^BVSP"
  }'
```

**Resposta**:
```json
{
  "result": {
    "relative_var": 0.0185,
    "alpha": 0.95,
    "method": "ewma",
    "details": {
      "mu": 0.0002,
      "sigma": 0.0145,
      "z": -1.645,
      "method": "ewma",
      "ewma_lambda": 0.94
    }
  }
}
```

**Interpretação**: Com 95% de confiança, a carteira performa abaixo do IBOVESPA por no máximo 1.85%.

---

### 10. Backtest do VaR

**Endpoint**: `POST /api/v1/risk/backtest`

```bash
curl -X POST http://localhost:8000/api/v1/risk/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA", "VALE3.SA"],
    "start_date": "2022-01-01",
    "end_date": "2024-12-31",
    "weights": [0.5, 0.5],
    "alpha": 0.99,
    "method": "historical"
  }'
```

**Resposta**:
```json
{
  "result": {
    "n": 500,
    "exceptions": 6,
    "exception_rate": 0.012,
    "kupiec_lr": 0.85,
    "kupiec_pvalue": 0.36,
    "christoffersen_pvalue": 0.42,
    "basel_zone": "green",
    "alpha": 0.99,
    "method": "historical"
  }
}
```

**Interpretação**:
- 6 exceções em 500 dias (1.2% vs 1% esperado)
- Kupiec p-value > 0.05: modelo não rejeitado
- Zona de Basileia "verde": modelo adequado

---

### 11. Otimização Markowitz

**Endpoint**: `POST /api/v1/opt/markowitz`

```bash
curl -X POST http://localhost:8000/api/v1/opt/markowitz \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "objective": "max_sharpe",
    "long_only": true,
    "max_weight": 0.5
  }'
```

**Resposta**:
```json
{
  "result": {
    "weights": [0.35, 0.5, 0.15],
    "expected_return": 0.18,
    "volatility": 0.25,
    "sharpe_ratio": 0.72
  }
}
```

---

### 12. Métricas CAPM

**Endpoint**: `POST /api/v1/factors/capm`

```bash
curl -X POST http://localhost:8000/api/v1/factors/capm \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "benchmark": "^BVSP"
  }'
```

**Resposta**:
```json
{
  "result": {
    "PETR4.SA": {
      "beta": 1.25,
      "alpha": 0.002,
      "r_squared": 0.65,
      "sharpe": 0.85
    }
  }
}
```

---

### 13. Fronteira Eficiente (Gráfico)

**Endpoint**: `POST /api/v1/visualization/efficient-frontier`

```bash
curl -X POST http://localhost:8000/api/v1/visualization/efficient-frontier \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "n_samples": 5000,
    "long_only": true,
    "max_weight": 0.6,
    "rf": 0.0
  }' --output frontier.png
```

Salva a imagem PNG da fronteira eficiente.

---

### 14. Fama-French 3 Fatores (Mensal)

**Endpoint**: `POST /api/v1/factors/ff3`

```bash
curl -X POST http://localhost:8000/api/v1/factors/ff3 \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA", "VALE3.SA"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "frequency": "M",
    "market": "US",
    "rf_source": "ff",
    "convert_to_usd": true
  }'
```

**Resposta** (resumo):
```json
{
  "result": {
    "frequency": "M",
    "model": "FF3",
    "results": {
      "PETR4.SA": {
        "alpha": 0.001,
        "beta_mkt": 1.10,
        "beta_smb": 0.15,
        "beta_hml": -0.05,
        "r2": 0.62,
        "n_obs": 24
      }
    }
  }
}
```

**Observações**:
- `rf_source`: 
  - `"ff"`: Taxa livre de risco do dataset Fama-French (padrão, recomendado para consistência)
  - `"selic"`: **Taxa CDI do Banco Central do Brasil** - compõe taxa mensal via dados diários do BCB (série 12)
  - `"us10y"`: Treasury de 10 anos do FRED (convertendo para taxa mensal)
- `convert_to_usd`: quando `true`, os preços dos ativos em BRL são convertidos para USD via USDBRL antes da regressão, mantendo a consistência com os fatores em USD.
- Fatores são dos EUA (Biblioteca Kenneth French) com frequência mensal: `MKT_RF`, `SMB`, `HML`.
- **💡 Dica**: Use `rf_source="selic"` para ativos brasileiros - reflete melhor a taxa livre de risco local.

---

### 15. Fama-French 5 Fatores (Mensal)

**Endpoint**: `POST /api/v1/factors/ff5`

```bash
curl -X POST http://localhost:8000/api/v1/factors/ff5 \
  -H "Content-Type: application/json" \
  -d '{
    "assets": ["PETR4.SA"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "rf_source": "ff",
    "convert_to_usd": true
  }'
```

**Resposta** (resumo):
```json
{
  "result": {
    "frequency": "M",
    "model": "FF5",
    "results": {
      "PETR4.SA": {
        "alpha": 0.0005,
        "beta_mkt": 1.08,
        "beta_smb": 0.12,
        "beta_hml": 0.07,
        "beta_rmw": 0.05,
        "beta_cma": -0.03,
        "r2": 0.68,
        "n_obs": 24
      }
    }
  }
}
```

**Notas**:
- Fatores 5: `MKT_RF`, `SMB`, `HML`, `RMW` (rentabilidade), `CMA` (investimento).
- `rf_source`: 
  - `"ff"`: Taxa do dataset Fama-French (padrão)
  - `"selic"`: **CDI do BCB** - mais apropriado para ativos brasileiros
  - `"us10y"`: Treasury 10 anos dos EUA
- `convert_to_usd` é recomendado para ativos em BRL.
- **💡 Para portfólios brasileiros**: use `rf_source="selic"` para taxa livre de risco baseada no CDI.

---

### 16. Gráficos Fama-French

#### 16.1 Fatores (séries)

**Endpoint**: `POST /api/v1/visualization/ff-factors`

```bash
curl -X POST http://localhost:8000/api/v1/visualization/ff-factors \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ff5",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30"
  }' --output factors.png
```

#### 16.2 Betas do Ativo

**Endpoint**: `POST /api/v1/visualization/ff-betas`

```bash
curl -X POST http://localhost:8000/api/v1/visualization/ff-betas \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ff3",
    "asset": "PETR4.SA",
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "rf_source": "ff",
    "convert_to_usd": true
  }' --output betas.png
```

**Notas**:
- `/plots/ff-betas` suporta `rf_source = ff | selic | us10y` e `convert_to_usd`.


## Headers Úteis

### ID da Requisição (para rastreamento)
```bash
curl -H "X-Request-ID: abc123" http://localhost:8000/api/v1/risk/var ...
```

### Headers da Resposta
- `X-Process-Time`: tempo de processamento em segundos
- `X-Request-ID`: ID da requisição (eco)

---

## Códigos de Status

- **200**: Sucesso
- **422**: Erro de validação (ativos vazios, pesos inválidos, etc.)
- **400**: Erro de requisição (arquivo inválido, etc.)
- **503**: Serviço externo indisponível (YFinance, BCB)
- **500**: Erro interno do servidor

---

## Dicas de Performance

1.  **Use filtros** em `/ta/moving-averages` e `/ta/macd`:
    ```json
    {
      "include_original": false,
      "only_columns": ["PETR4.SA_SMA_21"]
    }
    ```

2.  **Limite o período** para séries longas (máximo de 5 anos recomendado)

3.  **Cache**: dados históricos são cacheados automaticamente

4.  **Gzip**: respostas > 1KB são comprimidas automaticamente

---

## Solução de Problemas

### Erro 422: "assets não pode ser vazio"
- Verifique se o campo `assets` está presente e não está vazio

### Erro 422: "soma de weights deve ser > 0"
- Os pesos devem somar um valor positivo
- Se omitir `weights`, será equiponderado automaticamente

### Erro 503: "Falha ao baixar cotações"
- O YFinance pode estar temporariamente indisponível
- Verifique a conectividade com a internet
- Tente novamente após alguns segundos

### Erro 500: "Benchmark não disponível"
- Verifique se o ticker do benchmark está correto
- Ex: `^BVSP` (IBOVESPA), `^GSPC` (S&P 500)

---

## Próximos Passos

- Explore a documentação interativa em `/docs`
- Veja exemplos completos em `tests/api/`
