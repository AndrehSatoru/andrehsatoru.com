# Plataforma de Análise de Investimentos

Uma plataforma full-stack para análise de risco, otimização de portfólio e análise técnica de investimentos.

## 📚 Documentação

A documentação completa deste projeto está disponível no diretório [`docs/`](docs/).

- **[Página Inicial da Documentação](docs/README.md)**
- **[Guia do Usuário](docs/user-guide/getting-started.md)**
- **[Guia do Desenvolvedor](docs/developer-guide/setup/local-development.md)**
- **[Guia Docker](README-DOCKER.md)** 🐳

## 🚀 Quick Start

### Com Docker (Recomendado)

```powershell
# Build e iniciar todos os serviços (backend + frontend + redis)
.\start-docker.ps1 build
.\start-docker.ps1 start

# Acessar:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Desenvolvimento Manual

```powershell
# Instalar dependências
.\install_deps.ps1

# Rodar o servidor (backend + frontend)
.\run_server.ps1
```

📖 **[Guia completo do Docker](README-DOCKER.md)**
