"""
Repository Interfaces for Domain-Driven Design.

Repositories are abstractions for Aggregate persistence.
They define contracts that the Infrastructure layer must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

from .entities import Portfolio, Position, Transaction, User
from .value_objects import Ticker, DateRange


class IPortfolioRepository(ABC):
    """
    Repository interface for Portfolio (Aggregate Root).
    """

    @abstractmethod
    async def get_by_id(self, portfolio_id: UUID) -> Optional[Portfolio]:
        """Retrieves a portfolio by ID."""
        pass

    @abstractmethod
    async def get_by_owner(self, owner_id: UUID) -> List[Portfolio]:
        """Retrieves all portfolios for a user."""
        pass

    @abstractmethod
    async def save(self, portfolio: Portfolio) -> Portfolio:
        """Saves or updates a portfolio."""
        pass

    @abstractmethod
    async def delete(self, portfolio_id: UUID) -> bool:
        """Removes a portfolio."""
        pass

    @abstractmethod
    async def exists(self, portfolio_id: UUID) -> bool:
        """Checks if a portfolio exists."""
        pass


class ITransactionRepository(ABC):
    """
    Repository interface for Transactions.
    """

    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> Optional[Transaction]:
        """Retrieves a transaction by ID."""
        pass

    @abstractmethod
    async def get_by_portfolio(
        self, 
        portfolio_id: UUID, 
        date_range: Optional[DateRange] = None
    ) -> List[Transaction]:
        """Retrieves transactions for a portfolio, optionally filtered by date range."""
        pass

    @abstractmethod
    async def get_by_ticker(
        self, 
        portfolio_id: UUID, 
        ticker: Ticker
    ) -> List[Transaction]:
        """Retrieves transactions for a specific ticker."""
        pass

    @abstractmethod
    async def save(self, transaction: Transaction, portfolio_id: UUID) -> Transaction:
        """Saves a transaction."""
        pass

    @abstractmethod
    async def delete(self, transaction_id: UUID) -> bool:
        """Removes a transaction."""
        pass


class IUserRepository(ABC):
    """
    Repository interface for Users.
    """

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieves a user by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieves a user by email."""
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        """Saves or updates a user."""
        pass

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Removes a user."""
        pass

    @abstractmethod
    async def exists_email(self, email: str) -> bool:
        """Checks if an email is already registered."""
        pass


class IMarketDataRepository(ABC):
    """
    Repository interface for market data.
    Abstracts the data source (yfinance, API, cache, etc).
    """

    @abstractmethod
    async def get_prices(
        self, 
        tickers: List[Ticker], 
        date_range: DateRange
    ) -> Dict[str, Any]:
        """
        Retrieves historical prices.
        Returns a DataFrame-like object with adjusted prices.
        """
        pass

    @abstractmethod
    async def get_current_prices(self, tickers: List[Ticker]) -> Dict[str, float]:
        """Retrieves current prices."""
        pass

    @abstractmethod
    async def get_fundamentals(self, ticker: Ticker) -> Dict[str, Any]:
        """Retrieves fundamental data for an asset."""
        pass

    @abstractmethod
    async def get_dividends(
        self, 
        ticker: Ticker, 
        date_range: DateRange
    ) -> List[Dict[str, Any]]:
        """Retrieves dividend history."""
        pass


class ICDIRepository(ABC):
    """
    Repository interface for CDI (Interbank Deposit Certificate) data.
    """

    @abstractmethod
    async def get_rates(self, date_range: DateRange) -> Dict[date, float]:
        """Retrieves daily CDI rates for the period."""
        pass

    @abstractmethod
    async def get_current_rate(self) -> float:
        """Retrieves current CDI rate (annualized)."""
        pass

    @abstractmethod
    async def get_accumulated(self, date_range: DateRange) -> float:
        """Calculates accumulated CDI over the period."""
        pass


class ICacheRepository(ABC):
    """
    Repository interface for caching.
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieves a value from cache."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """Saves a value to cache with TTL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Removes a value from cache."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Checks if a key exists in cache."""
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Removes all keys matching the pattern."""
        pass