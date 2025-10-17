# optimization.py

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
from ..utils.config import Config
from .data_handling import DataLoader
from numpy.linalg import lstsq
from scipy.optimize import minimize


def _returns_from_prices(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.sort_index().pct_change().dropna(how='all')


def _annualize_mean_cov(rets: pd.DataFrame, dias_uteis: int) -> Tuple[np.ndarray, np.ndarray]:
    mu = rets.mean().values * dias_uteis
    cov = rets.cov().values * dias_uteis
    return mu, cov


@dataclass
class OptimizationEngine:
    loader: DataLoader
    config: Config

    def load_prices(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        return self.loader.fetch_stock_prices(assets, start_date, end_date)

    # Markowitz
    def optimize_markowitz(self, assets: List[str], start_date: str, end_date: str, objective: str = 'max_sharpe', bounds: Optional[List[Tuple[float,float]]] = None, long_only: bool = True, max_weight: Optional[float] = None) -> Dict:
        prices = self.load_prices(assets, start_date, end_date)
        rets = _returns_from_prices(prices)[assets].dropna()
        if rets.shape[1] < 2:
            raise ValueError("São necessários pelo menos 2 ativos para otimização")
        mu, cov = _annualize_mean_cov(rets, self.config.DIAS_UTEIS_ANO)
        n = len(assets)
        if bounds is None:
            if long_only:
                lower = 0.0
            else:
                lower = -1.0
            upper = 1.0 if max_weight is None else max_weight
            bounds = [(lower, upper) for _ in range(n)]
        rf = 0.0  # usar taxa livre anual já embutida opcionalmente; mantemos 0 para simplicidade

        def portfolio_stats(w):
            w = np.array(w)
            ret = w @ mu
            vol = float(np.sqrt(max(w @ cov @ w, 0)))
            sharpe = (ret - rf) / (vol + 1e-12)
            return ret, vol, sharpe

        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},)
        x0 = np.ones(n) / n

        if objective == 'min_var':
            fun = lambda w: w @ cov @ w
        elif objective == 'max_return':
            fun = lambda w: -(w @ mu)
        else:  # max_sharpe
            fun = lambda w: -((w @ mu - rf) / (np.sqrt(max(w @ cov @ w, 0)) + 1e-12))

        res = minimize(fun, x0, bounds=bounds, constraints=cons, method='SLSQP', options={'maxiter': 100})
        w_opt = res.x
        ret, vol, sharpe = portfolio_stats(w_opt)
        return {
            'weights': {assets[i]: float(w_opt[i]) for i in range(n)},
            'ret_annual': float(ret),
            'vol_annual': float(vol),
            'sharpe': float(sharpe),
            'objective': objective,
            'success': bool(res.success),
            'message': res.message,
        }

    # CAPM: beta/alpha vs benchmark
    def capm_metrics(self, assets: List[str], start_date: str, end_date: str, benchmark_ticker: str) -> Dict:
        prices = self.load_prices(assets, start_date, end_date)
        bench_series = self.loader.fetch_benchmark_data(benchmark_ticker, start_date, end_date)
        if bench_series is None:
            raise ValueError("Benchmark sem dados")
        df = prices.join(bench_series.rename('BENCH'), how='inner')
        rets = _returns_from_prices(df)
        results = {}
        rb = rets['BENCH'].values.reshape(-1, 1)
        X = np.column_stack([np.ones(rb.shape[0]), rb])
        for a in assets:
            if a not in rets.columns:
                continue
            y = rets[a].values
            beta_params, *_ = lstsq(X, y, rcond=None)
            alpha, beta = beta_params[0], beta_params[1]
            # estatísticas simples
            y_hat = X @ beta_params
            resid = y - y_hat
            ss_res = float(np.sum(resid**2))
            ss_tot = float(np.sum((y - np.mean(y))**2))
            r2 = 0.0 if ss_tot == 0 else 1 - ss_res/ss_tot
            results[a] = {'alpha': float(alpha), 'beta': float(beta), 'r2': float(r2)}
        return {'benchmark': benchmark_ticker, 'metrics': results}

    # APT: regressão multifatores (factors como tickers)
    def apt_metrics(self, assets: List[str], start_date: str, end_date: str, factors: List[str]) -> Dict:
        prices_assets = self.load_prices(assets, start_date, end_date)
        prices_factors = self.load_prices(factors, start_date, end_date)
        df = prices_assets.join(prices_factors, how='inner', lsuffix='', rsuffix='_F')
        rets = _returns_from_prices(df)
        # separa colunas
        factor_cols = [c for c in rets.columns if c in factors]
        X = rets[factor_cols].values
        X = np.column_stack([np.ones(X.shape[0]), X])
        results = {}
        for a in assets:
            if a not in rets.columns:
                continue
            y = rets[a].values
            coeffs, *_ = lstsq(X, y, rcond=None)
            alpha = coeffs[0]
            betas = coeffs[1:].tolist()
            y_hat = X @ coeffs
            resid = y - y_hat
            ss_res = float(np.sum(resid**2))
            ss_tot = float(np.sum((y - np.mean(y))**2))
            r2 = 0.0 if ss_tot == 0 else 1 - ss_res/ss_tot
            results[a] = {'alpha': float(alpha), 'betas': betas, 'factors': factor_cols, 'r2': float(r2)}
        return {'metrics': results}

    # Black-Litterman simplificado
    def black_litterman(self, assets: List[str], start_date: str, end_date: str, market_caps: Dict[str, float], views: List[Dict], tau: float = 0.05) -> Dict:
        prices = self.load_prices(assets, start_date, end_date)
        rets = _returns_from_prices(prices)[assets].dropna()
        mu, Sigma = _annualize_mean_cov(rets, self.config.DIAS_UTEIS_ANO)
        assets_idx = {a: i for i, a in enumerate(assets)}
        # Pesos de equilíbrio proporcionais ao market cap
        caps = np.array([float(market_caps.get(a, 0.0)) for a in assets])
        if caps.sum() <= 0:
            w_mkt = np.ones(len(assets)) / len(assets)
        else:
            w_mkt = caps / caps.sum()
        # world implied returns (simplificado): pi = delta * Sigma * w_mkt, com delta=1
        pi = Sigma @ w_mkt
        # Views: lista de dicts {"assets": [..], "weights": [..], "view": retorno_esperado}
        P_list = []
        Q_list = []
        for v in views:
            aset = v.get('assets', [])
            wv = np.array(v.get('weights', []), dtype=float)
            row = np.zeros(len(assets))
            for ai, aw in zip(aset, wv):
                if ai in assets_idx:
                    row[assets_idx[ai]] = aw
            P_list.append(row)
            Q_list.append(float(v.get('view', 0.0)))
        if not P_list:
            # Sem views -> retorna equilíbrio
            w_eq = w_mkt
            return {'weights': {assets[i]: float(w_eq[i]) for i in range(len(assets))}, 'pi': pi.tolist(), 'tau': tau, 'views': []}
        P = np.vstack(P_list)
        Q = np.array(Q_list)
        # Incerteza das views Omega (proporcional à variância projetada)
        Omega = np.diag(np.diag(P @ (tau * Sigma) @ P.T))
        # Posterior de Black-Litterman
        # mu_BL = [(tau*Sigma)^-1 + P^T Omega^-1 P]^-1 [ (tau*Sigma)^-1 pi + P^T Omega^-1 Q ]
        tauSigma_inv = np.linalg.inv(tau * Sigma)
        middle = tauSigma_inv + P.T @ np.linalg.inv(Omega) @ P
        mu_bl = np.linalg.inv(middle) @ (tauSigma_inv @ pi + P.T @ np.linalg.inv(Omega) @ Q)
        # pesos ótimos com média-variância (delta=1)
        w_bl = np.linalg.inv(Sigma) @ mu_bl
        w_bl = w_bl / w_bl.sum()
        return {
            'weights': {assets[i]: float(w_bl[i]) for i in range(len(assets))},
            'pi': pi.tolist(),
            'mu_bl': mu_bl.tolist(),
            'tau': tau,
            'views': views,
        }
