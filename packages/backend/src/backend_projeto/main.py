"""
Main entry point for the Investment Backend FastAPI application.

This module initializes the FastAPI app, configures middleware (CORS, GZip, Rate Limiting),
sets up logging, includes all API routers, and defines custom exception handlers
for a robust and well-structured API.
"""
# main.py
# Ponto de entrada da aplicação FastAPI

import time
import logging
from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .api import (
    system_endpoints,
    data_endpoints,
    technical_analysis_endpoints,
    risk_endpoints,
    optimization_endpoints,
    visualization_endpoints,
    factor_endpoints,
    portfolio_endpoints,
    portfolio_simulation_endpoints,
    dashboard_endpoints,
    advanced_endpoints,
    analysis_endpoints,
    transaction_endpoints,
    auth_endpoints # New import
)
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from .application.auth import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_username(token: Annotated[str, Depends(oauth2_scheme)]) -> str:
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username

# Inicializar logging
from .infrastructure.utils.config import settings as config
from .infrastructure.utils.logging_setup import setup_logging
log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
setup_logging(level=log_level, log_format=config.LOG_FORMAT)

app = FastAPI(
    title="Investment Backend API",
    description="API para análise de risco, otimização de portfólio e análise técnica",
    version="1.0.0",
)

# CORS (condicional)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.info(f"CORS habilitado para: {origins}")

# Middleware de compressão gzip
app.add_middleware(GZipMiddleware, minimum_size=config.GZIP_MINIMUM_SIZE)

# Rate limiter (condicional)
from .infrastructure.utils.rate_limiter import InMemoryRateLimiter, add_rate_limit_headers
if config.RATE_LIMIT_ENABLED:
    app.state.rate_limiter = InMemoryRateLimiter(
        max_requests=config.RATE_LIMIT_REQUESTS,
        window_seconds=config.RATE_LIMIT_WINDOW_SECONDS,
    )
    logging.info(f"Rate limiting habilitado: {config.RATE_LIMIT_REQUESTS} req/{config.RATE_LIMIT_WINDOW_SECONDS}s")
else:
    logging.info("Rate limiting desabilitado")

# Middleware para logging e métricas
@app.middleware("http")
async def log_and_metrics_middleware(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", f"req-{int(time.time()*1000)}")
    
    # Rate limiting (se habilitado)
    if config.RATE_LIMIT_ENABLED:
        try:
            await app.state.rate_limiter(request)
        except HTTPException as e:
            # Rate limit excedido - retornar erro imediatamente
            return JSONResponse(
                status_code=e.status_code,
                content=e.detail,
                headers=e.headers,
            )
    
    # Log da requisição
    logging.info(
        f"[{request_id}] --> {request.method} {request.url.path}",
        extra={"request_id": request_id}
    )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    # Adicionar headers de rate limit
    if config.RATE_LIMIT_ENABLED:
        response = add_rate_limit_headers(request, response)
    
    # Log da resposta
    log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
    logging.log(
        log_level,
        f"[{request_id}] <-- {request.method} {request.url.path} "
        f"status={response.status_code} time={process_time:.3f}s",
        extra={"request_id": request_id, "duration": int(process_time * 1000)}
    )
    
    return response

app.include_router(system_endpoints.router, prefix="/api/v1")
app.include_router(data_endpoints.router, prefix="/api/v1")
app.include_router(technical_analysis_endpoints.router, prefix="/api/v1")
app.include_router(risk_endpoints.router, prefix="/api/v1")
app.include_router(optimization_endpoints.router, prefix="/api/v1")
app.include_router(visualization_endpoints.router, prefix="/api/v1")
app.include_router(factor_endpoints.router, prefix="/api/v1")
app.include_router(portfolio_endpoints.router, prefix="/api/v1")
app.include_router(portfolio_simulation_endpoints.router, prefix="/api/v1")
app.include_router(dashboard_endpoints.router, prefix="/api/v1")
app.include_router(advanced_endpoints.router, prefix="/api/v1")
app.include_router(analysis_endpoints.router, prefix="/api/v1")
app.include_router(transaction_endpoints.router, prefix="/api/v1")
app.include_router(auth_endpoints.router, prefix="/api/v1")

# Root endpoint
@app.get("/")
def root():
    return {"message": "Investment Backend API", "docs": "/docs", "status": "/api/v1/status"}

# Se desejar, adicione lógica de inicialização aqui


# Exception Handlers padronizados
from .domain.exceptions import ( # Moved this import here
    AppError,
    DataProviderError,
    InvalidTransactionFileError,
    DataValidationError,
)

@app.exception_handler(DataProviderError)
async def data_provider_exception_handler(request: Request, exc: DataProviderError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": f"Não foi possível obter dados externos: {str(exc)}"},
    )


@app.exception_handler(InvalidTransactionFileError)
async def invalid_transaction_file_handler(request: Request, exc: InvalidTransactionFileError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Arquivo de Transação Inválido",
            "message": f"O arquivo de transação fornecido é inválido: {str(exc)}",
            "suggestion": "Certifique-se de que o arquivo está no formato correto (e.g., Excel) e contém todas as colunas obrigatórias.",
            "details": exc.to_dict(),
            "path": str(request.url.path),
        },
    )


@app.exception_handler(DataValidationError)
async def data_validation_error_handler(request: Request, exc: DataValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Erro de Validação de Dados",
            "message": f"Os dados fornecidos não passaram na validação: {str(exc)}",
            "suggestion": "Verifique os valores e formatos dos dados enviados. Consulte a documentação da API para os requisitos de cada campo.",
            "details": exc.to_dict(),
            "path": str(request.url.path),
        },
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Erro na Aplicação",
            "message": f"Ocorreu um erro inesperado na aplicação: {str(exc)}",
            "suggestion": "Verifique os parâmetros da sua requisição e tente novamente. Se o problema persistir, contate o suporte técnico.",
            "details": exc.to_dict(),
            "path": str(request.url.path),
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    # ValueError -> 422 para inputs inválidos
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Erro de Valor Inválido",
            "message": f"Um valor inválido foi fornecido: {str(exc)}",
            "suggestion": "Verifique se todos os valores numéricos e strings estão dentro dos limites e formatos esperados.",
            "path": str(request.url.path),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Fallback para erros não tratados, retornando JSON padronizado
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Erro Interno do Servidor",
            "message": "Ocorreu um erro inesperado no servidor. Por favor, tente novamente mais tarde.",
            "suggestion": "Se o problema persistir, contate o suporte técnico e forneça o ID da requisição se disponível.",
            "path": str(request.url.path),
        },
    )
