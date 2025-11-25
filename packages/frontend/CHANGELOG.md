# Histórico de Mudanças - Frontend

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
