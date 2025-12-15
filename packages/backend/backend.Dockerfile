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

# Variáveis de ambiente
ENV PATH="/app/venv/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO \
    ENABLE_CACHE=true

# Criar usuário não-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check (start_period maior para VMs lentas)
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/status')"

# Expor porta
EXPOSE 8000

# Comando de inicialização (1 worker para ambientes com poucos recursos)
CMD ["/app/venv/bin/python", "-m", "uvicorn", "src.backend_projeto.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
