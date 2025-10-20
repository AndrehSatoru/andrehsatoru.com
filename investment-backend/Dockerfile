# Multi-stage build para otimizar tamanho da imagem
FROM python:3.11-slim as builder

WORKDIR /build

# Instalar dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar apenas requirements primeiro (cache layer)
COPY requirements.txt .

# Instalar dependências em /build/venv
RUN python -m venv /build/venv
ENV PATH="/build/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ===== Stage 2: Runtime =====
FROM python:3.11-slim

WORKDIR /app

# Copiar venv do builder
COPY --from=builder /build/venv /app/venv

# Copiar código da aplicação
COPY src/ ./src/

# Criar diretórios necessários
RUN mkdir -p src/backend_projeto/cache && \
    mkdir -p src/backend_projeto/outputs && \
    mkdir -p src/backend_projeto/inputs

# Criar usuário não-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Variáveis de ambiente
ENV PATH="/app/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO \
    ENABLE_CACHE=true

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD ["python","-c","import os, urllib.request; urllib.request.urlopen('http://localhost:%s/status' % os.environ.get('PORT','8000'))"]

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["sh","-c","uvicorn src.backend_projeto.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4"]
