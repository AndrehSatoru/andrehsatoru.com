"""
This module provides functionalities for simulating portfolio operations based on buy/sell orders.

It includes the `PortfolioSimulator` class which allows users to:
- Simulate the evolution of a portfolio over time given an initial investment and a series of orders.
- Calculate portfolio value, positions, and performance metrics.
- Determine current holdings and their respective weights and returns.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, date
from backend_projeto.utils.config import Settings
from backend_projeto.core.data_handling import YFinanceProvider
from backend_projeto.core.analysis import compute_returns, portfolio_returns, drawdown

@dataclass
class PortfolioSimulator:
    """
    Classe responsável por simular operações de portfólio com base em ordens de compra/venda.
    """
    data_loader: YFinanceProvider
    config: Settings

    def simulate_portfolio(
        self,
        initial_investment: float,
        start_date: date,
        end_date: date,
        orders: List[Dict]
    ) -> Tuple[pd.Series, pd.DataFrame, Dict]:
        """
        Simulates the evolution of a portfolio based on an initial investment and a list of buy/sell orders.

        Args:
            initial_investment (float): The initial capital for the simulation.
            start_date (date): The start date of the simulation.
            end_date (date): The end date of the simulation.
            orders (List[Dict]): A list of order dictionaries. Each dictionary should contain:
                                 - 'asset' (str): The asset ticker.
                                 - 'type' (str): 'BUY' or 'SELL'.
                                 - 'quantity' (float): The quantity of the asset.
                                 - 'date' (str): The date of the order (YYYY-MM-DD).
                                 - 'price' (Optional[float]): The execution price. If None, market price is used.

        Returns:
            Tuple[pd.Series, pd.DataFrame, Dict]: A tuple containing:
                                                  - pd.Series: Time series of the portfolio's total value.
                                                  - pd.DataFrame: DataFrame with asset positions over time.
                                                  - Dict: Dictionary of performance metrics.

        Raises:
            ValueError: If no price data can be obtained for the selected assets,
                        or if there are insufficient funds for a buy order,
                        or insufficient position for a sell order.
        """
        # Ordenar ordens por data
        sorted_orders = sorted(orders, key=lambda x: x['date'])

        # Obter lista única de ativos
        assets = list({order['asset'] for order in sorted_orders})

        # Buscar dados de preços
        prices = self.data_loader.fetch_stock_prices(
            assets=assets,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        if prices.empty:
            raise ValueError("Não foi possível obter dados de preços para os ativos selecionados")

        # Inicializar posições e caixa
        positions = pd.DataFrame(0.0, index=prices.index, columns=assets)
        cash = pd.Series(initial_investment, index=prices.index)

        # Processar ordens
        for order in sorted_orders:
            exec_date = prices.index[prices.index >= pd.Timestamp(order['date'])][0]
            asset = order['asset']
            quantity = order['quantity']
            
            # Usar preço fornecido ou preço de mercado
            price = order.get('price') or prices.loc[exec_date, asset]
            order_value = quantity * price

            if order['type'].upper() == 'BUY':
                if cash[exec_date] < order_value:
                    raise ValueError(f"Fundos insuficientes para ordem em {order['date']}")
                positions.loc[exec_date:, asset] += quantity
                cash.loc[exec_date:] -= order_value
            else:  # SELL
                if positions.loc[exec_date, asset] < quantity:
                    raise ValueError(f"Posição insuficiente em {asset} para venda em {order['date']}")
                positions.loc[exec_date:, asset] -= quantity
                cash.loc[exec_date:] += order_value

        # Calcular valor total do portfólio ao longo do tempo
        portfolio_value = pd.Series(0.0, index=prices.index, name='portfolio_value')
        for asset in assets:
            portfolio_value += positions[asset] * prices[asset]
        portfolio_value += cash

        # Calcular métricas de performance
        returns = portfolio_value.pct_change().dropna()
        total_return = (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) - 1
        
        # Métricas anualizadas
        trading_days = len(returns)
        years = trading_days / 252
        annualized_return = (1 + total_return) ** (1/years) - 1
        
        volatility = returns.std() * np.sqrt(252)
        max_dd = drawdown(portfolio_value).min()
        
        # Índice Sharpe (assumindo taxa livre de risco de 4.5%)
        risk_free_rate = self.config.RISK_FREE_RATE
        excess_returns = returns - risk_free_rate/252
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / returns.std()

        performance_metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'max_drawdown': max_dd,
            'sharpe_ratio': sharpe_ratio,
            'risk_free_rate': risk_free_rate
        }

        return portfolio_value, positions, performance_metrics

    def calculate_current_holdings(
        self,
        positions: pd.DataFrame,
        prices: pd.DataFrame,
        total_value: float
    ) -> List[Dict]:
        """
        Calculates the current holdings of the portfolio, including quantity, value, weight, and return for each asset.

        Args:
            positions (pd.DataFrame): DataFrame containing asset positions over time.
            prices (pd.DataFrame): DataFrame containing asset prices.
            total_value (float): The current total value of the portfolio.

        Returns:
            List[Dict]: A list of dictionaries, where each dictionary represents an asset holding
                        with details like 'asset', 'quantity', 'current_value', 'weight', and 'return'.
        """
        holdings = []
        last_date = positions.index[-1]

        for asset in positions.columns:
            quantity = positions.loc[last_date, asset]
            if quantity > 0:
                current_price = prices.loc[last_date, asset]
                current_value = quantity * current_price
                weight = current_value / total_value

                # Calcular retorno do ativo
                first_price = prices.loc[positions.index[0], asset]
                asset_return = (current_price / first_price) - 1

                holdings.append({
                    'asset': asset,
                    'quantity': quantity,
                    'current_value': current_value,
                    'weight': weight,
                    'return': asset_return
                })

        return holdings