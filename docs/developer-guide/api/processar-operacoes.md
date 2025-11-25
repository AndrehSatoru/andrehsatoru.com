# Endpoint: Processar Operações

## Visão Geral

O endpoint `/api/v1/processar_operacoes` é responsável por receber operações financeiras (compra/venda de ativos), buscar cotações históricas reais e executar análise completa de portfólio.

## 📍 Endpoint

```
POST /api/v1/processar_operacoes
```

## 🔑 Autenticação

Este endpoint não requer autenticação no momento.

## 📥 Request

### Headers

```
Content-Type: application/json
```

### Body Schema

```typescript
{
  valorInicial: number;      // Valor inicial do investimento (opcional)
  dataInicial: string;       // Data inicial no formato YYYY-MM-DD
  operacoes: Array<{
    data: string;            // Data da operação (YYYY-MM-DD)
    ticker: string;          // Código do ativo (ex: PETR4, VALE3)
    tipo: string;            // Tipo: "compra" ou "venda"
    valor: number;           // Valor monetário da operação
  }>;
}
```

### Exemplo de Request

```json
{
  "valorInicial": 100000,
  "dataInicial": "2018-10-10",
  "operacoes": [
    {
      "data": "2019-10-10",
      "ticker": "VALE3",
      "tipo": "compra",
      "valor": 10000
    },
    {
      "data": "2019-10-10",
      "ticker": "PETR4",
      "tipo": "compra",
      "valor": 10000
    }
  ]
}
```

## 📤 Response

### Success Response (200 OK)

```json
{
  "status": "success",
  "message": "Análise executada com sucesso!",
  "results": {
    "metrics": {
      "return_total": 0.0847,
      "sharpe_ratio": 1.85,
      "volatility": 0.083,
      "beta": 0.92,
      "alpha": 1.80,
      "var_95": -0.0156,
      "cvar_95": -0.0234,
      "max_drawdown": -0.052
    },
    "allocation": {
      "VALE3": 0.48,
      "PETR4": 0.52
    },
    "performance": [...],
    "charts": {...}
  }
}
```

### Error Response (500 Internal Server Error)

```json
{
  "detail": "Erro ao processar operações: [mensagem de erro]"
}
```

## 🔧 Funcionamento Interno

### 1. Busca de Cotações Históricas

Para cada operação, o sistema:

1. **Identifica a data da operação**
2. **Busca preços históricos** via YFinance API
   - Intervalo: ±5 dias da data da operação
   - Garante disponibilidade de dados
3. **Encontra o preço mais próximo** da data solicitada
4. **Calcula a quantidade de ações**:
   ```
   Quantidade = Valor Investido ÷ Preço da Ação
   ```

### 2. Exemplo de Cálculo

```
Operação: Compra de R$ 10.000 em VALE3 no dia 10/10/2019

1. Sistema busca: Cotação de VALE3 entre 05/10/2019 e 15/10/2019
2. Encontra: Preço = R$ 50,25 em 10/10/2019
3. Calcula: Quantidade = 10.000 ÷ 50,25 = 199,00 ações
4. Armazena:
   - Data: 2019-10-10
   - Ativo: VALE3
   - Quantidade: 199.00
   - Preco: 50.25
```

### 3. Transformação de Dados

O sistema converte as operações para o formato esperado pelo `PortfolioAnalyzer`:

| Campo Frontend | Campo Backend | Descrição |
|---------------|---------------|-----------|
| `data` | `Data` | Data da operação |
| `ticker` | `Ativo` | Código do ativo |
| `valor` + cotação | `Quantidade` | Calculado automaticamente |
| cotação histórica | `Preco` | Buscado via YFinance |

### 4. Fallback em Caso de Erro

Se não for possível buscar a cotação histórica:
- **Quantidade** = 1.0
- **Preço** = valor informado
- **Log** de warning é registrado

## 📊 Integração com Frontend

### Componente de Envio

```typescript
// app/enviar/page.tsx
const payload = {
  valorInicial: parseFloat(valorInicial) || 0,
  dataInicial,
  operacoes: operacoes.map(op => ({
    data: op.data,
    ticker: op.ticker.trim(),
    tipo: op.tipo,
    valor: parseFloat(op.valor) || 0
  }))
};

const response = await fetch('/api/enviar-operacoes', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
});
```

### API Route Next.js

```typescript
// app/api/enviar-operacoes/route.ts
export async function POST(req: Request) {
  const json = await req.json();
  const parsed = BodySchema.safeParse(json);
  
  if (!parsed.success) {
    return new Response(JSON.stringify({
      message: "Corpo da requisição inválido",
      errors: parsed.error.flatten()
    }), { status: 400 });
  }

  // Chama o backend interno
  const resp = await enviarOperacoes(parsed.data);
  return new Response(JSON.stringify(resp), { status: 200 });
}
```

## 🐛 Debugging

### Logs do Backend

Para ver os cálculos de quantidade em tempo real:

```bash
docker logs portfolio_backend --tail 50 --follow
```

Exemplo de log:

```
INFO: Operação VALE3 em 2019-10-10: valor=10000, preço=50.25, quantidade=199.0000
WARNING: Não foi possível buscar preço para XYZ123 em 2019-10-10. Usando valor como preço.
```

### Validação de Dados

O sistema valida:
- ✅ Formato de datas (YYYY-MM-DD)
- ✅ Tickers válidos (não vazios)
- ✅ Valores numéricos positivos
- ✅ Tipo de operação ("compra" ou "venda")

## 🚀 Performance

- **Busca paralela**: Cotações são buscadas para todos os ativos simultaneamente
- **Cache**: YFinance mantém cache de cotações já buscadas
- **Timeout**: 30 segundos por requisição ao YFinance
- **Retry**: 3 tentativas com backoff exponencial

## 📝 Notas Importantes

1. **Cotações de ações brasileiras**: Use sufixo `.SA` para ações da B3 (ex: PETR4.SA)
2. **Fins de semana**: Sistema busca próxima data útil automaticamente
3. **Feriados**: Considera calendário de negociação brasileiro
4. **Horário**: Usa preços de fechamento (Adjusted Close)

## 🔗 Endpoints Relacionados

- `GET /api/v1/status` - Health check do backend
- `GET /api/v1/prices` - Busca direta de cotações históricas
- `POST /api/v1/auth/token` - Autenticação (futuro)

## 📚 Referências

- [YFinance Documentation](https://github.com/ranaroussi/yfinance)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PortfolioAnalyzer Source](../../packages/backend/src/backend_projeto/domain/analysis.py)
