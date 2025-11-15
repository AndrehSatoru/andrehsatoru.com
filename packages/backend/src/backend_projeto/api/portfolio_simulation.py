"""
This module defines FastAPI endpoints for portfolio simulation.

It provides a route to simulate portfolio performance over time based on an
initial investment and a series of trading orders (buy/sell).
It also includes helper functions for calculating daily portfolio values and
various performance metrics.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from backend_projeto.core.data_handling import YFinanceProvider
from backend_projeto.core.analysis import compute_returns, portfolio_returns, drawdown
from .models.portfolio_simulation import (
    PortfolioSimulationRequest,
    PortfolioSimulationResponse,
    PortfolioValue,
    HoldingInfo,
    PortfolioPerformance,
    TradeOrder
)
from .deps import get_loader

router = APIRouter()

def calculate_portfolio_values(
    prices: pd.DataFrame,
    initial_investment: float,
    orders: List[TradeOrder]
) -> pd.Series:
    """
    Calculate daily portfolio values based on trades and market prices.

    Args:
        prices (pd.DataFrame): DataFrame of asset prices with a DatetimeIndex.
        initial_investment (float): The initial capital for the portfolio.
        orders (List[TradeOrder]): A list of trade orders to execute.

    Returns:
        pd.Series: A Series representing the daily total value of the portfolio.

    Raises:
        HTTPException: 400 if there are insufficient funds for a buy order
                       or insufficient shares for a sell order.
    """
    portfolio = pd.DataFrame(0, index=prices.index, columns=prices.columns)
    cash = pd.Series(initial_investment, index=prices.index)
    
    # Process orders chronologically
    sorted_orders = sorted(orders, key=lambda x: x.date)
    
    for order in sorted_orders:
        # Find the first valid date on or after the order date
        exec_date = prices.index[prices.index >= pd.Timestamp(order.date)][0]
        
        asset_price = prices.loc[exec_date, order.asset]
        order_value = order.quantity * (order.price or asset_price)
        
        if order.type == "BUY":
            if cash[exec_date] < order_value:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient funds for order on {order.date}: needed {order_value}, had {cash[exec_date]}"
                )
            portfolio.loc[exec_date:, order.asset] += order.quantity
            cash.loc[exec_date:] -= order_value
        else:  # SELL
            if portfolio.loc[exec_date, order.asset] < order.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient {order.asset} shares for sell order on {order.date}"
                )
            portfolio.loc[exec_date:, order.asset] -= order.quantity
            cash.loc[exec_date:] += order_value
    
    # Calculate daily portfolio values
    portfolio_values = (portfolio * prices).sum(axis=1) + cash
    return portfolio_values

def calculate_performance_metrics(portfolio_values: pd.Series) -> PortfolioPerformance:
    """
    Calculate portfolio performance metrics.

    Args:
        portfolio_values (pd.Series): A Series representing the daily total value of the portfolio.

    Returns:
        PortfolioPerformance: A Pydantic model containing various performance metrics.
    """
    returns = portfolio_values.pct_change().dropna()
    total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1
    
    # Annualized metrics
    trading_days = len(returns)
    years = trading_days / 252
    annualized_return = (1 + total_return) ** (1/years) - 1
    
    volatility = returns.std() * np.sqrt(252)
    max_dd = drawdown(portfolio_values).min()
    
    # Sharpe ratio (assuming risk-free rate of 4.5%)
    risk_free_rate = 0.045
    excess_returns = returns - risk_free_rate/252
    sharpe_ratio = np.sqrt(252) * excess_returns.mean() / returns.std()
    
    return PortfolioPerformance(
        totalReturn=total_return,
        annualizedReturn=annualized_return,
        maxDrawdown=max_dd,
        volatility=volatility,
        sharpeRatio=sharpe_ratio
    )

@router.post("/portfolio/simulate", response_model=PortfolioSimulationResponse, tags=["Portfolio"])
async def simulate_portfolio(
    req: PortfolioSimulationRequest,
    loader: YFinanceProvider = Depends(get_loader)
) -> PortfolioSimulationResponse:
    """
    Simulate portfolio performance based on initial investment and trading orders.

    Args:
        req (PortfolioSimulationRequest): Request body containing initial investment,
                                          start date, end date, and a list of trade orders.
        loader (YFinanceProvider): Dependency injection for the data loader.

    Returns:
        PortfolioSimulationResponse: A Pydantic model containing the simulated portfolio's
                                     value history, performance metrics, final holdings, and transactions.

    Raises:
        HTTPException: 404 if no price data is found for the given assets and date range,
                       500 for other internal server errors during simulation.
    """
    try:
        # Get unique assets from orders
        assets = list({order.asset for order in req.orders})
        
        # Fetch price data
        prices = loader.fetch_stock_prices(assets, req.startDate, req.endDate)
        if prices.empty:
            raise HTTPException(
                status_code=404,
                detail="No price data found for the given assets and date range"
            )
        
        # Calculate portfolio values
        portfolio_values = calculate_portfolio_values(prices, req.initialInvestment, req.orders)
        
        # Calculate final holdings
        final_holdings = []
        portfolio_value = portfolio_values.iloc[-1]
        
        for asset in assets:
            quantity = sum(
                order.quantity * (1 if order.type == "BUY" else -1)
                for order in req.orders
                if order.asset == asset
            )
            if quantity > 0:
                current_price = prices[asset].iloc[-1]
                current_value = quantity * current_price
                asset_return = (current_price / prices[asset].iloc[0]) - 1
                
                final_holdings.append(HoldingInfo(
                    asset=asset,
                    quantity=quantity,
                    currentValue=current_value,
                    weight=current_value / portfolio_value,
                    return_=asset_return
                ))
        
        # Prepare response
        portfolio_value_series = [
            PortfolioValue(date=date, value=value)
            for date, value in portfolio_values.items()
        ]
        
        performance = calculate_performance_metrics(portfolio_values)
        
        return PortfolioSimulationResponse(
            portfolioValue=portfolio_value_series,
            performance=performance,
            holdings=final_holdings,
            transactions=req.orders
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error simulating portfolio: {str(e)}"
        )