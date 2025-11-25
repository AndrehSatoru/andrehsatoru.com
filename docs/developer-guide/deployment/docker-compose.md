# Deploy com Docker Compose

Este documento fornece informações técnicas sobre o deploy da aplicação usando Docker Compose, incluindo todas as melhorias e correções implementadas.

## 📋 Visão Geral

O Docker Compose orquestra três serviços principais:

1. **Redis 7** - Cache persistente com volume dedicado
2. **Backend (Python 3.11)** - API FastAPI com 4 workers Uvicorn
3. **Frontend (Node 20)** - Aplicação Next.js com build otimizado

## ✨ Melhorias Implementadas (Nov 2025)

### 🔧 Correções Técnicas
- ✅ **Networking interno** com comunicação entre containers via DNS
- ✅ **Variáveis de ambiente** separadas para server-side e client-side
- ✅ **Health checks** implementados para todos os serviços
- ✅ **Port mapping** corrigido para evitar conflitos
- ✅ **Monorepo support** com shared-types funcionando corretamente

### 📊 Integração Backend-Frontend
- ✅ **API Routes** do Next.js comunicando corretamente com backend
- ✅ **CORS** configurado para permitir requests internos
- ✅ **Zodios client** integrado com tipos do backend
- ✅ **Error handling** melhorado com logs detalhados

## 🚀 Quick Start

```powershell
# Na raiz do projeto
.\start-docker.ps1 build    # Build de todos os serviços
.\start-docker.ps1 start    # Inicia os containers
.\start-docker.ps1 status   # Verifica status
```

## 📦 Arquitetura

```
┌─────────────────────────────────────────┐
│         Docker Compose                   │
├─────────────────────────────────────────┤
│                                          │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   Frontend   │───▶│   Backend    │  │
│  │  (Next.js)   │    │  (FastAPI)   │  │
│  │   Port 3000  │    │  Port 8000   │  │
│  └──────────────┘    └───────┬──────┘  │
│                              │          │
│                       ┌──────▼──────┐   │
│                       │    Redis    │   │
│                       │  Port 6379  │   │
│                       └─────────────┘   │
│                                          │
└─────────────────────────────────────────┘
```

## 🔧 Configuração

### Arquivo docker-compose.yml

Localizado na raiz do projeto, define:

- **Serviços**: Redis, Backend, Frontend
- **Redes**: `app-network` para comunicação interna
- **Volumes**: Persistência de dados do Redis e cache do backend
- **Health Checks**: Monitoramento da saúde dos serviços
- **Dependencies**: Ordem correta de inicialização

### Variáveis de Ambiente

Configure no arquivo `.env` na raiz:

```env
# Backend
ENABLE_CACHE=true
LOG_LEVEL=INFO
MAX_ASSETS_PER_REQUEST=100
CACHE_TTL_SECONDS=3600

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Frontend
NODE_ENV=production
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🛠️ Comandos

### Script PowerShell (Recomendado)

```powershell
# Build das imagens
.\start-docker.ps1 build

# Iniciar serviços
.\start-docker.ps1 start

# Parar serviços
.\start-docker.ps1 stop

# Reiniciar serviços
.\start-docker.ps1 restart

# Ver logs
.\start-docker.ps1 logs

# Remover containers
.\start-docker.ps1 down

# Ver status
.\start-docker.ps1 status
```

### Comandos Docker Compose Diretos

```powershell
# Build
docker-compose build --no-cache

# Iniciar
docker-compose up -d

# Parar
docker-compose stop

# Ver logs
docker-compose logs -f

# Remover
docker-compose down

# Remover com volumes
docker-compose down -v
```

## 📊 Monitoramento

### Health Checks

Cada serviço possui health check configurado:

```powershell
# Ver status de saúde
docker ps

# Verificar manualmente
curl http://localhost:8000/status
curl http://localhost:3000
```

### Logs

```powershell
# Todos os serviços
.\start-docker.ps1 logs

# Serviço específico
docker-compose logs backend
docker-compose logs frontend
docker-compose logs redis

# Com timestamps
docker-compose logs --timestamps
```

### Recursos

```powershell
# Uso de CPU e memória
docker stats

# Informações detalhadas
docker inspect portfolio_backend
```

## 🔍 Troubleshooting

### Container não inicia

```powershell
# Ver logs detalhados
docker-compose logs backend

# Verificar configuração
docker-compose config

# Rebuild
docker-compose build --no-cache backend
docker-compose up -d
```

### Porta em uso

Edite `docker-compose.yml` para usar porta diferente:

```yaml
ports:
  - "3001:3000"  # Muda porta do host
```

### Problemas de rede

```powershell
# Recriar rede
docker-compose down
docker network prune
docker-compose up -d
```

### Limpeza completa

```powershell
# Parar tudo
docker-compose down

# Remover volumes
docker-compose down -v

# Remover imagens
docker rmi portfolio_backend portfolio_frontend

# Rebuild completo
.\start-docker.ps1 build
```

## 🔒 Segurança

### Produção

Para ambientes de produção, considere:

1. **Variáveis sensíveis**: Use secrets do Docker Swarm ou Kubernetes
2. **Rede**: Configure firewall e regras de rede adequadas
3. **SSL/TLS**: Configure certificados e reverse proxy (Nginx/Traefik)
4. **Recursos**: Limite CPU e memória nos containers
5. **Logs**: Configure logging driver apropriado

Exemplo com limites:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 🌐 Deploy em Produção

### Com Docker Swarm

```powershell
# Inicializar swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml portfolio

# Ver serviços
docker service ls

# Escalar
docker service scale portfolio_backend=3
```

### Com Kubernetes

Para Kubernetes, converta o compose:

```powershell
# Instalar kompose
# https://kompose.io/

# Converter
kompose convert -f docker-compose.yml
```

## 🐛 Troubleshooting Resolvido

### Problemas Comuns e Soluções Implementadas

#### 1. Toast() Error no Servidor
**Problema**: `Attempted to call toast() from the server`
**Causa**: Interceptor axios tentando chamar função client-side no servidor
**Solução**: Removido toast dos interceptors, implementado no client-side apenas

#### 2. Network Error - localhost:8000
**Problema**: Frontend não consegue conectar ao backend
**Causa**: `localhost` dentro do container aponta para o próprio container
**Solução**: 
- Adicionado `INTERNAL_API_URL=http://portfolio_backend:8000`
- Frontend detecta se está no servidor ou cliente
- Server-side usa URL interna Docker, client-side usa localhost

#### 3. Zodios Response Error
**Problema**: `init["status"] must be in the range of 200 to 599`
**Causa**: Zodios retorna dados diretamente, não objeto axios completo
**Solução**: API route ajustada para retornar `resp` diretamente, não `resp.data`

#### 4. DataFrame Columns Error
**Problema**: `O DataFrame deve conter as colunas: ['Data', 'Ativo', 'Quantidade', 'Preco']`
**Causa**: Mapeamento incorreto de colunas do frontend para backend
**Solução**: 
- Implementada busca de cotações históricas via YFinance
- Cálculo automático: `Quantidade = Valor / Preço`
- Mapeamento correto das colunas

#### 5. Port Conflicts
**Problema**: Redis porta 6379 em uso
**Solução**: Alterada para porta 6380 externa, 6379 interna

### Debug de Operações

```powershell
# Ver logs com cálculos de quantidade
docker logs portfolio_backend --tail 50 --follow

# Exemplo de log esperado:
# INFO: Operação VALE3 em 2019-10-10: valor=10000, preço=50.25, quantidade=199.00
```

### Verificar Comunicação Interna

```powershell
# Backend para Redis
docker exec portfolio_backend ping portfolio_redis

# Frontend para Backend
docker exec portfolio_frontend curl http://portfolio_backend:8000/api/v1/status
```

## 📚 Recursos Adicionais

- [Documentação Docker Compose](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [README-DOCKER.md](../../../README-DOCKER.md) - Guia completo do usuário
- [Endpoint: Processar Operações](../api/processar-operacoes.md) - Documentação da API

## 🔄 Atualizações

### Após mudanças no código

```powershell
# Rebuild serviço específico
docker-compose build backend
docker-compose up -d backend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# Ou rebuild tudo
.\start-docker.ps1 build
.\start-docker.ps1 restart
```

### Atualizar imagens base

```powershell
# Pull novas imagens base
docker-compose pull

# Rebuild com novas bases
docker-compose build --pull

# Rebuild
.\start-docker.ps1 build
```

## 💡 Dicas

1. **Use cache**: O Docker faz cache das camadas, rebuild é rápido
2. **Volumes nomeados**: Melhor para persistência de dados
3. **Health checks**: Essenciais para orquestração adequada
4. **Logs estruturados**: Configure JSON logging para melhor análise
5. **Backup**: Faça backup regular dos volumes do Redis
6. **Variáveis de ambiente**: Separe URLs internas (Docker) de externas (localhost)
7. **Network interno**: Use nomes de serviço (portfolio_backend) para comunicação entre containers

## 📝 Changelog

### v1.1.0 (Nov 2025)
- ✅ Integração completa Docker Compose (backend + frontend + redis)
- ✅ Busca automática de cotações históricas via YFinance
- ✅ Cálculo correto de quantidade de ações baseado em preços reais
- ✅ Networking interno otimizado com DNS Docker
- ✅ Correção de bugs críticos (Toast, Zodios, DataFrame columns)
- ✅ Health checks implementados em todos os serviços
- ✅ Documentação completa atualizada

---

**Nota**: Para informações mais detalhadas sobre uso do Docker, consulte o [README-DOCKER.md](../../../README-DOCKER.md) na raiz do projeto.
