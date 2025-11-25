# Plataforma de Análise de Investimentos

Uma plataforma full-stack para análise de risco, otimização de portfólio e análise técnica de investimentos.

## ✨ Novidade: Rendimento do CDI no Caixa

🎉 **Versão 1.3.0** - Agora o caixa não investido rende CDI automaticamente!

- 💰 **Dados Reais**: Integração com Banco Central do Brasil
- 📈 **Rendimento Diário**: Juros compostos aplicados dia-a-dia
- 🎯 **Realismo**: Portfólio reflete melhor a realidade do mercado
- 📊 **Exemplo**: R$ 90.000 em caixa por 1 ano = +R$ 12.285 de rendimento (CDI ~13,65% a.a.)

[📖 Saiba mais sobre a integração CDI](docs/developer-guide/architecture/cdi-integration.md)

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
