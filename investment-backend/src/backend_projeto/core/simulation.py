# simulation.py

import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from .data_handling import DataLoader, DataCleaner
from ..utils.config import Config

try:
    from arch import arch_model
except Exception:
    arch_model = None


def _ewma_vol(returns: np.ndarray, lam: float = 0.94) -> float:
    if returns.size == 0:
        return 0.0
    var = np.var(returns)
    for r in returns:
        var = lam * var + (1 - lam) * (r ** 2)
    return float(np.sqrt(var))


@dataclass
class MonteCarloEngine:
    loader: DataLoader
    config: Config

    def _portfolio_returns(self, prices: pd.DataFrame, assets: List[str], weights: Optional[List[float]]) -> pd.Series:
        from .analysis import compute_returns, portfolio_returns
        rets = compute_returns(prices)
        return portfolio_returns(rets, assets, weights)

    def _estimate_params(self, r: pd.Series, vol_method: str = 'std', ewma_lambda: float = 0.94) -> Dict:
        mu = float(r.mean())
        if vol_method == 'std':
            sigma = float(r.std(ddof=1))
        elif vol_method == 'ewma':
            sigma = _ewma_vol(r.fillna(0.0).values, lam=ewma_lambda)
        elif vol_method == 'garch':
            if arch_model is None:
                raise RuntimeError("Pacote 'arch' não disponível para vol_method=garch")
            am = arch_model(r.dropna() * 100, vol='GARCH', p=1, q=1, dist='normal')
            res = am.fit(disp='off')
            sigma = float(res.conditional_volatility.iloc[-1] / 100.0)
        else:
            raise ValueError("vol_method deve ser std|ewma|garch")
        return {"mu": mu, "sigma": sigma}

    def simulate_gbm(self, assets: List[str], start_date: str, end_date: str, weights: Optional[List[float]], n_paths: int, n_days: int, vol_method: str = 'std', ewma_lambda: float = 0.94, seed: Optional[int] = None) -> Dict:
        prices = self.loader.fetch_stock_prices(assets, start_date, end_date)
        r = self._portfolio_returns(prices, assets, weights)
        params = self._estimate_params(r, vol_method=vol_method, ewma_lambda=ewma_lambda)
        mu, sigma = params["mu"], params["sigma"]
        if seed is not None:
            np.random.seed(seed)
        dt = 1.0 / self.config.DIAS_UTEIS_ANO
        # Simulação de retornos diários (aproximação normal)
        shocks = np.random.normal((mu - 0.5 * sigma ** 2) * dt, sigma * np.sqrt(dt), size=(n_days, n_paths))
        # Trajetórias de preço baseadas em retorno cumulativo (assumindo preço inicial = 1)
        prices_paths = np.exp(np.cumsum(shocks, axis=0))
        terminal = prices_paths[-1, :]
        # Distribuição de PnL como retorno final da carteira
        pnl = terminal - 1.0
        # Métricas de risco da simulação
        var_sim = float(-np.quantile(pnl, 1 - self.config.VAR_CONFIDENCE_LEVEL))
        tail = pnl[pnl <= np.quantile(pnl, 1 - self.config.VAR_CONFIDENCE_LEVEL)]
        es_sim = float(-tail.mean()) if tail.size > 0 else 0.0
        return {
            "params": {"mu": mu, "sigma": sigma, "vol_method": vol_method},
            "var": var_sim,
            "es": es_sim,
            "confidence": self.config.VAR_CONFIDENCE_LEVEL,
            "n_paths": n_paths,
            "n_days": n_days,
        }


class PortfolioSimulator:
    def __init__(self, transactions_df: pd.DataFrame, data_loader: DataLoader, config: Config, data_cleaner: Optional[DataCleaner] = None):
        self.transactions = transactions_df.set_index('Data')
        self.start_date = self.transactions.index.min()
        self.end_date = pd.to_datetime(config.DATA_FINAL_SIMULACAO)
        self.assets = self.transactions['Ativo'].dropna().unique().tolist()
        self.data_loader = data_loader
        self.data_cleaner = data_cleaner
        self.config = config
        self.initial_capital = config.CAPITAL_INICIAL
        self.slippage_percentual = config.SLIPPAGE_PERCENTUAL
        self.portfolio_history = pd.DataFrame()
        self.quotes_history = pd.DataFrame()
        self.cdi_data = pd.DataFrame()
        self.pending_settlements: Dict[pd.Timestamp, float] = {}
        logging.info(f"PortfolioSimulator inicializado com slippage de {self.slippage_percentual:.4%}.")

    # Pontos de extensão futuros para simulação de carteira baseadas em transações
