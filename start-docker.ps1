# Script para iniciar o ambiente Docker
# Uso: .\start-docker.ps1 [build|start|stop|restart|logs|down]

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "start", "stop", "restart", "logs", "down", "status")]
    [string]$Action = "start"
)

$ErrorActionPreference = "Stop"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Portfolio Analysis - Docker Manager" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se Docker está rodando
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker não está rodando. Por favor, inicie o Docker Desktop." -ForegroundColor Red
    exit 1
}

# Verificar se arquivo .env existe, senão usar .env.example
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "⚠️  Arquivo .env não encontrado. Copiando .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Arquivo .env criado. Edite-o se necessário." -ForegroundColor Green
    } else {
        Write-Host "⚠️  Nenhum arquivo .env ou .env.example encontrado." -ForegroundColor Yellow
    }
}

switch ($Action) {
    "build" {
        Write-Host "🔨 Construindo imagens Docker..." -ForegroundColor Yellow
        docker-compose build --no-cache
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Build concluído com sucesso!" -ForegroundColor Green
        }
    }
    
    "start" {
        Write-Host "🚀 Iniciando serviços..." -ForegroundColor Yellow
        docker-compose up -d
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Serviços iniciados com sucesso!" -ForegroundColor Green
            Write-Host ""
            Write-Host "📊 Serviços disponíveis:" -ForegroundColor Cyan
            Write-Host "  • Frontend:  http://localhost:3000" -ForegroundColor White
            Write-Host "  • Backend:   http://localhost:8000" -ForegroundColor White
            Write-Host "  • API Docs:  http://localhost:8000/docs" -ForegroundColor White
            Write-Host "  • Redis:     localhost:6379" -ForegroundColor White
            Write-Host ""
            Write-Host "💡 Comandos úteis:" -ForegroundColor Cyan
            Write-Host "  .\start-docker.ps1 logs     # Ver logs" -ForegroundColor Gray
            Write-Host "  .\start-docker.ps1 stop     # Parar serviços" -ForegroundColor Gray
            Write-Host "  .\start-docker.ps1 restart  # Reiniciar serviços" -ForegroundColor Gray
            Write-Host "  .\start-docker.ps1 down     # Parar e remover containers" -ForegroundColor Gray
        }
    }
    
    "stop" {
        Write-Host "⏸️  Parando serviços..." -ForegroundColor Yellow
        docker-compose stop
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Serviços parados!" -ForegroundColor Green
        }
    }
    
    "restart" {
        Write-Host "🔄 Reiniciando serviços..." -ForegroundColor Yellow
        docker-compose restart
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Serviços reiniciados!" -ForegroundColor Green
        }
    }
    
    "logs" {
        Write-Host "📋 Exibindo logs (Ctrl+C para sair)..." -ForegroundColor Yellow
        Write-Host ""
        docker-compose logs -f
    }
    
    "down" {
        Write-Host "🗑️  Parando e removendo containers..." -ForegroundColor Yellow
        docker-compose down
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Containers removidos!" -ForegroundColor Green
        }
    }
    
    "status" {
        Write-Host "📊 Status dos containers:" -ForegroundColor Yellow
        Write-Host ""
        docker-compose ps
    }
}

Write-Host ""
