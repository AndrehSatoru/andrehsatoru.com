# core/exceptions.py
# Define exceções customizadas para o backend

from typing import Optional, Any, Dict


class AppError(Exception):
    """Erro base da aplicação para padronização."""

    def __init__(self, message: str, *, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code or self.__class__.__name__
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.code,
            "message": str(self),
            "details": self.details,
        }


class DataProviderError(AppError):
    """Erros ao contatar provedores externos de dados (yfinance, BCB, etc)."""


class InvalidTransactionFileError(AppError):
    """Erros relacionados ao arquivo de transações (formato, ausência de colunas, inexistente, etc)."""


class DataValidationError(AppError):
    """Erros de validação de dados carregados/recebidos."""
