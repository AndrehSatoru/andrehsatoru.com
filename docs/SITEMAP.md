# 🗺️ Mapa da Documentação

Guia rápido para encontrar informações na documentação do projeto.

## 🚀 Começando

| Você quer... | Vá para... |
|-------------|-----------|
| Rodar o projeto rapidamente | [Quick Start](../README.md#-quick-start) |
| Entender o que o projeto faz | [Guia do Usuário](user-guide/getting-started.md) |
| Configurar ambiente de dev | [Setup Local](developer-guide/setup/local-development.md) |
| Usar Docker | [README-DOCKER.md](../README-DOCKER.md) 🐳 |

## 👥 Por Perfil

### 🎯 Usuário Final / Investidor
```
├── 📖 Guia do Usuário
│   ├── Primeiros Passos ──────────── user-guide/getting-started.md
│   ├── Funcionalidades ──────────── user-guide/features/
│   └── Tutoriais ────────────────── user-guide/tutorials/
```

### 👨‍💻 Desenvolvedor
```
├── 🛠️ Guia do Desenvolvedor
│   ├── Setup
│   │   ├── Desenvolvimento Local ─── developer-guide/setup/local-development.md
│   │   └── Variáveis de Ambiente ─── developer-guide/setup/environment-vars.md
│   ├── Arquitetura
│   │   ├── Overview ─────────────── developer-guide/architecture/overview.md
│   │   ├── Backend ──────────────── developer-guide/architecture/backend-architecture.md
│   │   ├── Frontend ─────────────── developer-guide/architecture/frontend-architecture.md
│   │   └── Integração CDI ───────── developer-guide/architecture/cdi-integration.md
│   ├── API
│   │   ├── Quick Start ──────────── developer-guide/api/quickstart.md
│   │   └── Endpoints ────────────── developer-guide/api/endpoints/
│   ├── Deployment
│   │   └── Docker Compose ───────── developer-guide/deployment/docker-compose.md
│   └── Testing ──────────────────── developer-guide/testing/
```

### ⚙️ DevOps / SysAdmin
```
├── 🔧 Guia de Operações
│   ├── Deployment ───────────────── operations/deployment.md
│   ├── Docker Compose (User) ────── ../README-DOCKER.md
│   ├── Docker Compose (Tech) ────── developer-guide/deployment/docker-compose.md
│   └── Segurança ────────────────── operations/security.md
```

## 📦 Por Tecnologia

### 🐳 Docker
- **[Guia do Usuário](../README-DOCKER.md)** - Como usar, comandos, troubleshooting
- **[Guia Técnico](developer-guide/deployment/docker-compose.md)** - Arquitetura, configuração avançada
- **[Deploy em Produção](operations/deployment.md#docker-compose-recomendado)** - Deploy com Docker

### 🎨 Frontend (Next.js)
- **[Arquitetura Frontend](developer-guide/architecture/frontend-architecture.md)**
- **[Setup Local](developer-guide/setup/local-development.md#opção-2-desenvolvimento-manual)**
- **[Dockerfile](../packages/frontend/Dockerfile)** - Configuração Docker

### ⚙️ Backend (FastAPI)
- **[Arquitetura Backend](developer-guide/architecture/backend-architecture.md)**
- **[API Quick Start](developer-guide/api/quickstart.md)**
- **[Endpoints](developer-guide/api/endpoints/)**
- **[Processar Operações](developer-guide/api/processar-operacoes.md)** - Endpoint de análise com preços históricos
- **[Integração CDI](developer-guide/architecture/cdi-integration.md)** - Rendimento do caixa com dados do BCB
- **[Backend Dockerfile](../packages/backend/backend.Dockerfile)**

### 🗄️ Redis
- **[Docker Compose Config](../docker-compose.yml)** - Configuração do Redis
- **[Variáveis de Ambiente](developer-guide/setup/environment-vars.md)**

## 🔍 Por Tarefa

### Instalação e Setup

| Tarefa | Documento | Seção |
|--------|-----------|-------|
| Instalar com Docker | [README-DOCKER.md](../README-DOCKER.md) | Quick Start |
| Instalar manualmente | [local-development.md](developer-guide/setup/local-development.md) | Desenvolvimento Manual |
| Configurar variáveis | [environment-vars.md](developer-guide/setup/environment-vars.md) | Todas |
| Primeiro deploy | [deployment.md](operations/deployment.md) | Docker Compose |

### Desenvolvimento

| Tarefa | Documento | Seção |
|--------|-----------|-------|
| Entender arquitetura | [overview.md](developer-guide/architecture/overview.md) | Todas |
| Criar novo endpoint | [backend-architecture.md](developer-guide/architecture/backend-architecture.md) | API Structure |
| Adicionar componente | [frontend-architecture.md](developer-guide/architecture/frontend-architecture.md) | Components |
| Testar API | [quickstart.md](developer-guide/api/quickstart.md) | Exemplos |

### Operações

| Tarefa | Documento | Seção |
|--------|-----------|-------|
| Deploy em produção | [deployment.md](operations/deployment.md) | Docker Compose |
| Monitorar containers | [docker-compose.md](developer-guide/deployment/docker-compose.md) | Monitoramento |
| Troubleshooting | [README-DOCKER.md](../README-DOCKER.md) | Troubleshooting |
| Configurar segurança | [security.md](operations/security.md) | Todas |
| Ver logs | [docker-compose.md](developer-guide/deployment/docker-compose.md) | Logs |

## 🆘 Preciso de Ajuda Com...

### "Não consigo rodar o projeto"
1. Tente Docker primeiro: [README-DOCKER.md](../README-DOCKER.md)
2. Se não funcionar: [Troubleshooting](../README-DOCKER.md#-troubleshooting)
3. Ainda com problemas: [Setup Manual](developer-guide/setup/local-development.md)

### "Como usar a API?"
1. Comece aqui: [API Quick Start](developer-guide/api/quickstart.md)
2. Liste endpoints: [API Endpoints](developer-guide/api/endpoints/)
3. Endpoint principal: [Processar Operações](developer-guide/api/processar-operacoes.md) - Com preços históricos
4. Documentação interativa: `http://localhost:8000/docs`

### "Quero contribuir"
1. Setup: [Desenvolvimento Local](developer-guide/setup/local-development.md)
2. Entenda: [Arquitetura](developer-guide/architecture/overview.md)
3. Leia: Backend ou Frontend Architecture

### "Preciso fazer deploy"
1. Docker Compose: [README-DOCKER.md](../README-DOCKER.md)
2. Detalhes técnicos: [docker-compose.md](developer-guide/deployment/docker-compose.md)
3. Outras opções: [deployment.md](operations/deployment.md)

## 📝 Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| [README.md](../README.md) | Página inicial do projeto |
| [README-DOCKER.md](../README-DOCKER.md) | Guia completo do Docker 🐳 |
| [docker-compose.yml](../docker-compose.yml) | Configuração dos serviços |
| [.env.example](../.env.example) | Template de variáveis de ambiente |
| [start-docker.ps1](../start-docker.ps1) | Script de gerenciamento Docker |
| [package.json](../package.json) | Configuração do monorepo |

## 🔗 Links Externos

- **Repositório GitHub**: https://github.com/AndrehSatoru/andrehsatoru.com
- **Issues**: https://github.com/AndrehSatoru/andrehsatoru.com/issues
- **Swagger UI**: http://localhost:8000/docs (quando rodando)
- **Frontend**: http://localhost:3000 (quando rodando)

## 💡 Dicas de Navegação

- 🐳 **Emoji Docker** = Informações sobre Docker/Containers
- 📖 **Links azuis** = Documentação interna
- 🔗 **Links externos** = Recursos externos
- ⚠️ **Avisos** = Informações importantes
- 💡 **Dicas** = Sugestões e melhores práticas

---

**Última atualização**: 25 de novembro de 2025

Não encontrou o que procura? [Abra uma issue](https://github.com/AndrehSatoru/andrehsatoru.com/issues) 🙋‍♂️
