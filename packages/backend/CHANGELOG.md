# Histórico de Mudanças - API de Análise de Investimentos

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