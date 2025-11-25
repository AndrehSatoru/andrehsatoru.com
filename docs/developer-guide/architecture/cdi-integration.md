# Integração com CDI - Rendimento do Caixa

## Visão Geral

A partir da versão 1.3.0, o sistema implementa o rendimento automático do CDI (Certificado de Depósito Interbancário) sobre o caixa não investido do portfólio. Na versão 1.4.0, foi corrigido o cálculo do CDI e adicionado o recebimento automático de dividendos.

## Motivação

Anteriormente, o caixa não investido era tratado como valor estático que apenas diminuía com novas compras. Isso não refletia a realidade do mercado brasileiro, onde:

- Recursos não investidos ficam tipicamente em produtos de renda fixa
- O CDI é o principal benchmark para investimentos de baixo risco
- Investidores conservadores mantêm parte do capital em liquidez diária que rende próximo ao CDI
- Dividendos e proventos são creditados automaticamente na conta

## Arquitetura da Implementação

### 1. Fonte de Dados: Banco Central do Brasil (BCB)

A integração utiliza a biblioteca `python-bcb` para acessar o Sistema Gerenciador de Séries Temporais (SGS) do Banco Central.

**Série utilizada:** 12 - Taxa de juros - CDI (taxa diária em %)

```python
from bcb import sgs

# Buscar CDI diário
cdi_data = sgs.get({'CDI': 12}, start=start_date, end=end_date)
```

### 2. Conversão de Taxas

> ⚠️ **IMPORTANTE (v1.4.0)**: A série 12 do BCB retorna a **taxa DIÁRIA já em percentual**, NÃO a taxa anual!

**Exemplo de dados do BCB:**
```
2024-01-02: 0.04290  (= 0.0429% ao dia)
2024-01-03: 0.04290
2024-01-04: 0.04290
```

**Conversão correta:**
```python
# Taxa diária em decimal = valor / 100
taxa_diaria_decimal = 0.04290 / 100  # = 0.000429
```

**❌ ERRO ANTIGO (v1.3.0):**
```python
# Tratava como taxa anual e convertia - INCORRETO!
taxa_diaria = ((1 + taxa_anual/100) ** (1/252)) - 1
```

### 3. Implementação no YFinanceProvider

#### Método `fetch_cdi_daily()` (v1.4.0)

```python
def fetch_cdi_daily(self, start_date: str, end_date: str) -> pd.Series:
    """
    Busca taxas diárias do CDI do BCB.
    
    IMPORTANTE: A série 12 retorna taxa DIÁRIA em %, não anual!
    CDI só rende em dias úteis - NÃO fazer forward fill para fins de semana.
    
    Returns:
        pd.Series com taxas diárias em decimal, apenas dias úteis com dados reais
    """
    cdi_data = sgs.get({'CDI': 12}, start=start_date, end=end_date)
    
    # Converter de percentual para decimal (0.017% -> 0.00017)
    cdi_diario = cdi_data['CDI'] / 100.0
    
    return cdi_diario  # Sem forward fill!
```

**Diferenças importantes da v1.4.0:**
- ✅ Não faz mais forward fill para fins de semana (CDI não rende nesses dias)
- ✅ Retorna apenas dias úteis com dados reais
- ✅ Valores de CDI anual agora estão corretos (ex: 2020 = 2.75%, não 4.03%)

#### Método `compute_monthly_rf_from_cdi()`

```python
def compute_monthly_rf_from_cdi(self, start_date: str, end_date: str) -> pd.Series:
    """
    Calcula taxa livre de risco mensal a partir do CDI diário.
    
    Returns:
        pd.Series com taxas mensais compostas, índice month-end
    """
    cdi_daily = self.fetch_cdi_daily(start_date, end_date)
    cdi_df = pd.DataFrame({'CDI': cdi_daily})
    monthly_rf = cdi_df.resample('M').apply(lambda x: (1 + x).prod() - 1)['CDI']
    
    return monthly_rf
```

### 4. Busca de Dividendos (v1.4.0)

#### Método `fetch_dividends()`

A partir da v1.4.0, os dividendos são buscados diretamente da API do Yahoo Finance (não mais via biblioteca yfinance que apresentava erros):

```python
def fetch_dividends(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """
    Busca histórico de dividendos via API direta do Yahoo Finance.
    """
    # Converter datas para timestamps
    start_ts = int(pd.Timestamp(start_date).timestamp())
    end_ts = int(pd.Timestamp(end_date).timestamp())
    
    # Chamar API direta
    url = f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}'
    params = {
        'period1': start_ts,
        'period2': end_ts,
        'interval': '1d',
        'events': 'div'  # Solicita apenas dividendos
    }
    
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()
    
    # Extrair dividendos
    dividends = data['chart']['result'][0]['events']['dividends']
```

### 5. Aplicação no PortfolioAnalyzer (v1.4.0)

### 4. Aplicação no PortfolioAnalyzer

O método `_calculate_portfolio_value()` foi completamente refatorado para aplicar o rendimento do CDI:

```python
def _calculate_portfolio_value(self) -> pd.Series:
    # 1. Calcular valor dos ativos (como antes)
    portfolio_value = ... # soma das posições × preços
    
    # 2. Buscar taxas CDI para o período
    cdi_rates = self.data_loader.fetch_cdi_daily(start_date, end_date)
    
    # 3. Calcular caixa com rendimento do CDI
    current_cash = self.initial_value
    
    for date in self.positions.index:
        # 3a. Aplicar rendimento do CDI ao caixa do dia anterior
        if date in cdi_rates.index and cdi_rates[date] > 0:
            current_cash *= (1 + cdi_rates[date])
        
        # 3b. Subtrair transações do dia
        if date in transactions_by_date:
            current_cash -= transactions_by_date[date]
        
        # 3c. Garantir caixa não negativo
        current_cash = max(0, current_cash)
        
        cash_series[date] = current_cash
    
    # 4. Valor total = ativos + caixa
    portfolio_value += cash_series
    
    return portfolio_value
```

## Fluxo de Cálculo

### Exemplo Detalhado

**Configuração:**
- Capital inicial: R$ 100.000
- Data inicial: 2024-01-02
- Transação: 2024-01-15 - Compra de R$ 10.000 em PETR4

**Dia 1 (2024-01-02):**
```
Caixa inicial: R$ 100.000,00
CDI: 0.000483 (0.0483%)
Rendimento: R$ 100.000 × 0.000483 = R$ 48,30
Caixa final: R$ 100.048,30
```

**Dia 2 (2024-01-03):**
```
Caixa inicial: R$ 100.048,30
CDI: 0.000483
Rendimento: R$ 100.048,30 × 0.000483 = R$ 48,33
Caixa final: R$ 100.096,63
```

**... (dias 3 a 14): rendimento contínuo**

**Dia 15 (2024-01-15):**
```
Caixa inicial: R$ 100.XXX,XX (após 13 dias de rendimento)
CDI: 0.000483
Rendimento: R$ 100.XXX,XX × 0.000483 = R$ 48,XX
Transação: -R$ 10.000,00 (compra de PETR4)
Caixa final: R$ 90.XXX,XX
```

**Dias seguintes:**
```
Caixa continua rendendo CDI sobre o saldo de ~R$ 90.000
```

## Impacto nos Resultados

### Correção do CDI (v1.4.0)

**O problema anterior:** O código tratava a série 12 do BCB como taxa anual e aplicava forward fill para fins de semana, resultando em valores inflacionados.

**Comparação de valores de CDI anual:**

| Ano  | Antes (incorreto) | Depois (v1.4.0) | Referência BCB |
|------|-------------------|-----------------|----------------|
| 2020 | 4.03%             | 2.75%           | 2.77% ✅       |
| 2021 | 6.45%             | 4.44%           | 4.40% ✅       |
| 2022 | 18.49%            | 12.38%          | 12.37% ✅      |
| 2023 | 19.67%            | 13.03%          | 13.05% ✅      |
| 2024 | 16.10%            | 10.89%          | 10.87% ✅      |
| 2025 | 18.98%            | 12.71%          | 12.69% ✅      |

### Comparação com Dividendos

**Cenário:** R$ 100.000 inicial, R$ 60.000 investidos (PETR4 + VALE3), período 2020-2025

| Componente | Antes | Depois (v1.4.0) |
|------------|-------|-----------------|
| Caixa inicial | R$ 40.000 | R$ 40.000 |
| CDI acumulado (5 anos) | - | ~R$ 60.000 |
| Dividendos recebidos | R$ 0 | ~R$ 74.000 |
| **Caixa final** | R$ 40.000 | **~R$ 174.000** |

### Realismo Financeiro

**Antes (v1.3.0 e anterior):**
- Caixa mostrava valor fixo (inicial - investido)
- Não refletia rendimento do CDI corretamente
- Não contabilizava dividendos

**Depois (v1.4.0):**
- Caixa rende CDI com taxas corretas
- Dividendos são creditados automaticamente
- Valor do caixa na tabela de alocação reflete a realidade

## Uso nos Endpoints da API

### Fama-French 3 e 5 Fatores

Os endpoints `/api/v1/factors/ff3` e `/api/v1/factors/ff5` agora suportam corretamente a opção `rf_source='selic'`:

```json
{
  "assets": ["PETR4.SA", "VALE3.SA"],
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "rf_source": "selic"  // Usa CDI como taxa livre de risco
}
```

**Opções de rf_source:**
- `"ff"`: Taxa do dataset Fama-French (padrão, mercado US)
- `"selic"`: CDI do BCB (mais apropriado para ativos brasileiros)
- `"us10y"`: Treasury 10 anos dos EUA

## Considerações de Performance

### Cache
- O `fetch_cdi_daily()` não utiliza cache por padrão
- Considere implementar cache se houver múltiplas chamadas para o mesmo período
- BCB SGS tem boa performance (< 1s para 1 ano de dados)

### Volume de Dados
- CDI diário: ~252 registros/ano
- Leve para processamento mesmo em períodos longos (10+ anos)
- Resample mensal reduz para 12 registros/ano

## Limitações e Considerações

### 1. Disponibilidade de Dados
- **BCB SGS:** Dados disponíveis desde 1986
- **Conexão com internet:** Necessária para buscar dados
- **Fallback:** Sistema retorna taxa zero em caso de erro

### 2. Aproximações
- **Taxa do CDI:** Representa investimento em renda fixa de baixo risco
- **Custos não considerados:** IR, taxas administrativas, spread bancário
- **Liquidez:** Assume liquidez instantânea (D+0)

### 3. Realismo vs Simplicidade
- **Realista:** Melhor que caixa sem rendimento
- **Simplificado:** Não considera diferentes produtos de renda fixa (CDB, Tesouro, etc.)
- **Trade-off:** Equilíbrio entre precisão e complexidade

## Testes

### Teste Manual

```python
from backend_projeto.infrastructure.data_handling import YFinanceProvider

loader = YFinanceProvider()

# Buscar CDI
cdi = loader.fetch_cdi_daily('2024-01-01', '2024-01-31')
print(f"CDI médio: {cdi.mean():.6f} ao dia")
print(f"CDI anual: {((1 + cdi.mean()) ** 252 - 1) * 100:.2f}%")

# Taxa mensal
rf_monthly = loader.compute_monthly_rf_from_cdi('2024-01-01', '2024-06-30')
print(f"RF mensal médio: {rf_monthly.mean():.4f}")
```

### Teste Integrado

Use o script de demonstração:
```bash
python examples/scripts/demo_cdi_cash.py
```

## Referências

- **BCB - Sistema SGS:** https://www3.bcb.gov.br/sgspub/
- **Série 12 (CDI):** https://www3.bcb.gov.br/sgspub/consultarvalores/consultarValoresSeries.do?method=getPagina&idSerie=12
- **Biblioteca python-bcb:** https://github.com/wilsonfreitas/python-bcb
- **Convenções de Mercado:** ANBIMA - Metodologia de Cálculo de Taxas

## Próximos Passos

### Melhorias Futuras
1. **Cache de CDI:** Implementar cache para reduzir chamadas ao BCB
2. **Produtos Diversos:** Permitir escolha entre CDI, Tesouro Selic, etc.
3. **Custos Reais:** Adicionar IR e taxas administrativas
4. **Comparação:** Gráfico comparando portfólio com/sem rendimento do caixa
5. **Métricas:** Adicionar "rendimento do caixa" nas estatísticas do portfólio

### Documentação Adicional
- [ ] Adicionar exemplos visuais (gráficos de evolução do caixa)
- [ ] Criar tutorial passo-a-passo no user guide
- [ ] Documentar fórmulas matemáticas completas
- [ ] Adicionar comparação com outros benchmarks de renda fixa
