"""
Domain Entities for Domain-Driven Design.

Entities são objetos com identidade única que persiste ao longo do tempo.
Dois Entities são iguais se têm o mesmo ID, mesmo que outros atributos difiram.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4
from enum import Enum

from .value_objects import Money, Percentage, Ticker, Weight, DateRange


class TransactionType(Enum):
    """Tipo de transação."""
    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    SPLIT = "split"
    BONUS = "bonus"


class AssetType(Enum):
    """Tipo de ativo."""
    STOCK = "stock"
    ETF = "etf"
    FII = "fii"
    BDR = "bdr"
    INDEX = "index"
    CASH = "cash"


@dataclass
class Transaction:
    """
    Entity que representa uma transação de compra/venda.
    Tem identidade única (id) que a distingue de outras transações.
    """
    id: UUID
    ticker: Ticker
    transaction_type: TransactionType
    quantity: Decimal
    unit_price: Money
    transaction_date: date
    broker: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not isinstance(self.id, UUID):
            self.id = UUID(str(self.id)) if self.id else uuid4()
        if not isinstance(self.ticker, Ticker):
            self.ticker = Ticker(self.ticker)
        if not isinstance(self.transaction_type, TransactionType):
            self.transaction_type = TransactionType(self.transaction_type)
        if not isinstance(self.quantity, Decimal):
            self.quantity = Decimal(str(self.quantity))
        if not isinstance(self.unit_price, Money):
            self.unit_price = Money(self.unit_price)
        if isinstance(self.transaction_date, str):
            self.transaction_date = date.fromisoformat(self.transaction_date)

    @property
    def total_value(self) -> Money:
        """Valor total da transação."""
        return self.unit_price * float(self.quantity)

    @property
    def is_buy(self) -> bool:
        return self.transaction_type == TransactionType.BUY

    @property
    def is_sell(self) -> bool:
        return self.transaction_type == TransactionType.SELL

    def __eq__(self, other) -> bool:
        if not isinstance(other, Transaction):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class Position:
    """
    Entity que representa uma posição em um ativo.
    Agrega transações para calcular a posição atual.
    """
    id: UUID
    ticker: Ticker
    quantity: Decimal
    average_price: Money
    current_price: Optional[Money] = None
    asset_type: AssetType = AssetType.STOCK
    transactions: List[Transaction] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.id, UUID):
            self.id = UUID(str(self.id)) if self.id else uuid4()
        if not isinstance(self.ticker, Ticker):
            self.ticker = Ticker(self.ticker)
        if not isinstance(self.quantity, Decimal):
            self.quantity = Decimal(str(self.quantity))
        if not isinstance(self.average_price, Money):
            self.average_price = Money(self.average_price)

    @property
    def cost_basis(self) -> Money:
        """Custo total da posição."""
        return self.average_price * float(self.quantity)

    @property
    def market_value(self) -> Optional[Money]:
        """Valor de mercado atual."""
        if self.current_price is None:
            return None
        return self.current_price * float(self.quantity)

    @property
    def unrealized_pnl(self) -> Optional[Money]:
        """Lucro/prejuízo não realizado."""
        if self.market_value is None:
            return None
        return self.market_value - self.cost_basis

    @property
    def unrealized_pnl_percent(self) -> Optional[Percentage]:
        """Retorno percentual não realizado."""
        if self.unrealized_pnl is None or self.cost_basis.amount == 0:
            return None
        return Percentage.from_decimal(
            float(self.unrealized_pnl.amount / self.cost_basis.amount)
        )

    def add_transaction(self, transaction: Transaction) -> None:
        """Adiciona uma transação e recalcula a posição."""
        self.transactions.append(transaction)
        self._recalculate()

    def _recalculate(self) -> None:
        """Recalcula quantidade e preço médio a partir das transações."""
        total_quantity = Decimal(0)
        total_cost = Decimal(0)

        for tx in sorted(self.transactions, key=lambda t: t.transaction_date):
            if tx.is_buy:
                total_cost += tx.quantity * tx.unit_price.amount
                total_quantity += tx.quantity
            elif tx.is_sell:
                if total_quantity > 0:
                    # Realiza venda pelo preço médio atual
                    avg = total_cost / total_quantity
                    total_cost -= tx.quantity * avg
                total_quantity -= tx.quantity

        self.quantity = total_quantity
        if total_quantity > 0:
            self.average_price = Money(total_cost / total_quantity)
        else:
            self.average_price = Money(Decimal(0))

    def __eq__(self, other) -> bool:
        if not isinstance(other, Position):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class Portfolio:
    """
    Aggregate Root que representa um portfólio de investimentos.
    Coordena as posições e garante invariantes do domínio.
    """
    id: UUID
    name: str
    owner_id: UUID
    positions: Dict[str, Position] = field(default_factory=dict)
    cash_balance: Money = field(default_factory=lambda: Money(Decimal(0)))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not isinstance(self.id, UUID):
            self.id = UUID(str(self.id)) if self.id else uuid4()
        if not isinstance(self.owner_id, UUID):
            self.owner_id = UUID(str(self.owner_id)) if self.owner_id else uuid4()

    @property
    def total_invested(self) -> Money:
        """Total investido (custo base de todas as posições)."""
        total = Money(Decimal(0))
        for position in self.positions.values():
            total = total + position.cost_basis
        return total

    @property
    def total_market_value(self) -> Optional[Money]:
        """Valor total de mercado."""
        total = self.cash_balance
        for position in self.positions.values():
            if position.market_value is None:
                return None
            total = total + position.market_value
        return total

    @property
    def total_pnl(self) -> Optional[Money]:
        """Lucro/prejuízo total não realizado."""
        if self.total_market_value is None:
            return None
        return self.total_market_value - self.total_invested - self.cash_balance

    @property
    def asset_count(self) -> int:
        """Número de ativos diferentes no portfólio."""
        return len([p for p in self.positions.values() if p.quantity > 0])

    def get_allocation(self) -> Dict[str, float]:
        """Retorna a alocação percentual por ativo."""
        total = self.total_market_value
        if total is None or total.amount == 0:
            return {}
        
        allocation = {}
        for ticker, position in self.positions.items():
            if position.market_value and position.quantity > 0:
                allocation[ticker] = float(position.market_value.amount / total.amount)
        return allocation

    def add_transaction(self, transaction: Transaction) -> None:
        """
        Adiciona uma transação ao portfólio.
        Cria nova posição se necessário, ou atualiza existente.
        """
        ticker_str = str(transaction.ticker)
        
        if ticker_str not in self.positions:
            self.positions[ticker_str] = Position(
                id=uuid4(),
                ticker=transaction.ticker,
                quantity=Decimal(0),
                average_price=Money(Decimal(0))
            )
        
        self.positions[ticker_str].add_transaction(transaction)
        self.updated_at = datetime.now()

        # Remove posição se quantidade zerou
        if self.positions[ticker_str].quantity <= 0:
            del self.positions[ticker_str]

    def update_prices(self, prices: Dict[str, float]) -> None:
        """Atualiza os preços atuais das posições."""
        for ticker, price in prices.items():
            if ticker in self.positions:
                self.positions[ticker].current_price = Money(Decimal(str(price)))
        self.updated_at = datetime.now()

    def deposit_cash(self, amount: Money) -> None:
        """Deposita dinheiro no portfólio."""
        self.cash_balance = self.cash_balance + amount
        self.updated_at = datetime.now()

    def withdraw_cash(self, amount: Money) -> None:
        """Retira dinheiro do portfólio."""
        if amount.amount > self.cash_balance.amount:
            raise ValueError("Insufficient cash balance")
        self.cash_balance = self.cash_balance - amount
        self.updated_at = datetime.now()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Portfolio):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class User:
    """
    Entity que representa um usuário do sistema.
    """
    id: UUID
    email: str
    name: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    portfolios: List[UUID] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.id, UUID):
            self.id = UUID(str(self.id)) if self.id else uuid4()

    def add_portfolio(self, portfolio_id: UUID) -> None:
        """Associa um portfólio ao usuário."""
        if portfolio_id not in self.portfolios:
            self.portfolios.append(portfolio_id)

    def remove_portfolio(self, portfolio_id: UUID) -> None:
        """Remove associação de um portfólio."""
        if portfolio_id in self.portfolios:
            self.portfolios.remove(portfolio_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
