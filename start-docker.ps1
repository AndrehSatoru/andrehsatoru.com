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
    Write-Host "[ERROR] Docker nao esta rodando. Por favor, inicie o Docker Desktop." -ForegroundColor Red
    exit 1
}

# Verificar se arquivo .env existe, senão usar .env.example
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "[WARN] Arquivo .env nao encontrado. Copiando .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "[OK] Arquivo .env criado. Edite-o se necessario." -ForegroundColor Green
    } else {
        Write-Host "[WARN] Nenhum arquivo .env ou .env.example encontrado." -ForegroundColor Yellow
    }
}

switch ($Action) {
    "build" {
        Write-Host "Construindo imagens Docker..." -ForegroundColor Yellow
        docker-compose build --no-cache
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Build concluido com sucesso!" -ForegroundColor Green
        }
    }
    
    "start" {
        Write-Host "Iniciando servicos..." -ForegroundColor Yellow
        docker-compose up -d
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "Servicos iniciados com sucesso!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Servicos disponiveis:" -ForegroundColor Cyan
            Write-Host "  - Frontend:  http://localhost:3000" -ForegroundColor White
            Write-Host "  - Backend:   http://localhost:8000" -ForegroundColor White
            Write-Host "  - API Docs:  http://localhost:8000/docs" -ForegroundColor White
            Write-Host "  - Redis:     localhost:6379" -ForegroundColor White
            Write-Host ""
            Write-Host "Comandos uteis:" -ForegroundColor Cyan
            Write-Host "  .\start-docker.ps1 logs     # Ver logs" -ForegroundColor Gray
            Write-Host "  .\start-docker.ps1 stop     # Parar servicos" -ForegroundColor Gray
            Write-Host "  .\start-docker.ps1 restart  # Reiniciar servicos" -ForegroundColor Gray
            Write-Host "  .\start-docker.ps1 down     # Parar e remover containers" -ForegroundColor Gray
        }
    }
    
    "stop" {
        Write-Host "Parando servicos..." -ForegroundColor Yellow
        docker-compose stop
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Servicos parados!" -ForegroundColor Green
        }
    }
    
    "restart" {
        Write-Host "Reiniciando servicos..." -ForegroundColor Yellow
        docker-compose restart
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Servicos reiniciados!" -ForegroundColor Green
        }
    }
    
    "logs" {
        Write-Host "Exibindo logs (Ctrl+C para sair)..." -ForegroundColor Yellow
        Write-Host ""
        docker-compose logs -f
    }
    
    "down" {
        Write-Host "Parando e removendo containers..." -ForegroundColor Yellow
        docker-compose down
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Containers removidos!" -ForegroundColor Green
        }
    }
    
    "status" {
        Write-Host "Status dos containers:" -ForegroundColor Yellow
        Write-Host ""
        docker-compose ps
    }
}

Write-Host ""
