"""
Domain Services for Domain-Driven Design.

Domain Services encapsulam lógica de negócio que não pertence
naturalmente a uma Entity ou Value Object específico.
"""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from datetime import date
import numpy as np

from .entities import Portfolio, Position, Transaction, TransactionType
from .value_objects import (
    Money, Percentage, Ticker, Weight, DateRange, 
    RiskMetrics, PortfolioAllocation
)


class PortfolioValuationService:
    """
    Domain Service para cálculo de valorização de portfólio.
    """

    def calculate_daily_returns(
        self, 
        prices: Dict[str, List[float]], 
        allocations: Dict[str, float]
    ) -> List[float]:
        """
        Calcula retornos diários do portfólio baseado nos preços e alocações.
        """
        if not prices or not allocations:
            return []

        # Converte para arrays numpy
        tickers = list(allocations.keys())
        weights = np.array([allocations.get(t, 0) for t in tickers])
        
        # Matriz de preços
        price_matrix = np.array([prices.get(t, []) for t in tickers])
        
        if price_matrix.size == 0:
            return []

        # Calcula retornos
        returns_matrix = np.diff(price_matrix, axis=1) / price_matrix[:, :-1]
        
        # Retorno do portfólio (soma ponderada)
        portfolio_returns = np.dot(weights, returns_matrix)
        
        return portfolio_returns.tolist()

    def calculate_cumulative_return(self, daily_returns: List[float]) -> float:
        """Calcula retorno acumulado a partir de retornos diários."""
        if not daily_returns:
            return 0.0
        return float(np.prod([1 + r for r in daily_returns]) - 1)

    def calculate_annualized_return(
        self, 
        cumulative_return: float, 
        days: int
    ) -> float:
        """Anualiza um retorno baseado no número de dias."""
        if days <= 0:
            return 0.0
        return float((1 + cumulative_return) ** (252 / days) - 1)


class RiskCalculationService:
    """
    Domain Service para cálculos de risco.
    """

    def calculate_var(
        self, 
        returns: List[float], 
        confidence: float = 0.95,
        method: str = "historical"
    ) -> Percentage:
        """
        Calcula Value at Risk.
        
        Args:
            returns: Lista de retornos
            confidence: Nível de confiança (ex: 0.95 para 95%)
            method: 'historical' ou 'parametric'
        """
        if not returns:
            return Percentage.from_decimal(0)

        returns_array = np.array(returns)
        
        if method == "historical":
            var = np.percentile(returns_array, (1 - confidence) * 100)
        else:  # parametric
            mean = np.mean(returns_array)
            std = np.std(returns_array)
            from scipy.stats import norm
            var = mean + std * norm.ppf(1 - confidence)
        
        return Percentage.from_decimal(float(var))

    def calculate_cvar(
        self, 
        returns: List[float], 
        confidence: float = 0.95
    ) -> Percentage:
        """
        Calcula Conditional Value at Risk (Expected Shortfall).
        """
        if not returns:
            return Percentage.from_decimal(0)

        returns_array = np.array(returns)
        var = np.percentile(returns_array, (1 - confidence) * 100)
        cvar = returns_array[returns_array <= var].mean()
        
        return Percentage.from_decimal(float(cvar))

    def calculate_volatility(
        self, 
        returns: List[float], 
        annualize: bool = True
    ) -> Percentage:
        """Calcula volatilidade (desvio padrão dos retornos)."""
        if not returns:
            return Percentage.from_decimal(0)

        vol = float(np.std(returns))
        if annualize:
            vol *= np.sqrt(252)
        
        return Percentage.from_decimal(vol)

    def calculate_max_drawdown(self, prices: List[float]) -> Percentage:
        """Calcula o máximo drawdown."""
        if not prices or len(prices) < 2:
            return Percentage.from_decimal(0)

        prices_array = np.array(prices)
        cummax = np.maximum.accumulate(prices_array)
        drawdowns = (prices_array - cummax) / cummax
        max_dd = float(np.min(drawdowns))
        
        return Percentage.from_decimal(max_dd)

    def calculate_sharpe_ratio(
        self, 
        returns: List[float], 
        risk_free_rate: float = 0.0
    ) -> float:
        """Calcula o Índice de Sharpe."""
        if not returns:
            return 0.0

        excess_returns = np.array(returns) - risk_free_rate / 252
        mean_excess = np.mean(excess_returns) * 252
        vol = np.std(excess_returns) * np.sqrt(252)
        
        if vol == 0:
            return 0.0
        
        return float(mean_excess / vol)

    def calculate_beta(
        self, 
        asset_returns: List[float], 
        benchmark_returns: List[float]
    ) -> float:
        """Calcula o beta em relação a um benchmark."""
        if len(asset_returns) != len(benchmark_returns) or not asset_returns:
            return 1.0

        covariance = np.cov(asset_returns, benchmark_returns)[0, 1]
        benchmark_variance = np.var(benchmark_returns)
        
        if benchmark_variance == 0:
            return 1.0
        
        return float(covariance / benchmark_variance)

    def calculate_risk_metrics(
        self,
        returns: List[float],
        prices: List[float],
        risk_free_rate: float = 0.0,
        benchmark_returns: Optional[List[float]] = None
    ) -> RiskMetrics:
        """Calcula todas as métricas de risco."""
        beta = None
        if benchmark_returns:
            beta = self.calculate_beta(returns, benchmark_returns)

        return RiskMetrics(
            var_95=self.calculate_var(returns, 0.95),
            var_99=self.calculate_var(returns, 0.99),
            cvar_95=self.calculate_cvar(returns, 0.95),
            cvar_99=self.calculate_cvar(returns, 0.99),
            volatility=self.calculate_volatility(returns),
            max_drawdown=self.calculate_max_drawdown(prices),
            sharpe_ratio=self.calculate_sharpe_ratio(returns, risk_free_rate),
            beta=beta
        )


class PortfolioOptimizationService:
    """
    Domain Service para otimização de portfólio.
    """

    def calculate_efficient_frontier(
        self,
        returns_matrix: np.ndarray,
        num_points: int = 50
    ) -> List[Dict]:
        """
        Calcula pontos da fronteira eficiente.
        
        Returns:
            Lista de dicionários com {return, volatility, sharpe, weights}
        """
        from scipy.optimize import minimize

        n_assets = returns_matrix.shape[0]
        mean_returns = np.mean(returns_matrix, axis=1) * 252
        cov_matrix = np.cov(returns_matrix) * 252

        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        def portfolio_return(weights):
            return np.dot(weights, mean_returns)

        # Restrições: soma dos pesos = 1, pesos >= 0
        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))

        # Encontra retornos mínimo e máximo
        min_ret_result = minimize(
            lambda w: -portfolio_return(w),
            np.ones(n_assets) / n_assets,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        max_ret = -min_ret_result.fun

        min_vol_result = minimize(
            portfolio_volatility,
            np.ones(n_assets) / n_assets,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        min_ret = portfolio_return(min_vol_result.x)

        # Gera pontos na fronteira
        target_returns = np.linspace(min_ret, max_ret, num_points)
        frontier_points = []

        for target_ret in target_returns:
            constraints_with_return = [
                {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
                {'type': 'eq', 'fun': lambda w, r=target_ret: portfolio_return(w) - r}
            ]
            
            result = minimize(
                portfolio_volatility,
                np.ones(n_assets) / n_assets,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_with_return
            )
            
            if result.success:
                vol = portfolio_volatility(result.x)
                ret = portfolio_return(result.x)
                sharpe = ret / vol if vol > 0 else 0
                
                frontier_points.append({
                    'return': float(ret),
                    'volatility': float(vol),
                    'sharpe': float(sharpe),
                    'weights': result.x.tolist()
                })

        return frontier_points

    def optimize_max_sharpe(
        self,
        returns_matrix: np.ndarray,
        risk_free_rate: float = 0.0
    ) -> Tuple[np.ndarray, float]:
        """
        Encontra o portfólio com máximo Sharpe ratio.
        
        Returns:
            Tuple de (pesos, sharpe_ratio)
        """
        from scipy.optimize import minimize

        n_assets = returns_matrix.shape[0]
        mean_returns = np.mean(returns_matrix, axis=1) * 252
        cov_matrix = np.cov(returns_matrix) * 252

        def neg_sharpe(weights):
            ret = np.dot(weights, mean_returns)
            vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return -(ret - risk_free_rate) / vol if vol > 0 else 0

        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))

        result = minimize(
            neg_sharpe,
            np.ones(n_assets) / n_assets,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return result.x, -result.fun

    def optimize_min_volatility(
        self,
        returns_matrix: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """
        Encontra o portfólio de mínima variância.
        
        Returns:
            Tuple de (pesos, volatilidade)
        """
        from scipy.optimize import minimize

        n_assets = returns_matrix.shape[0]
        cov_matrix = np.cov(returns_matrix) * 252

        def portfolio_volatility(weights):
            return np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))

        result = minimize(
            portfolio_volatility,
            np.ones(n_assets) / n_assets,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return result.x, result.fun


class CDICashService:
    """
    Domain Service para cálculo de rendimento do caixa pelo CDI.
    """

    def calculate_daily_return(
        self,
        principal: Money,
        daily_cdi_rate: float
    ) -> Money:
        """
        Calcula o rendimento diário do CDI.
        
        Args:
            principal: Valor principal
            daily_cdi_rate: Taxa CDI diária (decimal)
        """
        daily_return = principal.amount * Decimal(str(daily_cdi_rate))
        return Money(daily_return, principal.currency)

    def calculate_period_return(
        self,
        principal: Money,
        cdi_rates: Dict[date, float]
    ) -> Tuple[Money, Money]:
        """
        Calcula o valor final e rendimento total para um período.
        
        Args:
            principal: Valor inicial
            cdi_rates: Dicionário data -> taxa CDI diária
            
        Returns:
            Tuple de (valor_final, rendimento_total)
        """
        accumulated = principal.amount
        
        for rate in cdi_rates.values():
            accumulated *= Decimal(1 + rate)
        
        final_value = Money(accumulated, principal.currency)
        total_return = Money(accumulated - principal.amount, principal.currency)
        
        return final_value, total_return

    def annualize_rate(self, daily_rate: float) -> float:
        """Converte taxa diária para anual."""
        return (1 + daily_rate) ** 252 - 1

    def daily_from_annual(self, annual_rate: float) -> float:
        """Converte taxa anual para diária."""
        return (1 + annual_rate) ** (1/252) - 1
