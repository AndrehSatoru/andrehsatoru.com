"""
This module defines custom exception classes for the Investment Backend application.

These exceptions provide a structured way to handle and propagate errors
throughout the application, allowing for standardized error responses
in the API. It also includes a Pydantic model for consistent API error formatting.
"""
# core/exceptions.py
# Define exceções customizadas para o backend

from typing import Optional, Any, Dict
from pydantic import BaseModel # Import BaseModel


class AppError(Exception):
    """Erro base da aplicação para padronização."""

    def __init__(self, message: str, *, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code: str = code or self.__class__.__name__
        self.details: Dict[str, Any] = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.code,
            "message": str(self),
            "details": self.details,
        }


class DataProviderError(AppError):
    """Erros ao contatar provedores externos de dados (yfinance, BCB, etc)."""
    def __init__(self, message: str, *, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code=code, details=details)


class InvalidTransactionFileError(AppError):
    """
    Exception raised for errors related to invalid transaction files.

    This includes issues like incorrect file format, missing required columns,
    or the file not existing.
    """


class DataValidationError(AppError):
    """
    Exception raised for errors during data validation.

    This occurs when loaded or received data does not conform to expected
    formats, types, or business rules.
    """

class ApiErrorResponse(BaseModel):
    """
    Pydantic model for standardized API error responses.

    Attributes:
        error (str): A machine-readable error code (e.g., "invalid_request", "data_provider_error").
        message (str): A human-readable message describing the error.
        status_code (int): The HTTP status code associated with the error.
        details (Optional[Dict]): Optional dictionary for additional error details.
        request_id (str): A unique identifier for the request, useful for tracing.
    """
    error: str  # "invalid_request", "data_provider_error", etc
    message: str  # Mensagem legível
    status_code: int
    details: Optional[Dict] = None  # Info adicional
    request_id: str  # Para rastreamento