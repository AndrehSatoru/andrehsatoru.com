# Integração com CDI - Rendimento do Caixa

## Visão Geral

A partir da versão 1.3.0, o sistema implementa o rendimento automático do CDI (Certificado de Depósito Interbancário) sobre o caixa não investido do portfólio. Esta funcionalidade torna a análise de portfólio mais realista, refletindo que na prática o dinheiro não investido em ações rende juros.

## Motivação

Anteriormente, o caixa não investido era tratado como valor estático que apenas diminuía com novas compras. Isso não refletia a realidade do mercado brasileiro, onde:

- Recursos não investidos ficam tipicamente em produtos de renda fixa
- O CDI é o principal benchmark para investimentos de baixo risco
- Investidores conservadores mantêm parte do capital em liquidez diária que rende próximo ao CDI

## Arquitetura da Implementação

### 1. Fonte de Dados: Banco Central do Brasil (BCB)

A integração utiliza a biblioteca `python-bcb` para acessar o Sistema Gerenciador de Séries Temporais (SGS) do Banco Central.

**Série utilizada:** 12 - Taxa de juros - CDI

```python
from bcb import sgs

# Buscar CDI diário
cdi_anual = sgs.get({'CDI': 12}, start=start_date, end=end_date)
```

### 2. Conversão de Taxas

O CDI é fornecido como **taxa anual em percentual**. Precisamos converter para **taxa diária em decimal**:

**Fórmula:**
```
taxa_diária = (1 + taxa_anual/100)^(1/252) - 1
```

Onde:
- `taxa_anual`: Taxa fornecida pelo BCB (ex: 13.65 para 13,65% a.a.)
- `252`: Dias úteis no ano (convenção do mercado brasileiro)
- `taxa_diária`: Taxa decimal (ex: 0.0004837 para 0.04837% ao dia)

**Exemplo prático:**
- CDI de 13,65% ao ano
- Taxa diária: (1 + 0.1365)^(1/252) - 1 = 0.0004837
- Em R$ 100.000: rendimento diário de ~R$ 48,37

### 3. Implementação no YFinanceProvider

#### Método `fetch_cdi_daily()`

```python
def fetch_cdi_daily(self, start_date: str, end_date: str) -> pd.Series:
    """
    Busca taxas diárias do CDI do BCB.
    
    Returns:
        pd.Series com taxas diárias em decimal, índice DatetimeIndex
    """
    # 1. Buscar dados do BCB
    cdi_anual = sgs.get({'CDI': 12}, start=start_date, end=end_date)
    
    # 2. Converter para taxa diária decimal
    cdi_diario = ((1 + cdi_anual['CDI'] / 100.0) ** (1.0 / 252.0) - 1.0)
    
    # 3. Preencher dias não úteis (finais de semana/feriados)
    full_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    cdi_diario = cdi_diario.reindex(full_dates).ffill().fillna(0.0)
    
    return cdi_diario
```

**Tratamento de erros:**
- Se não houver dados disponíveis: retorna série com taxa zero
- Se houver erro de conexão: log de warning e retorna taxa zero
- Dias sem dados: forward fill (repete última taxa disponível)

#### Método `compute_monthly_rf_from_cdi()`

```python
def compute_monthly_rf_from_cdi(self, start_date: str, end_date: str) -> pd.Series:
    """
    Calcula taxa livre de risco mensal a partir do CDI diário.
    
    Usado nos endpoints Fama-French quando rf_source='selic'
    
    Returns:
        pd.Series com taxas mensais compostas, índice month-end
    """
    # 1. Buscar CDI diário
    cdi_daily = self.fetch_cdi_daily(start_date, end_date)
    
    # 2. Calcular retorno composto mensal
    # RF_mensal = Produto((1 + r_diário)) - 1
    monthly_rf = cdi_df.resample('M').apply(lambda x: (1 + x).prod() - 1)['CDI']
    
    return monthly_rf
```

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

### Comparação Antes vs Depois

**Cenário:** R$ 100.000 com R$ 10.000 investidos em ações, R$ 90.000 em caixa, período de 1 ano

| Métrica | Antes (sem CDI) | Depois (com CDI ~13,65% a.a.) | Diferença |
|---------|-----------------|-------------------------------|-----------|
| Caixa inicial | R$ 90.000 | R$ 90.000 | - |
| Caixa final | R$ 90.000 | R$ 102.285 | +R$ 12.285 |
| Rendimento do caixa | 0% | 13,65% | +13,65% |
| Impacto no portfólio total | Nenhum | Significativo | - |

### Realismo Financeiro

**Antes:**
- Caixa era tratado como "dinheiro embaixo do colchão"
- Não refletia custo de oportunidade
- Subestimava retorno total do portfólio

**Depois:**
- Caixa rende taxa próxima ao CDI (como na prática)
- Reflete melhor estratégia conservadora (parte em ações, parte em renda fixa)
- Permite comparação justa com benchmarks

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
