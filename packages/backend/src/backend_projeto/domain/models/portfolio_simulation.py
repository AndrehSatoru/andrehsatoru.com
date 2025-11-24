from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class TradeOrder(BaseModel):
    asset: str
    type: OrderType
    quantity: float
    date: date
    price: Optional[float] = None

class PortfolioSimulationRequest(BaseModel):
    initialInvestment: float
    startDate: date
    endDate: date
    orders: List[TradeOrder]

class PortfolioValue(BaseModel):
    date: date
    value: float

class HoldingInfo(BaseModel):
    asset: str
    quantity: float
    currentValue: float
    weight: float
    return_: float

class PortfolioPerformance(BaseModel):
    totalReturn: float
    annualizedReturn: float
    maxDrawdown: float
    volatility: float
    sharpeRatio: float

class PortfolioSimulationResponse(BaseModel):
    portfolioValue: List[PortfolioValue]
    performance: PortfolioPerformance
    holdings: List[HoldingInfo]
    transactions: List[TradeOrder]