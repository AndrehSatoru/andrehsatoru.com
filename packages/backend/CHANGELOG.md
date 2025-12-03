# Histórico de Mudanças - API de Análise de Investimentos

## [1.8.0] - 2025-12-03

### 🚀 Novas Funcionalidades

#### Distance Correlation Matrix
- ✨ **Método `_generate_distance_correlation_matrix()`**: Calcula correlação de distância entre todos os pares de ativos
- 📊 **dCor (Székely et al.)**: Mede dependência estatística não-linear (0 = independência, 1 = dependência)
- 🔢 **Fórmula**: $dCor(X,Y) = \frac{dCov(X,Y)}{\sqrt{dVar(X) \cdot dVar(Y)}}$
- 📈 **Estatísticas**: Retorna média, mínimo e máximo da matriz

#### TMFG (Triangulated Maximally Filtered Graph)
- ✨ **Método `_generate_tmfg_graph()`**: Constrói grafo planar triangulado das correlações
- 🔗 **Algoritmo de Tumminello**: Filtra conexões mantendo apenas as mais significativas
- 🎯 **Detecção de comunidades**: Usa algoritmo Louvain para identificar clusters de ativos
- 📏 **Métricas de centralidade**: Degree centrality e betweenness centrality por ativo
- 📦 **networkx**: Adicionado ao requirements.txt para análise de grafos

### 📊 Novos Campos no Response

| Campo | Descrição |
|-------|-----------|
| `distance_correlation_matrix` | Matriz dCor com assets, matrix, avg/min/max |
| `tmfg_graph` | Nós (id, group, degree, betweenness, weight) e arestas (source, target, correlation) |

### 🔧 Dependências

- ➕ **networkx==3.2.1**: Biblioteca para análise de redes e grafos

---

## [1.7.0] - 2025-11-28

### 🚀 Novas Funcionalidades

#### 6 Novas Análises Avançadas
- ✨ **Análise CAPM**: Cálculo de Alpha, Beta, Sharpe, Treynor e R² por ativo e portfólio
- ✨ **Otimização Markowitz**: Fronteira eficiente com portfólios ótimos (máximo Sharpe, mínima volatilidade, máximo retorno)
- ✨ **Análise Fama-French 3 Fatores**: Exposição a MKT, SMB (tamanho) e HML (valor) por ativo
- ✨ **VaR Backtest**: Validação do modelo VaR com teste de Kupiec e classificação Basel (verde/amarelo/vermelho)
- ✨ **Risk Attribution Detalhada**: MCR, contribuição ao risco e benefício de diversificação por ativo
- ✨ **Incremental VaR (IVaR)**: Impacto marginal de cada ativo no VaR do portfólio

#### Simulação Monte Carlo Aprimorada
- 📈 **100.000 simulações**: Aumentado de 5.000 para 100.000 paths para distribuição mais suave
- 🧮 **Fórmula MGB corrigida**: Correção do drift que estava sendo dividido por 252 duas vezes
- 📊 **50 bins**: Resolução aumentada de 30 para 50 bins no histograma
- 📉 **Normalização em %**: Valores do eixo Y agora mostram percentual de simulações

### 🔧 Melhorias

#### Serialização JSON
- ✅ **numpy.bool_ → bool**: Corrigido erro de serialização em `_generate_var_backtest()`

#### Busca de Benchmark IBOVESPA
- ✅ **CAPM corrigido**: Usando `fetch_stock_prices(['^BVSP'])` com cache em vez de `fetch_benchmark_data`

### 📊 Novos Campos no Response

| Campo | Descrição |
|-------|-----------|
| `capm_analysis` | Alpha, Beta, Sharpe, Treynor, R² por ativo e métricas do portfólio |
| `markowitz_optimization` | Fronteira eficiente e portfólios ótimos com pesos sugeridos |
| `fama_french` | Exposição aos 3 fatores FF por ativo e portfólio |
| `var_backtest` | Resultado do backtest VaR com zona Basel e lista de exceções |
| `risk_attribution_detailed` | MCR, contribuição ao risco, VaR e diversificação por ativo |
| `incremental_var` | IVaR, MVaR, Component VaR e benefício de diversificação |

---

## [1.6.0] - 2025-11-28

### 🏗️ Refatoração Arquitetural

#### Reorganização do Módulo `analysis.py`
O arquivo monolítico `analysis.py` (2242 linhas) foi reorganizado em módulos especializados para melhor manutenibilidade:

| Módulo | Linhas | Responsabilidade |
|--------|--------|------------------|
| `analysis.py` | 128 | Entry point - re-exporta funções para compatibilidade |
| `risk_metrics.py` | 222 | VaR, ES (paramétrico, histórico, EVT), Drawdown |
| `stress_testing.py` | 140 | Testes de estresse, backtesting de VaR |
| `covariance.py` | 260 | Matriz de covariância Ledoit-Wolf, atribuição de risco |
| `fama_french.py` | 127 | Modelos Fama-French FF3 e FF5 |
| `risk_engine.py` | 122 | Classe RiskEngine para orquestrar análises |
| `portfolio_analyzer.py` | 1270 | Classe PortfolioAnalyzer (análise completa de portfólio) |

#### Benefícios da Reorganização
- ✅ **Modularidade**: Cada arquivo tem uma responsabilidade clara (Single Responsibility)
- ✅ **Manutenibilidade**: Mais fácil encontrar, entender e modificar código
- ✅ **Testabilidade**: Funções isoladas são mais fáceis de testar unitariamente
- ✅ **Backward Compatibility**: O `analysis.py` continua funcionando como entry point
- ✅ **Colaboração**: Equipes podem trabalhar em módulos diferentes sem conflitos

### 🚀 Novas Funcionalidades

#### Testes de Estresse Reais
- ✨ **`_generate_stress_tests()`**: Implementado cálculo real de testes de estresse
- 📊 **Cenários Históricos**: Crise 2008, COVID-19, Crise Subprime
- 📈 **Cenários Hipotéticos**: Choque de Taxa +3%, Recessão Global, Crise Cambial
- 🎯 **Impacto Personalizado**: Baseado na volatilidade e correlação do portfólio

### 🔧 Melhorias

#### Função `drawdown()`
- 🐛 Corrigido erro quando o índice do DataFrame não é datetime
- ✅ Agora funciona com índices numéricos e de datetime

#### Testes Unitários
- 🔧 Atualizados caminhos de mock nos testes do `RiskEngine`
- ✅ 65 testes passando, 2 skipped (integração)

### 📁 Estrutura de Arquivos Atualizada

```
packages/backend/src/backend_projeto/domain/
├── analysis.py           # Entry point (re-exports)
├── risk_metrics.py       # VaR, ES, Drawdown
├── stress_testing.py     # Stress tests, Backtest VaR
├── covariance.py         # Covariance, Risk Attribution
├── fama_french.py        # FF3, FF5 models
├── risk_engine.py        # RiskEngine class
├── portfolio_analyzer.py # PortfolioAnalyzer class
├── entities.py           # Domain entities
├── value_objects.py      # Value objects
├── services.py           # Domain services
├── repositories.py       # Repository interfaces
└── exceptions.py         # Domain exceptions
```

---

## [1.5.0] - 2025-11-27

### 🚀 Novas Funcionalidades

#### Contribuição de Risco por Ativo
- ✨ **`_generate_risk_contribution()`**: Novo método que calcula a contribuição de cada ativo para a volatilidade total
- 📊 **Risk Attribution**: Usa função `risk_attribution()` existente para calcular contribuições marginais
- 📈 **Ordenação por Contribuição**: Ativos ordenados do maior para o menor contribuidor de risco

#### Evolução do Beta da Carteira
- ✨ **`_generate_beta_evolution()`**: Novo método para calcular beta rolling vs IBOVESPA (^BVSP)
- 📉 **Beta Rolling 60 dias**: Janela de 60 dias úteis para cálculo do beta
- 📅 **Dados Mensais**: Agrupamento por mês para não sobrecarregar o gráfico
- 🎯 **Estatísticas**: Beta atual, médio, mínimo e máximo calculados dinamicamente

#### Simulação Monte Carlo
- ✨ **`_generate_monte_carlo_simulation()`**: Simulação comparativa MGB vs Bootstrap Histórico
- 📊 **MGB (Geometric Brownian Motion)**: Simulação paramétrica com volatilidade histórica
- 🔄 **Bootstrap Histórico**: Simulação por reamostragem de retornos históricos reais
- 📈 **5.000 simulações**: Por padrão, 5.000 paths para cada método
- 📉 **45 bins dinâmicos**: Histograma com número fixo de bins, independente do valor da carteira
- 💰 **Formatação inteligente**: Labels adaptados (K, M, B) conforme o valor

### 🔧 Melhorias

#### run_analysis()
- 🆕 **Novos campos**: `risk_contribution`, `beta_evolution`, `monte_carlo` adicionados ao retorno
- 📊 **Dados completos**: Todos os dados necessários para os gráficos do dashboard em uma única chamada

### 📊 Novos Endpoints de Dados

| Campo | Descrição |
|-------|-----------|
| `risk_contribution` | Lista de `{asset, contribution}` ordenada por contribuição |
| `beta_evolution` | Lista de `{date, beta}` com evolução mensal |
| `monte_carlo.distribution` | Dados do histograma para ambas distribuições |
| `monte_carlo.mgb` | Estatísticas da simulação MGB (mediana, percentis, etc) |
| `monte_carlo.bootstrap` | Estatísticas da simulação Bootstrap |

---

## [1.4.0] - 2025-11-25

### 🚀 Novas Funcionalidades

#### Dividendos no Caixa
- ✨ **Dividendos Automáticos**: Implementado recebimento automático de dividendos/proventos no caixa
- 📈 **Busca via Yahoo Finance API**: Integração direta com a API do Yahoo Finance para buscar histórico de dividendos
- 💰 **Cálculo por Ação**: Dividendos calculados corretamente: `quantidade_ações × valor_por_ação`
- 🔄 **Processamento por Data**: Dividendos são creditados no caixa na data de pagamento

#### Tabela de Rentabilidades Mensais
- 📊 **Novo Endpoint**: `/api/v1/portfolio/monthly-returns` para dados da tabela de rentabilidade
- 📅 **Dados Dinâmicos**: Tabela gerada a partir dos dados reais do portfólio, não mais hardcoded
- 🎯 **Sincronização com Frontend**: Tabela usa `analysisResult` do contexto em vez de API separada

### 🐛 Correções Críticas

#### CDI Corrigido
- ✅ **Taxa Diária Correta**: BCB série 12 retorna taxa diária em %, não anual. Removida conversão incorreta
- ✅ **Sem Forward Fill**: CDI não rende em fins de semana/feriados - removido forward fill que inflacionava os valores
- ✅ **Valores Corretos**: CDI 2020 agora mostra 2.75% (antes: 4.03%), alinhado com dados oficiais

#### Dividendos Corrigidos
- ✅ **Busca Direta pela API**: Substituída biblioteca yfinance (que falhava) por chamada direta à API do Yahoo Finance
- ✅ **Tratamento de Erros**: Logs detalhados quando dividendos não são encontrados

#### Caixa Corrigido
- ✅ **Valor Atualizado**: `self.cash` agora reflete CDI + dividendos acumulados, não mais valor inicial - investido
- ✅ **Alocação Correta**: Tabela de ativos mostra caixa real com rendimentos

#### Normalização de Datas
- ✅ **Transações**: Datas das transações normalizadas e mapeadas para primeiro dia útil disponível
- ✅ **Dividendos**: Datas de pagamento mapeadas corretamente para o índice de posições

### 🔧 Melhorias

#### YFinanceProvider
- 🆕 **`fetch_dividends()` reescrito**: Usa API direta do Yahoo Finance em vez da biblioteca yfinance
- 🔄 **Requests paralelos**: ThreadPoolExecutor para buscar dividendos de múltiplos ativos
- 📝 **Logs informativos**: Log de quantidade de dividendos encontrados por ativo

#### PortfolioAnalyzer
- 🆕 **`_generate_monthly_returns()`**: Novo método para gerar tabela de rentabilidades mensais
- 🔄 **Cálculo do CDI anual**: Composição correta dos retornos mensais do CDI
- 📊 **Acumulados**: Cálculo correto de acumulado do fundo e acumulado do CDI desde início

### 📊 Comparação de Valores

**CDI Anual (Sistema vs Referência BCB):**
| Ano  | Antes  | Depois | Referência |
|------|--------|--------|------------|
| 2020 | 4.03%  | 2.75%  | 2.77% ✅   |
| 2021 | 6.45%  | 4.44%  | 4.40% ✅   |
| 2022 | 18.49% | 12.38% | 12.37% ✅  |
| 2023 | 19.67% | 13.03% | 13.05% ✅  |
| 2024 | 16.10% | 10.89% | 10.87% ✅  |
| 2025 | 18.98% | 12.71% | 12.69% ✅  |

---

## [1.3.0] - 2025-11-25

### 🚀 Novas Funcionalidades

#### Rendimento do CDI no Caixa
- ✨ **CDI no Caixa Não Investido**: Implementado rendimento automático do CDI no caixa disponível do portfólio
- 📈 **Busca de Dados Reais do CDI**: Integração com BCB (Banco Central do Brasil) via biblioteca `bcb` para buscar taxas diárias do CDI (Série 12 do SGS)
- 🔄 **Aplicação Diária**: O caixa agora é atualizado diariamente com a fórmula: `caixa_novo = caixa_anterior × (1 + taxa_CDI_diária)`
- 💰 **Cálculo Realista**: Valor do portfólio agora reflete a realidade onde o caixa não fica "parado" sem rendimento
- 📊 **Taxa Livre de Risco Mensal**: Novo método `compute_monthly_rf_from_cdi()` que calcula taxa mensal composta a partir do CDI diário

#### Novos Métodos no YFinanceProvider
- 🆕 **`fetch_cdi_daily(start_date, end_date)`**: Busca taxas diárias do CDI do BCB
  - Converte taxa anual (%) para taxa diária em decimal: `(1 + taxa_anual/100)^(1/252) - 1`
  - Preenche dias não úteis com forward fill
  - Tratamento de erros com fallback para taxa zero
- 🆕 **`compute_monthly_rf_from_cdi(start_date, end_date)`**: Calcula taxa livre de risco mensal
  - Utilizado nos endpoints Fama-French quando `rf_source='selic'`
  - Retorna série mensal com taxas compostas
  - Corrige erro anterior onde o método era chamado mas não existia

### 🔧 Melhorias

#### PortfolioAnalyzer
- 🔄 **Refatoração do `_calculate_portfolio_value()`**: Lógica completamente reescrita para aplicar rendimento do CDI
- 📅 **Processamento Dia-a-Dia**: Loop através de cada data do índice para aplicar rendimentos e transações na ordem correta
- 🎯 **Precisão Temporal**: Transações organizadas por data para subtração eficiente do caixa
- 🛡️ **Proteção de Caixa Negativo**: Caixa sempre ≥ 0 após cada operação

### 🐛 Correções

- ✅ **Endpoints Fama-French**: Corrigido erro onde `compute_monthly_rf_from_cdi()` era chamado mas não existia
- ✅ **Taxa Livre de Risco**: Implementação completa da fonte 'selic' para rf_source nos endpoints FF3/FF5
- ✅ **Cálculo de Portfólio**: Valor total agora inclui corretamente: ativos + caixa rendendo CDI

### 📚 Documentação

- 📄 **Exemplo de Demonstração**: Novo script `examples/scripts/demo_cdi_cash.py` mostrando funcionamento do CDI
- 📄 **Teste Unitário**: Arquivo `tests/test_cdi_cash_return.py` com testes do rendimento do CDI
- 📖 **Documentação da Arquitetura**: Atualizado com descrição da integração BCB/CDI

### 📊 Impacto

**Antes:**
```python
# Caixa apenas diminuía, sem rendimento
cash_series = pd.Series(initial_value, index=dates)
for tx in transactions:
    cash_series.loc[tx_date:] -= tx_value
```

**Depois:**
```python
# Caixa rende CDI diariamente e diminui com transações
current_cash = initial_value
for date in dates:
    # 1. Aplicar rendimento do CDI
    current_cash *= (1 + cdi_rate[date])
    # 2. Subtrair transações do dia
    current_cash -= transactions_on_date
    cash_series[date] = max(0, current_cash)
```

**Exemplo Prático:**
- Capital inicial: R$ 100.000
- Investido em ações: R$ 10.000
- Caixa: R$ 90.000
- CDI ~13,65% a.a. (2024)
- Rendimento do caixa em 1 ano: ~R$ 12.285 (em vez de R$ 0)

---

## [1.2.0] - 2025-11-25

### 🚀 Novas Funcionalidades

#### Integração de Preços Históricos
- ✨ **Busca Automática de Cotações**: Implementada integração com YFinance para buscar preços históricos reais de ações
- 📊 **Cálculo Automático de Quantidade**: Sistema calcula automaticamente `Quantidade = Valor / Preço` para cada operação
- 🔍 **Janela de Busca Inteligente**: Busca preços em ±5 dias caso a data exata não tenha dados de mercado
- 📝 **Logging Detalhado**: Logs mostram cálculos realizados: "Operação VALE3 em 2019-10-10: valor=10000.00, preço=50.25, quantidade=199.00"
- 🛡️ **Fallback Robusto**: Se preço não for encontrado, usa valor como preço e quantidade=1.0

#### Endpoint `/api/v1/transactions/processar-operacoes`
- 🔄 **Refatoração Completa**: Endpoint reescrito para integrar PortfolioAnalyzer com dados históricos
- ✅ **Validação Aprimorada**: Verifica formato de data e disponibilidade de dados
- 📈 **Mapeamento Correto**: DataFrame agora usa colunas corretas ['Data', 'Ativo', 'Quantidade', 'Preco']

### 🐳 Infraestrutura Docker

#### Docker Compose
- ✨ **Setup Completo**: Implementado docker-compose.yml com 3 serviços (backend, frontend, redis)
- 🔧 **Health Checks**: Todos os serviços com verificações de saúde configuradas
- 🌐 **Networking Otimizado**: Rede interna 'app-network' com DNS Docker para comunicação entre containers
- 📦 **Volumes Persistentes**: Redis com armazenamento persistente
- 🔌 **Portas Configuradas**: Backend (8000), Frontend (3000), Redis (6380→6379)

#### Dockerfile Melhorado
- ✅ **CMD Corrigido**: Usa caminho completo `/app/venv/bin/python -m uvicorn`
- ✅ **PYTHONPATH Configurado**: `/app/src` para resolução correta de módulos
- ✅ **Workers Uvicorn**: 4 workers para melhor performance
- ✅ **Health Check**: Endpoint `/api/v1/status` verificado automaticamente

### 🐛 Correções

- 🔴 **DataFrame Columns Error**: Corrigido mapeamento de colunas de Tipo/Valor para Quantidade/Preco
- 🟢 **Module Import Error**: PYTHONPATH configurado corretamente no Dockerfile
- 🔵 **Port Conflicts**: Redis movido para porta 6380 externa
- 🟡 **CORS Configuration**: Permitido localhost:3000 no backend

### 📚 Documentação

- 📖 **API Documentation**: Criado `docs/developer-guide/api/processar-operacoes.md` com guia completo
- 📖 **Docker Guide**: Atualizado `docs/developer-guide/deployment/docker-compose.md` com troubleshooting
- 📖 **README Updates**: Seção "Novidades Recentes" adicionada ao docs/README.md

## [1.1.1] - 2025-11-24

### 🏗️ Melhorias de Arquitetura

- **Refatoração para Clean Architecture:** A estrutura do backend foi extensivamente refatorada para aderir mais estritamente aos princípios da Clean Architecture. Módulos foram explicitamente organizados em camadas de `domain` (lógica de negócio e entidades), `application` (casos de uso e orquestração) e `infrastructure` (detalhes de implementação como provedores de dados e visualização). Esta reorganização visa melhorar a separação de preocupações, a testabilidade e a manutenibilidade do código.

### 🧪 Testes

- **Correção Abrangente de Testes:** Foram corrigidos diversos testes unitários e de integração que falhavam devido à refatoração da arquitetura e a inconsistências lógicas. Isso incluiu:
    - Correções em `tests/unit/test_core_engines.py` para alinhar asserções e mocks com a nova estrutura.
    - Atualização e adequação dos testes em `tests/unit/test_dashboard_generator.py` à nova API da classe `DashboardGenerator`.
    - Resolução de problemas de indexação de datas e validação de dados em `tests/unit/test_portfolio_analyzer.py`.
    - Ajustes nas chamadas de função e no tratamento de retornos em `tests/unit/test_risk_engine.py`.
- **`openapi.json` Gerado:** O script de geração do `openapi.json` foi corrigido e executado para garantir que os testes de contrato da API passem, validando as definições dos endpoints.

### 📚 Documentação

- **`RELATORIO_ARQUITETURA.md` Atualizado:** O relatório de arquitetura foi atualizado para refletir as melhorias implementadas e o alinhamento com a Clean Architecture.

## [1.1.0] - 2025-10-29

### 📚 Documentação

- **`README.md` Atualizado:** O `README.md` principal foi completamente reescrito para refletir o estado atual do projeto.
- **Adicionadas Informações do Frontend:** O `README.md` agora inclui informações sobre o frontend em React, incluindo instruções de instalação e inicialização.
- **Diagrama de Arquitetura Corrigido:** O diagrama de arquitetura no `README.md` foi atualizado para representar com precisão a estrutura modular do backend e a inclusão do frontend.
- **Guia de Início Rápido Melhorado:** O guia "Início Rápido" agora prioriza o Docker Compose para uma configuração simplificada e fornece instruções separadas para o desenvolvimento manual.
- **Adicionado `.env.example`:** Um arquivo `.env.example` foi adicionado ao diretório raiz para facilitar a configuração do ambiente.
- **Comandos de Teste Atualizados:** Os comandos de teste no `README.md` agora correspondem aos comandos usados no pipeline de CI/CD.
- **Links Quebrados Corrigidos:** Links quebrados na documentação foram reparados.

### 🏗️ Melhorias de Arquitetura

- **Adicionado `.env.example`:** Criado um arquivo `.env.example` para padronizar a configuração de variáveis de ambiente.

## [1.0.0] - 2025-10-09

### 🎯 Novas Funcionalidades

#### Análise Técnica
- ✨ **Médias Móveis (SMA/EMA)**: Endpoint `/ta/moving-averages` com janelas customizáveis
- ✨ **MACD**: Endpoint `/ta/macd` com parâmetros configuráveis (fast, slow, signal)
- ✨ **Filtros de Payload**: `include_original` e `only_columns` para reduzir o tamanho da resposta

#### Métricas de Risco Avançadas
- ✨ **Incremental VaR (IVaR)**: Endpoint `/risk/ivar` - sensibilidade do VaR a mudanças nos pesos
- ✨ **Marginal VaR (MVaR)**: Endpoint `/risk/mvar` - impacto de remover cada ativo
- ✨ **VaR Relativo**: Endpoint `/risk/relvar` - risco de underperformance vs benchmark

### 🏗️ Melhorias de Arquitetura

#### Injeção de Dependência
- 📦 Criado `api/deps.py` com factories centralizadas
- 🔧 Todos os endpoints refatorados para usar `Depends()`
- ✅ Redução de ~70% no código boilerplate
- ✅ Facilita testes com mocks

#### Validações de Entrada
- ✅ `assets`: não vazios, limitados a 100 tickers
- ✅ `weights`: mesmo tamanho que assets, soma > 0
- ✅ `windows` (TA): positivos e únicos
- ✅ `MACD`: fast < slow
- ✅ `benchmark`: não vazio

#### Tratamento de Erros
- 🔴 **ValueError** → 422 (validação de entrada)
- 🟡 **DataProviderError** → 503 (serviço externo)
- 🔵 **InvalidTransactionFileError** → 400
- 🟢 **DataValidationError** → 422
- ⚫ **Exceção genérica** → 500 com logging detalhado

### 📚 Documentação

#### Docstrings Completas
- 📖 `incremental_var()`: fórmulas, parâmetros, exemplos, complexidade
- 📖 `marginal_var()`: explicação detalhada, diferenças conceituais
- 📖 `relative_var()`: casos de uso, interpretação
- 📖 `var_parametric()`: suposições (normalidade), métodos
- 📖 `es_parametric()`: fórmula matemática

#### Swagger/OpenAPI
- 🏷️ Tags organizadas por categoria
- 📝 Descrições em português nos endpoints
- 📊 Metadados da API (título, descrição, versão)

#### Guias
- 📄 `API_QUICKSTART.md`: exemplos práticos de uso
- 📄 `IMPROVEMENTS_SUMMARY.md`: detalhamento técnico das melhorias
- 📄 `CHANGELOG.md`: este arquivo

### ⚡ Performance

#### Middleware
- 🗜️ **GZip**: compressão automática para respostas > 1KB
- 📊 **Logging**: Rastreamento de ID de requisição e tempo de processamento
- 🔍 **Observabilidade**: Headers `X-Request-ID` e `X-Process-Time`

#### Otimizações
- 🎯 Filtros reduzem o payload em até 80%
- 💾 Cache automático de dados históricos
- 🚀 Injeção de dependência reduz o overhead

### 🧪 Testes

#### Nova Cobertura
- ✅ `test_ta_endpoints.py`: MAs e MACD
- ✅ `test_ta_endpoints_extra.py`: EMA, validações
- ✅ `test_risk_var_extensions.py`: IVaR, MVaR, RelVaR
- ✅ `test_risk_var_extensions_more.py`: métodos std/ewma, edge cases
- ✅ `test_risk_var_extensions_evt.py`: cobertura EVT com mocks
- ✅ `test_risk_var_extensions_errors.py`: validações, xfail para garch

#### Estratégia
- 🎭 Monkeypatch para evitar chamadas externas
- 🔧 Fixtures reutilizáveis
- 🚨 Testes de erro retornando 422/500

### 📦 Dependências

#### requirements.txt
- 📌 Versões fixadas para reprodutibilidade
- 📂 Organizado por categoria
- 💬 Comentários indicando dependências opcionais

### 🔄 Mudanças Quebradas (Breaking Changes)

Nenhuma. Todas as mudanças são retrocompatíveis.

### 🐛 Correções

- 🔧 Benchmark ausente agora retorna 422 ao invés de 200 com erro no corpo da resposta
- 🔧 Validações impedem que erros cheguem à lógica de negócio
- 🔧 Mensagens de erro mais descritivas e consistentes

---

## Próximas Versões (Roadmap)

### [1.2.0] - Planejado
- [ ] ?
- [ ] ?
- [ ] ?
- [ ] ?
- [ ] ?

### [1.3.0] - Planejado
- [ ] ?
- [ ] ?
- [ ] ?
- [ ] ?
- [ ] ?