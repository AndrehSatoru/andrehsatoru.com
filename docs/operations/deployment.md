# Guia de Implantação - API de Análise de Investimentos

## Visão Geral

Este guia cobre diferentes métodos de implantação da plataforma:

1. **[Docker Compose](#docker-compose-recomendado)** - Recomendado para desenvolvimento e produção
2. **[Implantação Local](#implantação-local)** - Execução manual dos serviços
3. **[Implantação em Cloud](#implantação-em-cloud)** - Deploy em provedores cloud

---

## Docker Compose (Recomendado)

### Pré-requisitos

- Docker Desktop instalado e rodando
- Docker Compose (incluído no Docker Desktop)
- 4GB+ de RAM disponível
- Portas 3000, 8000 e 6379 livres

### Início Rápido

```powershell
# Clone o repositório
git clone https://github.com/AndrehSatoru/andrehsatoru.com.git
cd andrehsatoru.com

# Configure variáveis de ambiente (opcional)
cp .env.example .env

# Build e inicie todos os serviços
.\start-docker.ps1 build
.\start-docker.ps1 start
```

### Serviços Incluídos

- **Backend (FastAPI):** Porta 8000, 4 workers
- **Frontend (Next.js):** Porta 3000
- **Redis:** Porta 6379, cache persistente

### Comandos Disponíveis

```powershell
.\start-docker.ps1 start     # Iniciar serviços
.\start-docker.ps1 stop      # Parar serviços
.\start-docker.ps1 restart   # Reiniciar serviços
.\start-docker.ps1 logs      # Ver logs em tempo real
.\start-docker.ps1 down      # Parar e remover containers
.\start-docker.ps1 status    # Ver status dos containers
```

### Verificação

```powershell
# Verificar status dos containers
.\start-docker.ps1 status

# Testar endpoints
curl http://localhost:8000/status
curl http://localhost:3000
```

📖 **Documentação Docker:**
- **[Guia do Usuário](../../README-DOCKER.md)** - Guia completo para usuários
- **[Guia Técnico](../developer-guide/deployment/docker-compose.md)** - Detalhes técnicos e troubleshooting avançado

---

## Implantação Local

### Pré-requisitos

- Python 3.9+
- Node.js 18+
- pnpm
- (Opcional) Redis para cache

### 1. Instalar Dependências

```bash
cd investment-backend
pip install -r requirements.txt
```

### 2. Configurar Ambiente

```bash
cp .env.example .env
# Edite o .env conforme necessário
```

### 3. Iniciar Servidor

```bash
cd src/backend_projeto
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verificar

```bash
curl http://localhost:8000/api/v1/system/status
# Resposta: {"status": "ok"}
```

### 5. Acessar Documentação

- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Implantação com Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY src/ ./src/

# Expor porta
EXPOSE 8000

# Variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV ENABLE_CACHE=true

# Comando de inicialização
CMD ["uvicorn", "src.backend_projeto.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENABLE_CACHE=true
      - LOG_LEVEL=INFO
      - LOG_FORMAT=json
      - MAX_ASSETS_PER_REQUEST=100
    volumes:
      - ./src/backend_projeto/cache:/app/src/backend_projeto/cache
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/system/status"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 3s
      retries: 3
```

### Build e Execução

```bash
docker-compose up -d
docker-compose logs -f api
```

---

## Implantação em Produção

### 1. Servidor Linux (Ubuntu/Debian)

#### Instalar Python e Dependências

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip nginx
```

#### Criar Usuário de Serviço

```bash
sudo useradd -m -s /bin/bash investment-api
sudo su - investment-api
```

#### Clonar e Configurar

```bash
cd /opt
git clone <repo-url> investment-backend
cd investment-backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Configurar .env

```bash
cp .env.example .env
nano .env
```

**Configuração de produção**:
```bash
ENABLE_CACHE=true
CACHE_TTL_SECONDS=3600
LOG_LEVEL=WARNING
LOG_FORMAT=json
RATE_LIMIT_ENABLED=true
MAX_ASSETS_PER_REQUEST=50
YFINANCE_MAX_RETRIES=5
```

#### Criar Serviço Systemd

```bash
sudo nano /etc/systemd/system/investment-api.service
```

```ini
[Unit]
Description=API de Análise de Investimentos
After=network.target

[Service]
Type=notify
User=investment-api
Group=investment-api
WorkingDirectory=/opt/investment-backend/src/backend_projeto
Environment="PATH=/opt/investment-backend/venv/bin"
ExecStart=/opt/investment-backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Iniciar Serviço

```bash
sudo systemctl daemon-reload
sudo systemctl enable investment-api
sudo systemctl start investment-api
sudo systemctl status investment-api
```

---

### 2. Nginx como Proxy Reverso

#### Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/investment-api
```

```nginx
server {
    listen 80;
    server_name api.seudominio.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;
        
        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # Gzip (já feito pelo FastAPI, mas pode duplicar)
        gzip on;
        gzip_types application/json;
    }
}
```

#### Ativar Site

```bash
sudo ln -s /etc/nginx/sites-available/investment-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### 3. SSL com Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.seudominio.com
```

---

## Implantação em Nuvem

### AWS (Elastic Beanstalk)

1.  **Instalar EB CLI**:
    ```bash
    pip install awsebcli
    ```

2.  **Inicializar**:
    ```bash
    eb init -p python-3.11 investment-api
    ```

3.  **Criar ambiente**:
    ```bash
    eb create investment-api-prod
    ```

4.  **Implantar**:
    ```bash
    eb deploy
    ```

5.  **Configurar variáveis de ambiente**:
    ```bash
    eb setenv ENABLE_CACHE=true LOG_FORMAT=json
    ```

---

### Google Cloud (Cloud Run)

1.  **Criar Dockerfile** (ver seção Docker acima)

2.  **Build e Push**:
    ```bash
    gcloud builds submit --tag gcr.io/PROJECT_ID/investment-api
    ```

3.  **Implantar**:
    ```bash
    gcloud run deploy investment-api \
     --image gcr.io/PROJECT_ID/investment-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars ENABLE_CACHE=true,LOG_FORMAT=json
    ```

---

### Heroku

1.  **Criar Procfile**:
    ```
    web: uvicorn src.backend_projeto.main:app --host 0.0.0.0 --port $PORT
    ```

2.  **Implantar**:
    ```bash
    heroku create investment-api
    git push heroku main
    ```

3.  **Configurar variáveis de ambiente**:
    ```bash
    heroku config:set ENABLE_CACHE=true
    heroku config:set LOG_FORMAT=json
    ```

---

## Monitoramento

### Verificações de Saúde (Health Checks)

```bash
# Simples
curl http://api.seudominio.com/api/v1/system/status

# Com timeout
curl --max-time 5 http://api.seudominio.com/api/v1/system/status
```

### Logs

```bash
# Systemd
sudo journalctl -u investment-api -f

# Docker
docker-compose logs -f api

# Heroku
heroku logs --tail
```

### Métricas

**Prometheus** (futuro):
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'investment-api'
    static_configs:
      - targets: ['localhost:8000']
```

---

## Backup e Recuperação

### Cache

```bash
# Backup
tar -czf cache-backup-$(date +%Y%m%d).tar.gz src/backend_projeto/cache/

# Restaurar
tar -xzf cache-backup-20251009.tar.gz
```

### Configurações

```bash
# Backup
cp .env .env.backup-$(date +%Y%m%d)

# Restaurar
cp .env.backup-20251009 .env
```

---

## Solução de Problemas

### Servidor não inicia

1.  **Verifique os logs**:
    ```bash
    sudo journalctl -u investment-api -n 50
    ```

2.  **Teste manualmente**:
    ```bash
    cd /opt/investment-backend/src/backend_projeto
    source ../../venv/bin/activate
    uvicorn main:app --host 127.0.0.1 --port 8000
    ```

### Erros 503 frequentes

- **Causa**: YFinance indisponível ou com rate limit
- **Solução**: Aumentar `YFINANCE_MAX_RETRIES` e `YFINANCE_BACKOFF_FACTOR`

### Alto uso de memória

- **Causa**: Cache muito grande ou muitas requisições simultâneas
- **Solução**:
    - Reduzir `CACHE_TTL_SECONDS`
    - Limitar workers do Uvicorn
    - Adicionar Redis para cache externo

### Timeouts

- **Causa**: Requisições com muitos ativos ou períodos longos
- **Solução**:
    - Aumentar `REQUEST_TIMEOUT_SECONDS`
    - Reduzir `MAX_ASSETS_PER_REQUEST`
    - Otimizar queries

---

## Checklist de Produção

- [ ] `.env` configurado corretamente
- [ ] Segredos não commitados no Git
- [ ] SSL/TLS habilitado
- [ ] Firewall configurado (apenas portas necessárias)
- [ ] Logs centralizados (ELK, Datadog, etc.)
- [ ] Monitoramento (uptime, latência, erros)
- [ ] Backups automáticos
- [ ] Documentação atualizada
- [ ] Testes passando (`pytest -q`)
- [ ] Health checks configurados
- [ ] Rate limiting habilitado
- [ ] CORS configurado (se necessário)

---

## Segurança

### Recomendações

1.  **Não exponha diretamente**: Use Nginx/Cloudflare como proxy
2.  **Rate limiting**: Habilite em produção
3.  **Validações**: Já implementadas (ativos, pesos, etc.)
4.  **Logs**: Não logue dados sensíveis
5.  **HTTPS**: Obrigatório em produção
6.  **Firewall**: Apenas portas 80/443 abertas
7.  **Atualizações**: Mantenha as dependências atualizadas

### Sanitização

Já implementado:
- ✅ Limite de 100 ativos por requisição
- ✅ Validação de tipos via Pydantic
- ✅ Tratamento de exceções

---

## Ajuste de Performance

### Uvicorn Workers

```bash
# Desenvolvimento
uvicorn main:app --reload

# Produção (4 workers)
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000

# Produção (auto workers = núcleos de CPU)
uvicorn main:app --workers $(nproc) --host 0.0.0.0 --port 8000
```

### Gunicorn + Uvicorn

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile -
```

---

## Suporte

- **Documentação**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Email**: suporte@seudominio.com

---

**Última atualização**: 2025-10-09
