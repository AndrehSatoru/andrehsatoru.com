"""
Value Objects for Domain-Driven Design.

Value Objects são objetos imutáveis que representam conceitos do domínio
sem identidade própria. Dois Value Objects são iguais se seus valores são iguais.
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from datetime import date


@dataclass(frozen=True)
class Money:
    """
    Value Object que representa um valor monetário.
    Imutável e com precisão decimal para cálculos financeiros.
    """
    amount: Decimal
    currency: str = "BRL"

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, 'amount', Decimal(str(self.amount)))

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {self.currency} and {other.currency}")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, factor: float) -> "Money":
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def __truediv__(self, divisor: float) -> "Money":
        return Money(self.amount / Decimal(str(divisor)), self.currency)

    def round(self, places: int = 2) -> "Money":
        """Arredonda para o número especificado de casas decimais."""
        quantize_str = "0." + "0" * places
        rounded = self.amount.quantize(Decimal(quantize_str), rounding=ROUND_HALF_UP)
        return Money(rounded, self.currency)

    def to_float(self) -> float:
        """Converte para float (usar com cuidado em cálculos)."""
        return float(self.amount)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:,.2f}"


@dataclass(frozen=True)
class Percentage:
    """
    Value Object que representa uma porcentagem.
    Armazena internamente como decimal (0.15 = 15%).
    """
    value: Decimal

    def __post_init__(self):
        if not isinstance(self.value, Decimal):
            object.__setattr__(self, 'value', Decimal(str(self.value)))

    @classmethod
    def from_percent(cls, percent: float) -> "Percentage":
        """Cria a partir de valor percentual (15 -> 0.15)."""
        return cls(Decimal(str(percent)) / 100)

    @classmethod
    def from_decimal(cls, decimal_value: float) -> "Percentage":
        """Cria a partir de valor decimal (0.15 -> 0.15)."""
        return cls(Decimal(str(decimal_value)))

    def to_percent(self) -> float:
        """Retorna como percentual (0.15 -> 15.0)."""
        return float(self.value * 100)

    def to_decimal(self) -> float:
        """Retorna como decimal (0.15 -> 0.15)."""
        return float(self.value)

    def __mul__(self, other: Money) -> Money:
        """Aplica a porcentagem a um valor monetário."""
        if isinstance(other, Money):
            return Money(other.amount * self.value, other.currency)
        return Percentage(self.value * Decimal(str(other)))

    def __str__(self) -> str:
        return f"{self.to_percent():.2f}%"


@dataclass(frozen=True)
class Ticker:
    """
    Value Object que representa um símbolo de ativo.
    Valida e normaliza o formato do ticker.
    """
    symbol: str
    exchange: Optional[str] = None

    def __post_init__(self):
        # Normaliza para uppercase
        object.__setattr__(self, 'symbol', self.symbol.upper().strip())
        
        # Detecta exchange do sufixo se não especificado
        if self.exchange is None and '.' in self.symbol:
            parts = self.symbol.split('.')
            if len(parts) == 2:
                object.__setattr__(self, 'exchange', parts[1])

    @property
    def is_brazilian(self) -> bool:
        """Verifica se é um ativo brasileiro (B3)."""
        return self.exchange == "SA" or self.symbol.endswith(".SA")

    @property
    def is_index(self) -> bool:
        """Verifica se é um índice (começa com ^)."""
        return self.symbol.startswith("^")

    def with_suffix(self, suffix: str) -> "Ticker":
        """Retorna novo ticker com sufixo adicionado."""
        base = self.symbol.split('.')[0]
        return Ticker(f"{base}.{suffix}")

    def __str__(self) -> str:
        return self.symbol


@dataclass(frozen=True)
class DateRange:
    """
    Value Object que representa um intervalo de datas.
    Garante que start <= end.
    """
    start: date
    end: date

    def __post_init__(self):
        if isinstance(self.start, str):
            object.__setattr__(self, 'start', date.fromisoformat(self.start))
        if isinstance(self.end, str):
            object.__setattr__(self, 'end', date.fromisoformat(self.end))
        
        if self.start > self.end:
            raise ValueError(f"Start date {self.start} cannot be after end date {self.end}")

    @property
    def days(self) -> int:
        """Número de dias no intervalo."""
        return (self.end - self.start).days

    @property
    def trading_days(self) -> int:
        """Número estimado de dias úteis (aproximado)."""
        return int(self.days * 252 / 365)

    def contains(self, d: date) -> bool:
        """Verifica se uma data está dentro do intervalo."""
        return self.start <= d <= self.end

    def overlaps(self, other: "DateRange") -> bool:
        """Verifica se há sobreposição com outro intervalo."""
        return self.start <= other.end and other.start <= self.end

    def __str__(self) -> str:
        return f"{self.start} to {self.end}"


@dataclass(frozen=True)
class Weight:
    """
    Value Object que representa um peso de alocação.
    Garante que o peso está entre 0 e 1 (ou permite short se especificado).
    """
    value: Decimal
    allow_short: bool = False

    def __post_init__(self):
        if not isinstance(self.value, Decimal):
            object.__setattr__(self, 'value', Decimal(str(self.value)))
        
        if not self.allow_short and self.value < 0:
            raise ValueError(f"Weight cannot be negative: {self.value}")
        
        if self.value > 1:
            raise ValueError(f"Weight cannot exceed 100%: {self.value}")

    def to_percent(self) -> float:
        """Retorna como percentual."""
        return float(self.value * 100)

    def to_decimal(self) -> float:
        """Retorna como decimal."""
        return float(self.value)

    def __str__(self) -> str:
        return f"{self.to_percent():.2f}%"


@dataclass(frozen=True)
class RiskMetrics:
    """
    Value Object que agrupa métricas de risco de um portfólio.
    Imutável após criação.
    """
    var_95: Percentage
    var_99: Percentage
    cvar_95: Percentage
    cvar_99: Percentage
    volatility: Percentage
    max_drawdown: Percentage
    sharpe_ratio: float
    beta: Optional[float] = None

    def __str__(self) -> str:
        return (
            f"VaR 95%: {self.var_95}, VaR 99%: {self.var_99}, "
            f"Volatility: {self.volatility}, Sharpe: {self.sharpe_ratio:.2f}"
        )


@dataclass(frozen=True)
class PortfolioAllocation:
    """
    Value Object que representa uma alocação de portfólio.
    Mapeamento ticker -> peso, garantindo que soma = 100%.
    """
    allocations: tuple  # tuple de (Ticker, Weight) para ser hashable

    def __post_init__(self):
        # Valida que a soma dos pesos é aproximadamente 1
        total = sum(w.to_decimal() for _, w in self.allocations)
        if abs(total - 1.0) > 0.0001:
            raise ValueError(f"Allocations must sum to 100%, got {total * 100:.2f}%")

    @classmethod
    def from_dict(cls, weights: dict) -> "PortfolioAllocation":
        """Cria a partir de um dicionário {ticker: peso}."""
        allocations = tuple(
            (Ticker(k), Weight(v)) for k, v in weights.items()
        )
        return cls(allocations)

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {str(ticker): weight.to_decimal() for ticker, weight in self.allocations}

    def get_weight(self, ticker: str) -> Optional[Weight]:
        """Retorna o peso de um ticker específico."""
        for t, w in self.allocations:
            if str(t) == ticker.upper():
                return w
        return None

    @property
    def tickers(self) -> list:
        """Lista de tickers na alocação."""
        return [str(t) for t, _ in self.allocations]

    def __str__(self) -> str:
        parts = [f"{t}: {w}" for t, w in self.allocations]
        return ", ".join(parts)
