# Histórico de Mudanças - Frontend

## [0.4.0] - 2025-11-27

### 🚀 Novas Funcionalidades

#### Gráficos Conectados à API

##### Evolução da Alocação Percentual
- ✨ **Dados Reais**: Gráfico de área empilhada conectado ao `allocation_history` da API
- 📊 **Eixo Y Corrigido**: Normalização para 0-100% com `stackOffset="none"` e domain fixo
- 🎨 **Tooltip com Percentuais**: Mostra valores reais em % (não frações)

##### Decomposição de Contribuição de Risco
- ✨ **Dados da API**: Conectado ao `risk_contribution` do backend
- 📊 **Barras Horizontais**: Ordenadas por contribuição (maior para menor)
- 📈 **Estatísticas Dinâmicas**: Top contribuidor e soma dos top 3

##### Evolução do Beta da Carteira
- ✨ **Beta Real**: Conectado ao `beta_evolution` da API (rolling 60 dias vs IBOVESPA)
- 📉 **Linha de Referência Mercado**: Beta = 1.0 (linha cinza pontilhada)
- 🟠 **Linha de Referência Média**: Beta médio da carteira (linha laranja pontilhada)
- 📊 **Estatísticas**: Beta atual, médio, mínimo (filtrado >0.1) e máximo
- 🎯 **Domain Dinâmico**: Eixo Y ajustado automaticamente aos dados

##### Simulação Monte Carlo
- ✨ **Distribuição Comparativa**: MGB (paramétrico) vs Bootstrap Histórico
- 📊 **45 Bins Fixos**: Histograma com densidade proporcional ao valor da carteira
- 💰 **Labels Inteligentes**: Formatação K/M/B conforme o valor
- 📈 **Drift Anualizado**: Calculado dinamicamente dos retornos históricos
- 📉 **Linha de Valor Inicial**: Referência pontilhada no valor atual

### 🐛 Correções

- ✅ **Favicon 404**: Adicionado ícone no `layout.tsx` metadata para evitar erro 404
- ✅ **Beta Mínimo**: Filtrado valores <0.1 (início da carteira sem dados suficientes)
- ✅ **Import Path**: Corrigido import de `useDashboardData` para `@/lib/dashboard-data-context`

### 🔧 Melhorias

#### Componentes Refatorados
- 🔄 **allocation-evolution.tsx**: Reescrito com normalização correta e dados da API
- 🔄 **risk-contribution.tsx**: Convertido de hardcoded para dados dinâmicos
- 🔄 **beta-evolution.tsx**: Novo hook `useDashboardData`, domain dinâmico, linhas de referência
- 🔄 **monte-carlo-distribution.tsx**: Removido `generateDistributionData()`, usa API

---

## [0.3.0] - 2025-11-25

### 🚀 Novas Funcionalidades

#### Tabela de Rentabilidades Dinâmica
- ✨ **Dados do Contexto**: Tabela de rentabilidades agora usa `analysisResult` do `useDashboardData()` em vez de API separada
- 📊 **Sincronização Automática**: Dados atualizados automaticamente quando operações são enviadas
- 🎯 **Sem Dados Hardcoded**: Removidos dados de fallback de 2017-2025 que não correspondiam à simulação

#### Melhorias na Tabela de Ativos
- 💰 **Caixa Atualizado**: Mostra valor real do caixa incluindo rendimento CDI + dividendos
- 📈 **Percentuais Corretos**: Alocação recalculada com valor total correto

### 🐛 Correções

- ✅ **Tabela Rentabilidades**: Corrigido para mostrar dados a partir da data inicial da simulação (não mais 2017)
- ✅ **CDI na Tabela**: Valores de CDI agora correspondem aos dados oficiais do BCB
- ✅ **Caixa na Alocação**: Mostrava R$ 40.000 fixo, agora mostra valor real (~R$ 174.000 com rendimentos)

### 🔧 Melhorias

#### profitability-table.tsx
- 🔄 **Refatoração Completa**: Componente reescrito para usar dados do contexto
- 📝 **Debug Logs**: Adicionados logs para facilitar debugging
- 🎨 **Cores Condicionais**: Mantidas cores verde/vermelho para valores positivos/negativos

#### assets-table.tsx
- 📊 **Dados Reais**: Tabela exibe alocação calculada pelo backend com caixa atualizado

### 📚 Documentação

- 📄 Atualizado CHANGELOG com novas funcionalidades

---

## [0.2.0] - 2025-11-25

### 🚀 Novas Funcionalidades

#### Integração com Backend via Docker
- ✨ **Detecção Automática de Ambiente**: Frontend detecta se está rodando no servidor (SSR) ou cliente
- 🌐 **URLs Duais**: `INTERNAL_API_URL` para comunicação servidor-backend, `NEXT_PUBLIC_API_URL` para cliente
- 📡 **API Route Proxy**: Endpoint `/api/enviar-operacoes` para processar operações via backend

#### Função enviarOperacoes
- 📤 **Nova Função**: `enviarOperacoes()` em `lib/backend-api.ts` para enviar operações financeiras
- ✅ **Validação de Dados**: Verifica formato correto antes de enviar
- 🔄 **Integração com PortfolioAnalyzer**: Dados enviados são processados com preços históricos reais

### 🐳 Infraestrutura Docker

#### Dockerfile Multi-Stage
- ✨ **Build Otimizado**: Dockerfile com 3 estágios (deps, builder, runner)
- 📦 **Monorepo Support**: Copia shared-types corretamente do monorepo
- ⚡ **Next.js Standalone**: Build standalone para imagens mais leves
- 🔧 **Health Check**: Verifica `/` automaticamente

#### Configuração
- ✅ **tsconfig.json**: Paths configurados para importar shared-types
- ✅ **Environment Variables**: NEXT_PUBLIC_API_URL e INTERNAL_API_URL configuradas
- ✅ **Port Configuration**: Porta 3000 exposta corretamente

### 🐛 Correções

- 🔴 **Toast Server-Side Error**: Removido toast() dos interceptors axios (não pode ser chamado no servidor)
- 🟢 **Network Error - localhost:8000**: Implementada detecção de ambiente com URLs corretas
- 🔵 **Zodios Response Format**: API route corrigida para retornar `resp` diretamente (Zodios já retorna dados)
- 🟡 **Port Mismatch**: Todas referências atualizadas de 8001 para 8000
- ⚫ **Module Resolution**: shared-types importado corretamente em Docker build

### 🏗️ Melhorias de Arquitetura

#### API Client (backend-api.ts)
- 🔧 **Refatoração**: Separação clara entre chamadas server-side e client-side
- 🌐 **isServer Detection**: `typeof window === 'undefined'` para detectar ambiente
- 📝 **Comentários**: Documentação inline sobre uso de URLs

#### API Routes
- 📁 **app/api/enviar-operacoes/route.ts**: Proxy Next.js para processar operações
- ✅ **Error Handling**: Tratamento adequado de erros com status codes corretos
- 🔄 **Data Flow**: Cliente → Next.js API Route → Backend Docker → Análise com preços históricos

### 📚 Documentação

- 📖 **README-DOCKER.md**: Atualizado com novidades e comandos para ver logs
- 📖 **SITEMAP.md**: Adicionadas referências às novas funcionalidades

## [0.1.1] - 2025-11-24

### 🐛 Correções

- **Correção do Botão de Login:** Resolvido um problema onde o botão de login não funcionava devido a uma configuração incorreta da opção `skip` no hook `useApi`. A função `execute` do hook agora é chamada corretamente, permitindo que a requisição de login seja enviada ao backend.

### 🧪 Testes

- **Configuração Inicial do Jest:** Adicionada a configuração inicial para o Jest, incluindo `babel.config.js`, `jest.config.js` e `jest.setup.js`, para habilitar testes unitários para os componentes e hooks do frontend.
- **Teste para o Hook `useApi`:** Criado o arquivo `use-api.test.ts` com testes para validar o comportamento do hook `useApi`, garantindo que ele gerencie corretamente os estados de carregamento, dados e erros, bem como a execução condicional da API.

## [0.1.0] - 2025-11-24

### 🎯 Novas Funcionalidades

- **Implementação da Página de Login:** Desenvolvimento inicial da página de login com formulário de autenticação.
- **Integração com API de Autenticação:** Conectado o formulário de login com o endpoint de autenticação do backend usando o hook `useApi`.
