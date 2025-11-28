"""
Repository Interfaces for Domain-Driven Design.

Repositories são abstrações para persistência de Aggregates.
Definem contratos que a camada de Infrastructure deve implementar.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

from .entities import Portfolio, Position, Transaction, User
from .value_objects import Ticker, DateRange


class IPortfolioRepository(ABC):
    """
    Interface de repositório para Portfolio (Aggregate Root).
    """

    @abstractmethod
    async def get_by_id(self, portfolio_id: UUID) -> Optional[Portfolio]:
        """Busca um portfólio pelo ID."""
        pass

    @abstractmethod
    async def get_by_owner(self, owner_id: UUID) -> List[Portfolio]:
        """Busca todos os portfólios de um usuário."""
        pass

    @abstractmethod
    async def save(self, portfolio: Portfolio) -> Portfolio:
        """Salva ou atualiza um portfólio."""
        pass

    @abstractmethod
    async def delete(self, portfolio_id: UUID) -> bool:
        """Remove um portfólio."""
        pass

    @abstractmethod
    async def exists(self, portfolio_id: UUID) -> bool:
        """Verifica se um portfólio existe."""
        pass


class ITransactionRepository(ABC):
    """
    Interface de repositório para Transactions.
    """

    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> Optional[Transaction]:
        """Busca uma transação pelo ID."""
        pass

    @abstractmethod
    async def get_by_portfolio(
        self, 
        portfolio_id: UUID, 
        date_range: Optional[DateRange] = None
    ) -> List[Transaction]:
        """Busca transações de um portfólio, opcionalmente filtradas por período."""
        pass

    @abstractmethod
    async def get_by_ticker(
        self, 
        portfolio_id: UUID, 
        ticker: Ticker
    ) -> List[Transaction]:
        """Busca transações de um ticker específico."""
        pass

    @abstractmethod
    async def save(self, transaction: Transaction, portfolio_id: UUID) -> Transaction:
        """Salva uma transação."""
        pass

    @abstractmethod
    async def delete(self, transaction_id: UUID) -> bool:
        """Remove uma transação."""
        pass


class IUserRepository(ABC):
    """
    Interface de repositório para Users.
    """

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Busca um usuário pelo ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Busca um usuário pelo email."""
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        """Salva ou atualiza um usuário."""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Remove um usuário."""
        pass

    @abstractmethod
    async def exists_email(self, email: str) -> bool:
        """Verifica se um email já está cadastrado."""
        pass


class IMarketDataRepository(ABC):
    """
    Interface de repositório para dados de mercado.
    Abstrai a fonte de dados (yfinance, API, cache, etc).
    """

    @abstractmethod
    async def get_prices(
        self, 
        tickers: List[Ticker], 
        date_range: DateRange
    ) -> Dict[str, Any]:
        """
        Busca preços históricos.
        Retorna DataFrame-like com preços ajustados.
        """
        pass

    @abstractmethod
    async def get_current_prices(self, tickers: List[Ticker]) -> Dict[str, float]:
        """Busca preços atuais."""
        pass

    @abstractmethod
    async def get_fundamentals(self, ticker: Ticker) -> Dict[str, Any]:
        """Busca dados fundamentalistas de um ativo."""
        pass

    @abstractmethod
    async def get_dividends(
        self, 
        ticker: Ticker, 
        date_range: DateRange
    ) -> List[Dict[str, Any]]:
        """Busca histórico de dividendos."""
        pass


class ICDIRepository(ABC):
    """
    Interface de repositório para dados do CDI.
    """

    @abstractmethod
    async def get_rates(self, date_range: DateRange) -> Dict[date, float]:
        """Busca taxas CDI diárias para o período."""
        pass

    @abstractmethod
    async def get_current_rate(self) -> float:
        """Busca taxa CDI atual (anualizada)."""
        pass

    @abstractmethod
    async def get_accumulated(self, date_range: DateRange) -> float:
        """Calcula CDI acumulado no período."""
        pass


class ICacheRepository(ABC):
    """
    Interface de repositório para cache.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Busca valor do cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Salva valor no cache com TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Remove valor do cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Verifica se chave existe no cache."""
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Remove todas as chaves que correspondem ao padrão."""
        pass
