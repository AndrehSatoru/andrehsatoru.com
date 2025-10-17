# analysis.py

import pandas as pd
import numpy as np
import statsmodels.api as sm
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from .data_handling import DataLoader
from ..utils.config import Config

try:
    from arch import arch_model
except Exception:  # pacote opcional, lidamos quando método for garch
    arch_model = None


def _as_weights(assets: List[str], weights: Optional[List[float]]) -> np.ndarray:
    if not weights:
        return np.ones(len(assets)) / len(assets)
    w = np.array(weights, dtype=float)
    if len(w) != len(assets):
        raise ValueError("Tamanho de weights difere do número de assets")
    s = w.sum()
    if s == 0:
        raise ValueError("Soma dos pesos não pode ser zero")
    return w / s


def compute_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    r = price_df.sort_index().pct_change().dropna(how='all')
    return r.replace([np.inf, -np.inf], np.nan).dropna(how='all')


def portfolio_returns(returns_df: pd.DataFrame, assets: List[str], weights: Optional[List[float]]) -> pd.Series:
    sel = [a for a in assets if a in returns_df.columns]
    if not sel:
        raise ValueError("Nenhum ativo encontrado em returns_df")
    w = _as_weights(sel, weights if weights and len(weights) == len(assets) else None)
    X = returns_df[sel].copy()
    # Renormaliza pesos por data considerando apenas ativos com retorno disponível
    w_series = pd.Series(w, index=sel)
    mask = X.notna()
    w_masked = mask.mul(w_series, axis=1)
    row_sum = w_masked.sum(axis=1).replace(0.0, np.nan)
    w_norm = w_masked.div(row_sum, axis=0).fillna(0.0)
    port = (X.fillna(0.0) * w_norm).sum(axis=1)
    port.name = 'portfolio'
    return port


def var_parametric(returns: pd.Series, alpha: float = 0.99, method: str = 'std', ewma_lambda: float = 0.94) -> Tuple[float, Dict]:
    """VaR Paramétrico assumindo distribuição normal (ou GARCH condicional).

    IMPORTANTE: Assume normalidade dos retornos. Para distribuições com caudas pesadas,
    considere usar método EVT.

    Métodos:
        - 'std': volatilidade histórica (desvio padrão amostral).
        - 'ewma': volatilidade EWMA (Exponentially Weighted Moving Average).
        - 'garch': volatilidade condicional via GARCH(1,1).

    Parâmetros:
        returns: Série de retornos.
        alpha: Nível de confiança.
        method: 'std' | 'ewma' | 'garch'.
        ewma_lambda: Fator de decaimento EWMA (padrão 0.94, RiskMetrics usa 0.94).

    Retorna:
        (var_value, details) onde details contém {'mu', 'sigma', 'z', 'method', 'ewma_lambda'}.
    """
    mu = float(returns.mean())
    if method == 'std':
        sigma = float(returns.std(ddof=1))
    elif method == 'ewma':
        lam = ewma_lambda
        # EWMA volatility
        x = returns.fillna(0.0).values
        var = np.var(x) if len(x) > 1 else 0.0
        for xi in x:
            var = lam * var + (1 - lam) * (xi ** 2)
        sigma = float(np.sqrt(var))
    elif method == 'garch':
        if arch_model is None:
            raise RuntimeError("Pacote 'arch' não disponível para método garch")
        am = arch_model(returns.dropna() * 100, vol='GARCH', p=1, q=1, dist='normal')
        res = am.fit(disp='off')
        sigma = float(res.conditional_volatility.iloc[-1] / 100.0)
    else:
        raise ValueError("method deve ser std|ewma|garch")
    from scipy.stats import norm
    z = float(norm.ppf(1 - alpha))  # VaR é quantil da cauda esquerda (negativa)
    var_value = -(mu + z * sigma)
    details = {"mu": mu, "sigma": sigma, "z": z, "method": method}
    if method == 'ewma':
        details["ewma_lambda"] = ewma_lambda
    return float(var_value), details


def es_parametric(returns: pd.Series, alpha: float = 0.99, method: str = 'std', ewma_lambda: float = 0.94) -> Tuple[float, Dict]:
    """Expected Shortfall (CVaR) Paramétrico.

    IMPORTANTE: Assume normalidade. ES é a média das perdas além do VaR.

    Fórmula (distribuição normal):
        ES = μ - σ * φ(z) / (1 - α)
        onde φ é a PDF da normal padrão e z = Φ^(-1)(1 - α).

    Parâmetros:
        returns: Série de retornos.
        alpha: Nível de confiança.
        method: 'std' | 'ewma' | 'garch'.
        ewma_lambda: Fator de decaimento EWMA.

    Retorna:
        (es_value, details).
    """
    mu = float(returns.mean())
    if method in ('std', 'ewma', 'garch'):
        v, d = var_parametric(returns, alpha=alpha, method=method, ewma_lambda=ewma_lambda)
        sigma = d["sigma"]
        from scipy.stats import norm
        z = float(norm.ppf(1 - alpha))
        es = -(mu - sigma * norm.pdf(z) / (1 - alpha))
        d.update({"z": z})
        return float(es), d
    raise ValueError("method deve ser std|ewma|garch")


def var_historical(returns: pd.Series, alpha: float = 0.99) -> Tuple[float, Dict]:
    q = float(np.nanquantile(returns.values, 1 - alpha))
    return float(-q), {"quantile": q}


def es_historical(returns: pd.Series, alpha: float = 0.99) -> Tuple[float, Dict]:
    q = np.nanquantile(returns.values, 1 - alpha)
    tail = returns[returns <= q]
    es = -float(tail.mean()) if not tail.empty else 0.0
    return es, {"threshold": float(q), "n_tail": int(tail.shape[0])}


# EVT (GPD) na cauda das perdas
def var_evt(returns: pd.Series, alpha: float = 0.99, threshold_quantile: float = 0.9) -> Tuple[float, Dict]:
    # Trabalhamos com perdas L = -R
    from scipy.stats import genpareto
    losses = (-returns).dropna().values
    if losses.size < 50:
        # fallback para histórico
        v, d = var_historical(returns, alpha)
        d.update({"fallback": "historical"})
        return v, d
    u = float(np.quantile(losses, threshold_quantile))
    excess = losses[losses > u] - u
    if excess.size < 30:
        v, d = var_historical(returns, alpha)
        d.update({"fallback": "historical"})
        return v, d
    # Ajuste GPD via MLE
    c, loc, scale = genpareto.fit(excess, floc=0.0)
    # Probabilidade condicional na cauda acima de u
    p_tail = 1 - threshold_quantile
    # Quantil alvo para a cauda usando a fórmula do quantil GPD
    # VaR em perdas: q_alpha = u + (scale/c) * ((p_tail/(1-alpha))**c - 1) se c != 0
    if abs(c) > 1e-8:
        q_loss = u + (scale / c) * (((p_tail) / (1 - alpha))**c - 1.0)
    else:
        q_loss = u + scale * np.log(p_tail / (1 - alpha))
    var_value = float(q_loss)  # em perdas
    return var_value, {"xi": float(c), "beta": float(scale), "u": u, "p_tail": p_tail}


def es_evt(returns: pd.Series, alpha: float = 0.99, threshold_quantile: float = 0.9) -> Tuple[float, Dict]:
    from scipy.stats import genpareto
    losses = (-returns).dropna().values
    if losses.size < 50:
        v, d = es_historical(returns, alpha)
        d.update({"fallback": "historical"})
        return v, d
    u = float(np.quantile(losses, threshold_quantile))
    excess = losses[losses > u] - u
    if excess.size < 30:
        v, d = es_historical(returns, alpha)
        d.update({"fallback": "historical"})
        return v, d
    c, loc, scale = genpareto.fit(excess, floc=0.0)
    p_tail = 1 - threshold_quantile
    # ES para GPD (perdas): ES = (VaR + (scale - c * u)) / (1 - c) aproximadamente sobre a cauda
    # Usamos fórmula: ES = (q_alpha + (scale - c * (q_alpha - u))) / (1 - c)
    var_loss, det = var_evt(returns, alpha, threshold_quantile)
    if c < 1:
        es_loss = (var_loss + (scale - c * (var_loss - u))) / (1 - c)
    else:
        es_loss = np.inf
    return float(es_loss), {"xi": float(c), "beta": float(scale), "u": u, "p_tail": p_tail, "var_loss": float(var_loss)}


def drawdown(returns: pd.Series) -> Dict:
    equity = (1 + returns.fillna(0)).cumprod()
    peak = equity.cummax()
    dd = (equity / peak) - 1.0
    max_dd = float(dd.min())
    end = dd.idxmin()
    start = (equity.loc[:end]).idxmax()
    return {
        "max_drawdown": max_dd,
        "start": str(start),
        "end": str(end),
    }


def stress_test(returns_df: pd.DataFrame, assets: List[str], weights: Optional[List[float]], shocks_pct: float = -0.1) -> Dict:
    sel = [a for a in assets if a in returns_df.columns]
    w = _as_weights(sel, weights)
    last = returns_df[sel].fillna(0.0).iloc[-1]
    shocked = last + shocks_pct
    pnl = float(np.dot(shocked.values, w))
    return {
        "shock": shocks_pct,
        "portfolio_return": pnl,
        "asset_returns": {a: float(shocked[a]) for a in sel},
    }


def backtest_var(returns: pd.Series, alpha: float, method: str = 'historical', ewma_lambda: float = 0.94) -> Dict:
    # janela rolling simples
    window = 250 if returns.shape[0] > 300 else max(60, int(returns.shape[0] * 0.6))
    exceptions = 0
    n = 0
    for i in range(window, len(returns)):
        hist = returns.iloc[i - window:i]
        r = returns.iloc[i]
        if method == 'historical':
            var_val, _ = var_historical(hist, alpha)
        elif method in ('std', 'ewma', 'garch'):
            var_val, _ = var_parametric(hist, alpha, method=method, ewma_lambda=ewma_lambda)
        elif method == 'evt':
            var_val, _ = var_evt(hist, alpha)
        else:
            raise ValueError("método inválido para backtest")
        # exceção se retorno < -VaR
        if r < -var_val:
            exceptions += 1
        n += 1
    # Teste de Kupiec (POF) aproximado
    if n == 0:
        return {"n": 0, "exceptions": 0, "exception_rate": 0.0}
    p = 1 - alpha
    pi = exceptions / n
    from math import log
    from scipy.stats import chi2, binom
    def L(k, N, p_):
        return (N - k) * log(1 - p_) + k * log(p_) if 0 < p_ < 1 else float('-inf')
    lr = -2 * (L(exceptions, n, p) - L(exceptions, n, pi if 0 < pi < 1 else 1e-9))
    kupiec_pvalue = float(1 - chi2.cdf(lr, df=1))

    # Christoffersen independência: sequência de exceções 00,01,10,11
    hits = (returns.iloc[window:] < -pd.Series([var_historical(returns.iloc[i-window:i], alpha)[0] if method=='historical' else (var_parametric(returns.iloc[i-window:i], alpha, method=method, ewma_lambda=ewma_lambda)[0] if method in ('std','ewma','garch') else var_evt(returns.iloc[i-window:i], alpha)[0]) for i in range(window, len(returns))], index=returns.index[window:])).astype(int)
    n00 = n01 = n10 = n11 = 0
    prev = hits.iloc[0]
    for h in hits.iloc[1:]:
        if prev == 0 and h == 0: n00 += 1
        if prev == 0 and h == 1: n01 += 1
        if prev == 1 and h == 0: n10 += 1
        if prev == 1 and h == 1: n11 += 1
        prev = h
    pi01 = n01 / (n00 + n01) if (n00 + n01) > 0 else 0.0
    pi11 = n11 / (n10 + n11) if (n10 + n11) > 0 else 0.0
    pic = (n01 + n11) / (n00 + n01 + n10 + n11) if (n00 + n01 + n10 + n11) > 0 else 0.0
    from math import log as ln
    Lc = 0.0
    if pi01>0 and pi01<1 and pi11>0 and pi11<1 and pic>0 and pic<1:
        L1 = (n00 * ln(1 - pi01) + n01 * ln(pi01) + n10 * ln(1 - pi11) + n11 * ln(pi11))
        L2 = (n00 + n10) * ln(1 - pic) + (n01 + n11) * ln(pic)
        LRind = -2 * (L2 - L1)
        christoffersen_pvalue = float(1 - chi2.cdf(LRind, df=1))
        LRcc = float(LRind + lr)
        christoffersen_combined_pvalue = float(1 - chi2.cdf(LRcc, df=2))
    else:
        LRind = float('nan')
        christoffersen_pvalue = float('nan')
        christoffersen_combined_pvalue = float('nan')

    # Basel Traffic-Light bands por binomial
    # Limiares aproximados para alpha=0.99; generalizamos por quantis binomiais
    green_upper = int(binom.ppf(0.95, n, p))  # limite superior verde
    amber_upper = int(binom.ppf(0.999, n, p))  # limite superior âmbar
    zone = 'green' if exceptions <= green_upper else ('amber' if exceptions <= amber_upper else 'red')

    return {
        "n": n,
        "exceptions": exceptions,
        "exception_rate": float(pi),
        "kupiec_lr": float(lr),
        "kupiec_pvalue": kupiec_pvalue,
        "christoffersen_lr_ind": float(LRind),
        "christoffersen_pvalue": christoffersen_pvalue,
        "christoffersen_lr_cc": float(LRind + lr) if not np.isnan(LRind) else float('nan'),
        "christoffersen_cc_pvalue": christoffersen_combined_pvalue,
        "basel_zone": zone,
        "alpha": alpha,
        "method": method,
    }


# Covariância (Ledoit-Wolf) e atribuição de risco
def covariance_ledoit_wolf(returns_df: pd.DataFrame) -> Dict:
    try:
        from sklearn.covariance import LedoitWolf
    except Exception as e:
        raise RuntimeError("Pacote sklearn necessário para Ledoit-Wolf") from e
    lw = LedoitWolf().fit(returns_df.dropna())
    cov = lw.covariance_
    shr = float(lw.shrinkage_)
    return {"cov": cov.tolist(), "shrinkage": shr, "columns": list(returns_df.columns)}


def risk_attribution(returns_df: pd.DataFrame, assets: List[str], weights: Optional[List[float]], method: str = 'std', ewma_lambda: float = 0.94) -> Dict:
    sel = [a for a in assets if a in returns_df.columns]
    if not sel:
        raise ValueError("Nenhum ativo válido para atribuição")
    w = _as_weights(sel, weights)
    X = returns_df[sel].dropna()
    # Covariância shrinked
    try:
        from sklearn.covariance import LedoitWolf
        Sigma = LedoitWolf().fit(X).covariance_
    except Exception:
        Sigma = np.cov(X.values, rowvar=False)
    port_var = float(w @ Sigma @ w)
    port_vol = float(np.sqrt(max(port_var, 0)))
    # Marginal Risk (vol)
    mvol = (Sigma @ w) / (port_vol + 1e-12)
    contrib_vol = w * mvol
    # Component VaR (paramétrico)
    if method in ('std', 'ewma'):
        if method == 'ewma':
            lam = ewma_lambda
            # escala port_vol por fator comparável? Manter Sigma já captura covariâncias históricas.
        z = float(__import__('scipy').stats.norm.ppf(0.99))
        mvar = (Sigma @ w) / (port_vol + 1e-12) * z
        contrib_var = (w * mvar).tolist()
    else:
        contrib_var = [float('nan')] * len(sel)
    return {
        "assets": sel,
        "weights": w.tolist(),
        "portfolio_vol": port_vol,
        "contribution_vol": contrib_vol.tolist(),
        "contribution_var": contrib_var,
    }


def incremental_var(
    returns_df: pd.DataFrame,
    assets: List[str],
    weights: Optional[List[float]],
    alpha: float = 0.99,
    method: str = 'historical',
    ewma_lambda: float = 0.94,
    delta: float = 0.01,
) -> Dict:
    """Incremental VaR (IVaR): impacto no VaR ao aumentar ligeiramente o peso de cada ativo.

    O IVaR mede a sensibilidade do VaR da carteira a pequenas mudanças na alocação.
    Para cada ativo i, aumentamos w_i em `delta` e renormalizamos os pesos para somarem 1,
    recalculando o VaR da carteira.

    Fórmula:
        iVaR_i = VaR(w + Δw_i) - VaR(w)
        onde Δw_i = [0, ..., δ, ..., 0] com δ na posição i, seguido de renormalização.

    Parâmetros:
        returns_df: DataFrame com retornos diários por ativo (colunas = ativos).
        assets: Lista de tickers a considerar.
        weights: Pesos da carteira (None = equiponderado).
        alpha: Nível de confiança (ex.: 0.99 para 99%).
        method: 'historical' | 'std' | 'ewma' | 'garch' | 'evt'.
        ewma_lambda: Parâmetro de decaimento para EWMA.
        delta: Incremento aplicado ao peso (padrão 0.01 = 1%).

    Retorna:
        Dict com chaves: 'alpha', 'method', 'delta', 'base_var', 'base_weights', 'ivar' (dict ativo->impacto), 'assets'.

    Exemplo:
        >>> rets = compute_returns(prices)
        >>> res = incremental_var(rets, ['AAPL', 'MSFT'], [0.5, 0.5], alpha=0.99, method='std', delta=0.01)
        >>> print(res['ivar'])
        {'AAPL': 0.0012, 'MSFT': 0.0008}

    Complexidade: O(n * T) onde n = número de ativos, T = tamanho da série temporal.
    """
    sel = [a for a in assets if a in returns_df.columns]
    if not sel:
        raise ValueError("Nenhum ativo válido em returns_df")
    base_w = _as_weights(sel, weights)
    X = returns_df[sel].dropna(how='all').fillna(0.0)
    port_base = pd.Series(X.values @ base_w, index=X.index)
    if method == 'historical':
        base_var, _ = var_historical(port_base, alpha)
    elif method in ('std', 'ewma', 'garch'):
        base_var, _ = var_parametric(port_base, alpha, method=method, ewma_lambda=ewma_lambda)
    elif method == 'evt':
        base_var, _ = var_evt(port_base, alpha)
    else:
        raise ValueError("método inválido para IVaR")

    ivar: Dict[str, float] = {}
    for i, a in enumerate(sel):
        w = base_w.copy()
        w[i] = max(w[i] + delta, 0.0)
        w = w / w.sum()
        port_new = pd.Series(X.values @ w, index=X.index)
        if method == 'historical':
            v, _ = var_historical(port_new, alpha)
        elif method in ('std', 'ewma', 'garch'):
            v, _ = var_parametric(port_new, alpha, method=method, ewma_lambda=ewma_lambda)
        else:
            v, _ = var_evt(port_new, alpha)
        ivar[a] = float(v - base_var)
    return {
        "alpha": alpha,
        "method": method,
        "delta": float(delta),
        "base_var": float(base_var),
        "base_weights": base_w.tolist(),
        "ivar": ivar,
        "assets": sel,
    }


def marginal_var(
    returns_df: pd.DataFrame,
    assets: List[str],
    weights: Optional[List[float]],
    alpha: float = 0.99,
    method: str = 'historical',
    ewma_lambda: float = 0.94,
) -> Dict:
    """Marginal VaR (MVaR): impacto no VaR ao remover completamente cada ativo da carteira.

    O MVaR mede o efeito de remover totalmente a posição de um ativo e renormalizar
    os pesos restantes. Útil para decisões de exclusão de ativos.

    Fórmula:
        MVaR_i = VaR(w_{-i}) - VaR(w)
        onde w_{-i} são os pesos renormalizados após remover o ativo i.

    Nota: Esta implementação remove a posição inteira ("component VaR change").
    Para o MVaR clássico (derivada ∂VaR/∂w_i), use aproximação infinitesimal ou
    método analítico paramétrico.

    Parâmetros:
        returns_df: DataFrame com retornos diários por ativo.
        assets: Lista de tickers.
        weights: Pesos da carteira (None = equiponderado).
        alpha: Nível de confiança.
        method: 'historical' | 'std' | 'ewma' | 'garch' | 'evt'.
        ewma_lambda: Parâmetro EWMA.

    Retorna:
        Dict com 'alpha', 'method', 'base_var', 'base_weights', 'mvar' (dict ativo->impacto), 'assets'.
        Se carteira tem 1 ativo, mvar[ativo] = NaN.

    Exemplo:
        >>> res = marginal_var(rets, ['A', 'B', 'C'], [0.3, 0.4, 0.3], alpha=0.95, method='historical')
        >>> print(res['mvar'])
        {'A': -0.002, 'B': 0.001, 'C': -0.0005}

    Complexidade: O(n² * T) onde n = ativos, T = tamanho série.
    """
    sel = [a for a in assets if a in returns_df.columns]
    if not sel:
        raise ValueError("Nenhum ativo válido em returns_df")
    base_w = _as_weights(sel, weights)
    X = returns_df[sel].dropna(how='all').fillna(0.0)
    port_base = pd.Series(X.values @ base_w, index=X.index)
    if method == 'historical':
        base_var, _ = var_historical(port_base, alpha)
    elif method in ('std', 'ewma', 'garch'):
        base_var, _ = var_parametric(port_base, alpha, method=method, ewma_lambda=ewma_lambda)
    elif method == 'evt':
        base_var, _ = var_evt(port_base, alpha)
    else:
        raise ValueError("método inválido para MVaR")

    mvar: Dict[str, float] = {}
    for i, a in enumerate(sel):
        keep_idx = [j for j in range(len(sel)) if j != i]
        if not keep_idx:
            # não é possível remover o único ativo
            mvar[a] = float('nan')
            continue
        w = base_w[keep_idx]
        w = w / w.sum()
        Xsub = X.iloc[:, keep_idx]
        port_new = pd.Series(Xsub.values @ w, index=Xsub.index)
        if method == 'historical':
            v, _ = var_historical(port_new, alpha)
        elif method in ('std', 'ewma', 'garch'):
            v, _ = var_parametric(port_new, alpha, method=method, ewma_lambda=ewma_lambda)
        else:
            v, _ = var_evt(port_new, alpha)
        mvar[a] = float(v - base_var)
    return {
        "alpha": alpha,
        "method": method,
        "base_var": float(base_var),
        "base_weights": base_w.tolist(),
        "mvar": mvar,
        "assets": sel,
    }


def relative_var(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    alpha: float = 0.99,
    method: str = 'historical',
    ewma_lambda: float = 0.94,
) -> Dict:
    """VaR Relativo: VaR da underperformance da carteira em relação a um benchmark.

    Mede o risco de underperformance relativa. Útil para gestores com mandato
    de tracking ou para avaliar risco ativo.

    Fórmula:
        Relative VaR = VaR(R_portfolio - R_benchmark)

    Assumindo 95% de confiança, um Relative VaR de 2% significa que, em média,
    a carteira underperforma o benchmark por mais de 2% apenas 5% do tempo.

    Parâmetros:
        portfolio_returns: Série temporal de retornos da carteira.
        benchmark_returns: Série temporal de retornos do benchmark.
        alpha: Nível de confiança.
        method: 'historical' | 'std' | 'ewma' | 'garch' | 'evt'.
        ewma_lambda: Parâmetro EWMA.

    Retorna:
        Dict com 'relative_var', 'alpha', 'method', 'details' (específicos do método).

    Raises:
        ValueError: Se séries não têm interseção temporal.

    Exemplo:
        >>> port_rets = pd.Series([0.01, -0.02, 0.015, ...], index=dates)
        >>> bench_rets = pd.Series([0.008, -0.015, 0.012, ...], index=dates)
        >>> res = relative_var(port_rets, bench_rets, alpha=0.95, method='std')
        >>> print(f"Relative VaR: {res['relative_var']:.2%}")
        Relative VaR: 1.85%

    Complexidade: O(T) onde T = tamanho da interseção das séries.
    """
    # alinhar índices
    rP, rB = portfolio_returns.align(benchmark_returns, join='inner')
    rel = (rP - rB).dropna()
    if rel.empty:
        raise ValueError("Séries sem interseção para VaR relativo")
    if method == 'historical':
        v, d = var_historical(rel, alpha)
    elif method in ('std', 'ewma', 'garch'):
        v, d = var_parametric(rel, alpha, method=method, ewma_lambda=ewma_lambda)
    elif method == 'evt':
        v, d = var_evt(rel, alpha)
    else:
        raise ValueError("método inválido para VaR relativo")
    return {"relative_var": float(v), "alpha": alpha, "method": method, "details": d}


def _monthly_returns_from_prices(df_prices: pd.DataFrame) -> pd.DataFrame:
    df = df_prices.sort_index()
    monthly_prices = df.resample('M').last()
    rets = monthly_prices.pct_change().dropna(how='all')
    return rets


def ff3_metrics(
    prices: pd.DataFrame,
    ff3_factors: pd.DataFrame,
    rf_series: pd.Series,
    assets: List[str],
) -> Dict:
    """Calcula métricas Fama-French 3 fatores (mensal) por ativo via OLS.

    Parâmetros:
      - prices: DataFrame de preços diários. Será convertido para retornos mensais.
      - ff3_factors: DataFrame mensal com colunas ['MKT_RF','SMB','HML'] (em decimal).
      - rf_series: Série mensal do risk-free em decimal (SELIC ou US10Y convertido para mensal).
      - assets: Lista de ativos a avaliar.

    Retorna dict por ativo: alpha, betas, tstats, pvalues, r2, n_obs.
    """
    # Retornos mensais dos ativos
    rets_m = _monthly_returns_from_prices(prices[assets]).dropna(how='all')
    # Alinhar fatores e RF em base mensal
    factors = ff3_factors[['MKT_RF', 'SMB', 'HML']].copy()
    rf_m = rf_series.copy()
    # União por índice mensal
    df = rets_m.join(factors, how='inner').join(rf_m.to_frame('RF'), how='inner')
    if df.empty:
        raise ValueError("Sem interseção temporal entre retornos, fatores e RF")

    X = df[['MKT_RF', 'SMB', 'HML']]
    X = sm.add_constant(X)

    results: Dict[str, Any] = {}
    for a in assets:
        if a not in df.columns:
            continue
        y = (df[a] - df['RF']).dropna()
        XA = X.loc[y.index]
        if len(y) < 10:
            # poucos pontos para regressão
            continue
        model = sm.OLS(y.values, XA.values)
        res = model.fit()
        params = res.params.tolist()
        pvals = res.pvalues.tolist()
        tstats = res.tvalues.tolist()
        # params = [const, beta_mkt, beta_smb, beta_hml]
        note = None
        if int(res.nobs) < 12:
            note = "Poucas observações (< 12 meses); estimativas podem ser instáveis."
        results[a] = {
            'alpha': float(params[0]),
            'beta_mkt': float(params[1]),
            'beta_smb': float(params[2]),
            'beta_hml': float(params[3]),
            'pvalues': pvals,
            'tstats': tstats,
            'r2': float(res.rsquared),
            'n_obs': int(res.nobs),
            'notes': note,
        }
    return {'frequency': 'M', 'model': 'FF3', 'results': results}


def ff5_metrics(
    prices: pd.DataFrame,
    ff5_factors: pd.DataFrame,
    rf_series: pd.Series,
    assets: List[str],
) -> Dict:
    """Calcula métricas Fama-French 5 fatores (mensal) por ativo via OLS.

    Espera colunas: ['MKT_RF','SMB','HML','RMW','CMA'] em decimal.
    """
    rets_m = _monthly_returns_from_prices(prices[assets]).dropna(how='all')
    factors = ff5_factors[['MKT_RF', 'SMB', 'HML', 'RMW', 'CMA']].copy()
    rf_m = rf_series.copy()
    df = rets_m.join(factors, how='inner').join(rf_m.to_frame('RF'), how='inner')
    if df.empty:
        raise ValueError("Sem interseção temporal entre retornos, fatores e RF (FF5)")
    X = df[['MKT_RF', 'SMB', 'HML', 'RMW', 'CMA']]
    X = sm.add_constant(X)
    results: Dict[str, Any] = {}
    for a in assets:
        if a not in df.columns:
            continue
        y = (df[a] - df['RF']).dropna()
        XA = X.loc[y.index]
        if len(y) < 10:
            continue
        res = sm.OLS(y.values, XA.values).fit()
        params = res.params.tolist()
        pvals = res.pvalues.tolist()
        tstats = res.tvalues.tolist()
        note = None
        if int(res.nobs) < 12:
            note = "Poucas observações (< 12 meses); estimativas podem ser instáveis."
        results[a] = {
            'alpha': float(params[0]),
            'beta_mkt': float(params[1]),
            'beta_smb': float(params[2]),
            'beta_hml': float(params[3]),
            'beta_rmw': float(params[4]),
            'beta_cma': float(params[5]),
            'pvalues': pvals,
            'tstats': tstats,
            'r2': float(res.rsquared),
            'n_obs': int(res.nobs),
            'notes': note,
        }
    return {'frequency': 'M', 'model': 'FF5', 'results': results}

@dataclass
class RiskEngine:
    loader: DataLoader
    config: Config

    def _load_prices(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        df = self.loader.fetch_stock_prices(assets, start_date, end_date)
        return df

    def _portfolio_series(self, df_prices: pd.DataFrame, assets: List[str], weights: Optional[List[float]]) -> pd.Series:
        rets = compute_returns(df_prices)
        return portfolio_returns(rets, assets, weights)

    def compute_var(self, assets: List[str], start_date: str, end_date: str, alpha: float, method: str, ewma_lambda: float, weights: Optional[List[float]]) -> Dict:
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        if method == 'historical':
            value, details = var_historical(r, alpha)
        else:
            value, details = var_parametric(r, alpha, method=method, ewma_lambda=ewma_lambda)
        return {"var": value, "alpha": alpha, "method": method, "details": details}

    def compute_es(self, assets: List[str], start_date: str, end_date: str, alpha: float, method: str, ewma_lambda: float, weights: Optional[List[float]]) -> Dict:
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        if method == 'historical':
            value, details = es_historical(r, alpha)
        else:
            value, details = es_parametric(r, alpha, method=method, ewma_lambda=ewma_lambda)
        return {"es": value, "alpha": alpha, "method": method, "details": details}

    def compute_drawdown(self, assets: List[str], start_date: str, end_date: str, weights: Optional[List[float]]) -> Dict:
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        return drawdown(r)

    def compute_stress(self, assets: List[str], start_date: str, end_date: str, weights: Optional[List[float]], shock_pct: float) -> Dict:
        prices = self._load_prices(assets, start_date, end_date)
        rets = compute_returns(prices)
        return stress_test(rets, assets, weights, shocks_pct=shock_pct)

    def backtest(self, assets: List[str], start_date: str, end_date: str, alpha: float, method: str, ewma_lambda: float, weights: Optional[List[float]]) -> Dict:
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        return backtest_var(r, alpha=alpha, method=method, ewma_lambda=ewma_lambda)

    def compute_covariance(self, assets: List[str], start_date: str, end_date: str) -> Dict:
        prices = self._load_prices(assets, start_date, end_date)
        rets = compute_returns(prices)
        return covariance_ledoit_wolf(rets[assets])

    def compute_attribution(self, assets: List[str], start_date: str, end_date: str, weights: Optional[List[float]], method: str, ewma_lambda: float) -> Dict:
        prices = self._load_prices(assets, start_date, end_date)
        rets = compute_returns(prices)
        return risk_attribution(rets, assets, weights, method=method, ewma_lambda=ewma_lambda)

    def compare_methods(self, assets: List[str], start_date: str, end_date: str, alpha: float, methods: List[str], ewma_lambda: float, weights: Optional[List[float]]) -> Dict:
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        out: Dict[str, Dict] = {}
        for m in methods:
            if m == 'historical':
                v, vd = var_historical(r, alpha)
                e, ed = es_historical(r, alpha)
            elif m in ('std', 'ewma', 'garch'):
                v, vd = var_parametric(r, alpha, method=m, ewma_lambda=ewma_lambda)
                e, ed = es_parametric(r, alpha, method=m, ewma_lambda=ewma_lambda)
            elif m == 'evt':
                v, vd = var_evt(r, alpha)
                e, ed = es_evt(r, alpha)
            else:
                continue
            out[m] = {"var": v, "es": e, "var_details": vd, "es_details": ed}
        return {"alpha": alpha, "results": out}
