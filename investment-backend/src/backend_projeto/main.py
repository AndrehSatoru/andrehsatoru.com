# main.py
# Ponto de entrada da aplicação FastAPI

import time
import logging
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import router
from .core.exceptions import (
    AppError,
    DataProviderError,
    InvalidTransactionFileError,
    DataValidationError,
)
from .utils.config import Config
from .utils.logging_setup import setup_logging
from .utils.rate_limiter import InMemoryRateLimiter, add_rate_limit_headers

# Inicializar logging
config = Config()
log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
setup_logging(level=log_level, log_format=config.LOG_FORMAT)

app = FastAPI(
    title="Investment Backend API",
    description="API para análise de risco, otimização de portfólio e análise técnica",
    version="1.0.0",
)

# Middleware de compressão gzip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiter (condicional)
if config.RATE_LIMIT_ENABLED:
    app.state.rate_limiter = InMemoryRateLimiter(
        max_requests=config.RATE_LIMIT_REQUESTS,
        window_seconds=config.RATE_LIMIT_WINDOW_SECONDS,
    )
    logging.info(f"Rate limiting habilitado: {config.RATE_LIMIT_REQUESTS} req/{config.RATE_LIMIT_WINDOW_SECONDS}s")
else:
    logging.info("Rate limiting desabilitado")

# CORS (condicional)
origins = [o.strip() for o in (config.CORS_ORIGINS or '').split(',') if o.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logging.info(f"CORS habilitado para: {origins}")
else:
    logging.info("CORS desabilitado (nenhuma origem configurada)")

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

app.include_router(router)

# Se desejar, adicione lógica de inicialização aqui


# Exception Handlers padronizados
@app.exception_handler(DataProviderError)
async def data_provider_exception_handler(request: Request, exc: DataProviderError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"path": str(request.url.path), **exc.to_dict()},
    )


@app.exception_handler(InvalidTransactionFileError)
async def invalid_transaction_file_handler(request: Request, exc: InvalidTransactionFileError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"path": str(request.url.path), **exc.to_dict()},
    )


@app.exception_handler(DataValidationError)
async def data_validation_error_handler(request: Request, exc: DataValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"path": str(request.url.path), **exc.to_dict()},
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"path": str(request.url.path), **exc.to_dict()},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    # ValueError -> 422 para inputs inválidos
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": str(exc),
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
            "error": "InternalServerError",
            "message": "Ocorreu um erro inesperado.",
            "path": str(request.url.path),
        },
    )
