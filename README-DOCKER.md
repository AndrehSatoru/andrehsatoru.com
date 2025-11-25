# 🐳 Docker - Guia de Uso

Este documento explica como executar o projeto completo (backend + frontend) usando Docker Compose.

## 📋 Pré-requisitos

- **Docker Desktop** instalado e rodando
- **Docker Compose** (incluído no Docker Desktop)
- Pelo menos **4GB de RAM** disponível
- Portas **3000**, **8000** e **6379** livres

## 🚀 Início Rápido

### 1. Primeira execução (build das imagens)

```powershell
# Build e start dos serviços
.\start-docker.ps1 build
.\start-docker.ps1 start
```

### 2. Execuções subsequentes

```powershell
# Apenas iniciar os serviços
.\start-docker.ps1 start
```

### 3. Acessar a aplicação

Após iniciar, os serviços estarão disponíveis em:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Redis**: localhost:6379

## 📦 Serviços Incluídos

### 🎨 Frontend (Next.js)
- Porta: **3000**
- Container: `portfolio_frontend`
- Build otimizado para produção

### ⚙️ Backend (FastAPI)
- Porta: **8000**
- Container: `portfolio_backend`
- Workers: 4
- Health check habilitado

### 🗄️ Redis (Cache)
- Porta: **6379**
- Container: `portfolio_redis`
- Volume persistente para dados

## 🛠️ Comandos Disponíveis

O script `start-docker.ps1` oferece os seguintes comandos:

```powershell
# Construir imagens (necessário apenas na primeira vez ou após mudanças)
.\start-docker.ps1 build

# Iniciar todos os serviços
.\start-docker.ps1 start

# Parar serviços (sem remover containers)
.\start-docker.ps1 stop

# Reiniciar serviços
.\start-docker.ps1 restart

# Ver logs em tempo real (Ctrl+C para sair)
.\start-docker.ps1 logs

# Parar e remover containers
.\start-docker.ps1 down

# Ver status dos containers
.\start-docker.ps1 status
```

## 🔧 Configuração

### Variáveis de Ambiente

As variáveis de ambiente podem ser configuradas no arquivo `.env` na raiz do projeto:

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

Um arquivo `.env.example` está disponível como referência.

## 📊 Volumes Persistentes

Os seguintes diretórios são mapeados para persistir dados:

- `./packages/backend/src/backend_projeto/cache` → Cache do backend
- `./packages/backend/src/backend_projeto/outputs` → Outputs de análises
- `redis_data` → Dados do Redis

## 🔍 Troubleshooting

### Container não inicia

```powershell
# Ver logs detalhados
.\start-docker.ps1 logs

# Verificar status
.\start-docker.ps1 status
```

### Porta já em uso

Se alguma porta estiver em uso, você pode:

1. Parar o serviço que está usando a porta
2. Ou modificar a porta no `docker-compose.yml`:

```yaml
ports:
  - "3001:3000"  # Mudar 3000 para 3001 no host
```

### Rebuild completo (limpar cache)

```powershell
# Parar e remover tudo
.\start-docker.ps1 down

# Remover volumes (CUIDADO: apaga dados do Redis)
docker-compose down -v

# Rebuild do zero
.\start-docker.ps1 build
.\start-docker.ps1 start
```

### Problemas com memória

Se encontrar erros de memória:

1. Abra Docker Desktop
2. Settings → Resources
3. Aumente a memória disponível para pelo menos 4GB

## 🐛 Debug

### Acessar shell de um container

```powershell
# Backend
docker exec -it portfolio_backend sh

# Frontend
docker exec -it portfolio_frontend sh

# Redis
docker exec -it portfolio_redis redis-cli
```

### Ver logs de um serviço específico

```powershell
docker-compose logs backend
docker-compose logs frontend
docker-compose logs redis
```

### Ver logs com timestamp

```powershell
docker-compose logs -f --timestamps
```

## 🔄 Atualizar após mudanças no código

Após fazer alterações no código:

```powershell
# Rebuild apenas do serviço alterado
docker-compose build backend  # ou frontend
docker-compose up -d

# Ou rebuild completo
.\start-docker.ps1 build
.\start-docker.ps1 restart
```

## 🌐 Acesso via Rede

Para acessar de outros dispositivos na mesma rede:

1. Descubra seu IP local:
   ```powershell
   ipconfig
   ```

2. Acesse de outro dispositivo:
   - Frontend: `http://SEU_IP:3000`
   - Backend: `http://SEU_IP:8000`

3. Ajuste o CORS no backend se necessário (variável `ALLOWED_ORIGINS`)

## 📈 Monitoramento

### Health Checks

Os serviços possuem health checks configurados:

```powershell
# Ver status de saúde
docker ps

# Testar manualmente
curl http://localhost:8000/status
```

### Recursos utilizados

```powershell
# Ver uso de CPU/Memória
docker stats
```

## 🛑 Parar e Limpar

### Parar serviços mantendo dados

```powershell
.\start-docker.ps1 stop
```

### Remover containers (mantém volumes)

```powershell
.\start-docker.ps1 down
```

### Limpar tudo (incluindo volumes)

```powershell
docker-compose down -v
docker system prune -a
```

## 📝 Notas Importantes

- ⚠️ **Primeira execução** pode demorar 5-10 minutos para build das imagens
- 💾 **Dados do Redis** são persistidos em volume Docker
- 🔄 **Mudanças no código** requerem rebuild da imagem
- 🌐 **Comunicação interna** entre containers usa nomes de serviços (backend, redis)
- 🔒 Em produção, configure variáveis sensíveis adequadamente
- 📊 **Análise de Portfolio** busca automaticamente preços históricos via YFinance
- 🧮 **Quantidade de ações** calculada automaticamente: Quantidade = Valor / Preço

## ✨ Novidades (v1.1.0 - Nov 2025)

### Integração de Preços Históricos
O endpoint `/api/v1/transactions/processar-operacoes` agora:
- Busca automaticamente preços históricos das ações via YFinance
- Calcula a quantidade exata de ações compradas: `Quantidade = Valor / Preço`
- Tenta buscar preços em uma janela de ±5 dias caso a data exata não tenha dados
- Exibe logs detalhados dos cálculos realizados

### Melhorias no Docker
- Networking interno otimizado (INTERNAL_API_URL)
- Correção de bugs críticos (Toast, Zodios, DataFrame columns)
- Health checks implementados em todos os serviços
- Documentação completa atualizada

### Ver Cálculos em Tempo Real
```powershell
docker logs portfolio_backend --tail 50 --follow
```

Exemplo de log:
```
INFO: Operação VALE3 em 2019-10-10: valor=10000.00, preço=50.25, quantidade=199.00
```

## 🆘 Ajuda

Se encontrar problemas:

1. Verifique os logs: `.\start-docker.ps1 logs`
2. Confirme que Docker Desktop está rodando
3. Verifique se as portas estão livres
4. Tente um rebuild limpo: `.\start-docker.ps1 down` → `.\start-docker.ps1 build`
5. Consulte troubleshooting completo: [docs/developer-guide/deployment/docker-compose.md](docs/developer-guide/deployment/docker-compose.md)

---

**Última atualização**: 25 de novembro de 2025
