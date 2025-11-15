# utils/sanitization.py
# Utilitários para sanitização e validação de inputs

import re
from typing import List, Optional


def sanitize_ticker(ticker: str) -> str:
    """Sanitiza ticker removendo caracteres inválidos.
    
    Permite: A-Z, a-z, 0-9, ponto, hífen, circunflexo, underline.
    Remove espaços e outros caracteres.
    """
    if not ticker:
        raise ValueError("Ticker não pode ser vazio")
    
    # Remove espaços
    ticker = ticker.strip()
    
    # Permite apenas caracteres válidos para tickers
    pattern = r'^[A-Za-z0-9.\-^_]+$'
    if not re.match(pattern, ticker):
        # Remove caracteres inválidos
        ticker = re.sub(r'[^A-Za-z0-9.\-^_]', '', ticker)
    
    if not ticker:
        raise ValueError("Ticker contém apenas caracteres inválidos")
    
    # Limitar tamanho
    if len(ticker) > 20:
        raise ValueError("Ticker muito longo (máximo 20 caracteres)")
    
    return ticker


def sanitize_tickers(tickers: List[str]) -> List[str]:
    """Sanitiza lista de tickers."""
    if not tickers:
        raise ValueError("Lista de tickers não pode ser vazia")
    
    sanitized = []
    for t in tickers:
        try:
            sanitized.append(sanitize_ticker(t))
        except ValueError as e:
            raise ValueError(f"Ticker inválido '{t}': {e}")
    
    # Remover duplicatas mantendo ordem
    seen = set()
    unique = []
    for t in sanitized:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    
    return unique


def validate_date_format(date_str: str) -> bool:
    """Valida se string está no formato YYYY-MM-DD."""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))


def sanitize_date(date_str: str) -> str:
    """Sanitiza e valida data."""
    if not date_str:
        raise ValueError("Data não pode ser vazia")
    
    date_str = date_str.strip()
    
    if not validate_date_format(date_str):
        raise ValueError(f"Data inválida '{date_str}'. Use formato YYYY-MM-DD")
    
    # Validar valores
    try:
        year, month, day = map(int, date_str.split('-'))
        if year < 1900 or year > 2100:
            raise ValueError(f"Ano inválido: {year}")
        if month < 1 or month > 12:
            raise ValueError(f"Mês inválido: {month}")
        if day < 1 or day > 31:
            raise ValueError(f"Dia inválido: {day}")
    except ValueError as e:
        raise ValueError(f"Data inválida '{date_str}': {e}")
    
    return date_str


def validate_weights(weights: Optional[List[float]], n_assets: int) -> Optional[List[float]]:
    """Valida lista de pesos.
    
    Retorna:
        weights validados ou None se input for None.
    
    Raises:
        ValueError: se pesos inválidos.
    """
    if weights is None:
        return None
    
    if len(weights) != n_assets:
        raise ValueError(f"Número de pesos ({len(weights)}) difere do número de ativos ({n_assets})")
    
    if any(w < 0 for w in weights):
        raise ValueError("Pesos não podem ser negativos")
    
    total = sum(weights)
    if total <= 0:
        raise ValueError("Soma dos pesos deve ser > 0")
    
    # Normalizar para somar 1
    normalized = [w / total for w in weights]
    
    return normalized


def validate_alpha(alpha: float) -> float:
    """Valida nível de confiança alpha."""
    if alpha <= 0 or alpha >= 1:
        raise ValueError(f"Alpha deve estar entre 0 e 1 (exclusivo). Recebido: {alpha}")
    
    # Valores comuns
    common_alphas = [0.90, 0.95, 0.99, 0.995, 0.999]
    if alpha not in common_alphas:
        import logging
        logging.warning(
            f"Alpha {alpha} não é um valor comum. "
            f"Valores típicos: {common_alphas}"
        )
    
    return alpha


def sanitize_string(s: str, max_length: int = 100) -> str:
    """Sanitiza string genérica."""
    if not s:
        raise ValueError("String não pode ser vazia")
    
    s = s.strip()
    
    if len(s) > max_length:
        raise ValueError(f"String muito longa (máximo {max_length} caracteres)")
    
    # Remove caracteres de controle
    s = ''.join(char for char in s if ord(char) >= 32)
    
    return s
