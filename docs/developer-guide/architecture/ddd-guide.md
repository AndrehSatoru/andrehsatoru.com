# Domain-Driven Design (DDD) no Backend

Este documento descreve a implementação dos padrões de Domain-Driven Design no backend.

## 1. Visão Geral

O backend segue os princípios de **Clean Architecture** combinados com **DDD** para criar uma base de código manutenível, testável e escalável.

### Princípios Aplicados

| Princípio | Implementação |
|-----------|---------------|
| **Separation of Concerns** | Camadas bem definidas (Domain, Application, Infrastructure, API) |
| **Dependency Inversion** | Domain define interfaces, Infrastructure implementa |
| **Single Responsibility** | Cada classe tem uma única responsabilidade |
| **Ubiquitous Language** | Código reflete a linguagem do domínio financeiro |

## 2. Camadas da Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│                        API Layer                              │
│  • FastAPI Controllers                                        │
│  • Request/Response DTOs                                      │
│  • Dependency Injection                                       │
└─────────────────────────────┬────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────┐
│                    Application Layer                          │
│  • Use Cases                                                  │
│  • Application Services                                       │
│  • Orchestration Logic                                        │
└─────────────────────────────┬────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────┐
│                      Domain Layer                             │
│  • Entities (Portfolio, Transaction, Position)                │
│  • Value Objects (Money, Percentage, Ticker)                  │
│  • Domain Services (RiskCalculation, Optimization)            │
│  • Repository Interfaces                                      │
│  • Domain Exceptions                                          │
└─────────────────────────────▲────────────────────────────────┘
                              │
┌─────────────────────────────┴────────────────────────────────┐
│                  Infrastructure Layer                         │
│  • Repository Implementations                                 │
│  • External API Clients (yfinance, BCB)                       │
│  • Cache Implementation                                       │
│  • Database Access                                            │
└──────────────────────────────────────────────────────────────┘
```

## 3. Value Objects

Value Objects são objetos imutáveis definidos por seus atributos, não por identidade.

### `Money`
```python
from domain.value_objects import Money

# Criação
price = Money(100.50)  # BRL por padrão
price_usd = Money(100.50, "USD")

# Operações
total = price + Money(50.25)  # Money(150.75, "BRL")
doubled = price * 2           # Money(201.00, "BRL")

# Formatação
print(price)  # "BRL 100.50"
```

### `Percentage`
```python
from domain.value_objects import Percentage

# De percentual (15 = 15%)
pct = Percentage.from_percent(15)

# De decimal (0.15 = 15%)
pct = Percentage.from_decimal(0.15)

# Operações
value = pct * Money(1000)  # Money(150.00)
print(pct)                 # "15.00%"
```

### `Ticker`
```python
from domain.value_objects import Ticker

ticker = Ticker("PETR4.SA")
print(ticker.is_brazilian)  # True
print(ticker.is_index)      # False

ibov = Ticker("^BVSP")
print(ibov.is_index)        # True
```

### `DateRange`
```python
from domain.value_objects import DateRange
from datetime import date

period = DateRange(date(2024, 1, 1), date(2024, 12, 31))
print(period.days)          # 365
print(period.trading_days)  # ~252
```

## 4. Entities

Entities têm identidade única que persiste ao longo do tempo.

### `Transaction`
```python
from domain.entities import Transaction, TransactionType

tx = Transaction(
    id=uuid4(),
    ticker=Ticker("VALE3.SA"),
    transaction_type=TransactionType.BUY,
    quantity=100,
    unit_price=Money(68.50),
    transaction_date=date(2024, 3, 15)
)

print(tx.total_value)  # Money(6850.00, "BRL")
```

### `Portfolio` (Aggregate Root)
```python
from domain.entities import Portfolio

portfolio = Portfolio(
    id=uuid4(),
    name="Minha Carteira",
    owner_id=user.id
)

# Adicionar transação
portfolio.add_transaction(tx)

# Consultar alocação
allocation = portfolio.get_allocation()
# {"VALE3.SA": 0.35, "PETR4.SA": 0.25, ...}

# Valor total
total = portfolio.total_market_value
```

## 5. Repository Interfaces

Definem contratos para persistência, sem implementação concreta.

```python
from domain.repositories import IPortfolioRepository

class IPortfolioRepository(ABC):
    @abstractmethod
    async def get_by_id(self, portfolio_id: UUID) -> Optional[Portfolio]:
        pass

    @abstractmethod
    async def save(self, portfolio: Portfolio) -> Portfolio:
        pass
```

### Implementação na Infrastructure
```python
# infrastructure/repositories/portfolio_repository.py
from domain.repositories import IPortfolioRepository

class PostgresPortfolioRepository(IPortfolioRepository):
    def __init__(self, db_session):
        self.db = db_session

    async def get_by_id(self, portfolio_id: UUID) -> Optional[Portfolio]:
        # Implementação real com PostgreSQL
        ...
```

## 6. Domain Services

Encapsulam lógica que não pertence a uma única Entity.

### `RiskCalculationService`
```python
from domain.services import RiskCalculationService

risk_service = RiskCalculationService()

# Calcular VaR
var_95 = risk_service.calculate_var(returns, confidence=0.95)

# Calcular métricas completas
metrics = risk_service.calculate_risk_metrics(
    returns=daily_returns,
    prices=prices,
    risk_free_rate=0.1175  # SELIC
)
print(metrics.sharpe_ratio)
print(metrics.volatility)
```

### `PortfolioOptimizationService`
```python
from domain.services import PortfolioOptimizationService

opt_service = PortfolioOptimizationService()

# Fronteira eficiente
frontier = opt_service.calculate_efficient_frontier(returns_matrix)

# Máximo Sharpe
weights, sharpe = opt_service.optimize_max_sharpe(returns_matrix)
```

## 7. Exceptions

Exceções específicas do domínio para tratamento de erros.

```python
from domain.exceptions import AppError, DataProviderError

class InsufficientFundsError(AppError):
    """Fundos insuficientes para a operação."""
    pass

class InvalidAllocationError(AppError):
    """Alocação inválida (soma != 100%)."""
    pass
```

## 8. Benefícios da Arquitetura

| Benefício | Descrição |
|-----------|-----------|
| **Testabilidade** | Domain pode ser testado isoladamente, sem dependências externas |
| **Manutenibilidade** | Mudanças em uma camada não afetam outras |
| **Flexibilidade** | Fácil trocar implementações (ex: PostgreSQL → MongoDB) |
| **Clareza** | Código expressa a linguagem do domínio financeiro |
| **Escalabilidade** | Cada camada pode escalar independentemente |

## 9. Exemplos de Uso

### Caso de Uso: Processar Transação
```python
# application/use_cases/process_transaction.py
class ProcessTransactionUseCase:
    def __init__(
        self,
        portfolio_repo: IPortfolioRepository,
        market_data_repo: IMarketDataRepository
    ):
        self.portfolio_repo = portfolio_repo
        self.market_data_repo = market_data_repo

    async def execute(self, portfolio_id: UUID, transaction: Transaction):
        # 1. Buscar portfólio
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            raise PortfolioNotFoundError(portfolio_id)

        # 2. Adicionar transação (lógica de domínio)
        portfolio.add_transaction(transaction)

        # 3. Atualizar preços
        tickers = [Ticker(t) for t in portfolio.positions.keys()]
        prices = await self.market_data_repo.get_current_prices(tickers)
        portfolio.update_prices(prices)

        # 4. Persistir
        await self.portfolio_repo.save(portfolio)

        return portfolio
```

## 10. Próximos Passos

Para completar a implementação DDD:

- [ ] Implementar repositórios concretos na Infrastructure
- [ ] Adicionar Event Sourcing para transações
- [ ] Implementar Domain Events (TransactionCreated, PortfolioUpdated)
- [ ] Criar Aggregates para análises (AnalysisResult)
- [ ] Adicionar Specifications para queries complexas
