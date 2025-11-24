"""
This module provides core financial analysis functionalities, including:
- Calculation of returns and portfolio performance.
- Various Value at Risk (VaR) and Expected Shortfall (ES) methods (parametric, historical, EVT).
- Drawdown calculation.
- Stress testing.
- VaR backtesting.
- Covariance and risk attribution.
- Incremental and Marginal VaR.
- Relative VaR.
- Fama-French 3 and 5 factor model metrics.

It also defines `RiskEngine` for orchestrating risk analysis and `PortfolioAnalyzer` for transaction-based portfolio analysis.
"""
# analysis.py

import pandas as pd
import numpy as np
import statsmodels.api as sm
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.infrastructure.utils.config import Settings, settings

try:
    from arch import arch_model
except Exception:
    arch_model = None

from backend_projeto.domain.financial_math import _returns_from_prices, _annualize_mean_cov

def _as_weights(assets: List[str], weights: Optional[List[float]]) -> np.ndarray:
    """
    Normalizes a list of weights for a given set of assets.

    If weights are not provided, equal weights are assigned to all assets.
    Ensures that the sum of weights is 1 and handles cases where weights sum to zero.

    Args:
        assets (List[str]): A list of asset identifiers.
        weights (Optional[List[float]]): A list of numerical weights corresponding to the assets.
                                         If None, equal weights are assigned.

    Returns:
        np.ndarray: A NumPy array of normalized weights.

    Raises:
        ValueError: If the length of weights does not match the number of assets,
                    or if the sum of weights is zero.
    """
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
    """Calcula os retornos diários percentuais a partir de um DataFrame de preços.

    A função primeiro ordena o DataFrame de preços pelo índice (data),
    calcula a variação percentual entre os preços consecutivos, remove
    quaisquer linhas que contenham apenas valores NaN resultantes da
    operação de `pct_change`, e então substitui valores infinitos
    (positivos ou negativos) por NaN, removendo novamente linhas com todos os NaNs.

    Parâmetros:
        price_df (pd.DataFrame): Um DataFrame onde o índice são as datas
                                 e as colunas são os preços dos ativos.

    Retorna:
        pd.DataFrame: Um DataFrame contendo os retornos diários percentuais
                      para cada ativo, com o mesmo índice de datas.
                      Valores infinitos e linhas com todos os NaNs são removidos.
    """
    r = price_df.sort_index().pct_change().dropna(how='all')
    return r.replace([np.inf, -np.inf], np.nan).dropna(how='all')


def portfolio_returns(returns_df: pd.DataFrame, assets: List[str], weights: Optional[List[float]]) -> pd.Series:
    """Calcula os retornos de um portfólio a partir dos retornos de ativos individuais e seus pesos.

    A função filtra os ativos presentes no DataFrame de retornos, normaliza os pesos
    (se fornecidos, ou assume pesos iguais), e então calcula o retorno ponderado do portfólio.
    Os pesos são renormalizados por data para considerar apenas ativos com retorno disponível.

    Parâmetros:
        returns_df (pd.DataFrame): DataFrame onde o índice são as datas e as colunas
                                   são os retornos diários dos ativos.
        assets (List[str]): Lista de tickers dos ativos a serem incluídos no portfólio.
        weights (Optional[List[float]]): Lista de pesos correspondentes aos ativos.
                                         Se None, os ativos são igualmente ponderados.
                                         Os pesos são normalizados para somar 1.

    Retorna:
        pd.Series: Uma série temporal contendo os retornos diários do portfólio.

    Raises:
        ValueError: Se nenhum ativo válido for encontrado no `returns_df` ou se a soma dos pesos for zero.
    """
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

def calculate_rolling_beta(asset_returns: pd.Series, benchmark_returns: pd.Series, window: int = 60) -> pd.Series:
    """
    Calculates the rolling beta of an asset's returns against a benchmark's returns.

    The beta is calculated as: Cov(R_asset, R_benchmark) / Var(R_benchmark)
    This function aligns the two series by their index and then computes the
    rolling covariance and variance over a specified window.

    Args:
        asset_returns (pd.Series): A time series of the asset's returns.
        benchmark_returns (pd.Series): A time series of the benchmark's returns.
        window (int): The size of the rolling window for calculation. Defaults to 60.

    Returns:
        pd.Series: A time series of the rolling beta values.
    """
    # Alinhar as séries de retornos
    asset_returns, benchmark_returns = asset_returns.align(benchmark_returns, join='inner')
    
    # Covariância rolante
    rolling_cov = asset_returns.rolling(window=window).cov(benchmark_returns)
    
    # Variância rolante do benchmark
    rolling_var = benchmark_returns.rolling(window=window).var()
    
    # Beta rolante
    rolling_beta = rolling_cov / rolling_var
    
    return rolling_beta.dropna()


def var_parametric(returns: pd.Series, alpha: float = 0.99, method: str = 'std', ewma_lambda: float = 0.94) -> Tuple[float, Dict]:
    """
    Calculates Parametric Value at Risk (VaR) assuming a normal distribution (or conditional GARCH).

    IMPORTANT: Assumes normality of returns. For distributions with heavy tails,
    consider using the EVT method.

    Methods:
        - 'std': Historical volatility (sample standard deviation).
        - 'ewma': EWMA (Exponentially Weighted Moving Average) volatility.
        - 'garch': Conditional volatility via GARCH(1,1).

    Args:
        returns (pd.Series): Series of asset returns.
        alpha (float): Confidence level (e.g., 0.99 for 99% VaR).
        method (str): Calculation method: 'std', 'ewma', or 'garch'.
        ewma_lambda (float): EWMA decay factor (default 0.94, RiskMetrics uses 0.94).

    Returns:
        Tuple[float, Dict]: A tuple containing the VaR value and a dictionary of details
                            (e.g., {'mu', 'sigma', 'z', 'method', 'ewma_lambda'}).

    Raises:
        RuntimeError: If 'arch' package is not available for 'garch' method.
        ValueError: If an invalid method is specified.
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
    """
    Calculates Parametric Expected Shortfall (ES) or Conditional Value at Risk (CVaR).

    IMPORTANT: Assumes normality of returns. ES is the average of losses beyond the VaR.

    Formula (normal distribution):
        ES = μ - σ * φ(z) / (1 - α)
        where φ is the PDF of the standard normal distribution and z = Φ^(-1)(1 - α).

    Args:
        returns (pd.Series): Series of asset returns.
        alpha (float): Confidence level.
        method (str): Calculation method: 'std', 'ewma', or 'garch'.
        ewma_lambda (float): EWMA decay factor.

    Returns:
        Tuple[float, Dict]: A tuple containing the ES value and a dictionary of details.

    Raises:
        ValueError: If an invalid method is specified.
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
    """
    Calculates Historical Value at Risk (VaR).

    The historical VaR is determined by finding the (1-alpha) quantile of the
    historical returns distribution.

    Args:
        returns (pd.Series): Series of asset returns.
        alpha (float): Confidence level (e.g., 0.99 for 99% VaR).

    Returns:
        Tuple[float, Dict]: A tuple containing the VaR value and a dictionary of details
                            (e.g., {'quantile': q}).
    """
    q = returns.quantile(1 - alpha)
    return float(-q), {"quantile": q}


def es_historical(returns: pd.Series, alpha: float = 0.99) -> Tuple[float, Dict]:
    """
    Calculates Historical Expected Shortfall (ES) or Conditional Value at Risk (CVaR).

    ES is the average of losses that exceed the historical VaR at a given confidence level.

    Args:
        returns (pd.Series): Series of asset returns.
        alpha (float): Confidence level (e.g., 0.99 for 99% ES).

    Returns:
        Tuple[float, Dict]: A tuple containing the ES value and a dictionary of details
                            (e.g., {'threshold': q, 'n_tail': count}).
    """
    q = returns.quantile(1 - alpha)
    tail = returns[returns < q]
    es = tail.mean()
    return float(-es), {"threshold": q, "n_tail": len(tail)}


# EVT (GPD) na cauda das perdas
def var_evt(returns: pd.Series, alpha: float = 0.99, threshold_quantile: float = 0.9) -> Tuple[float, Dict]:
    """
    Calculates Value at Risk (VaR) using Extreme Value Theory (EVT) with a Generalized Pareto Distribution (GPD).

    This method models the tail of the loss distribution, providing a more robust VaR estimate
    for distributions with heavy tails compared to parametric methods assuming normality.
    It works with losses (L = -R).

    Args:
        returns (pd.Series): Series of asset returns.
        alpha (float): Confidence level (e.g., 0.99 for 99% VaR).
        threshold_quantile (float): Quantile used to define the threshold for extreme losses.
                                    Losses above this threshold are fitted to a GPD.

    Returns:
        Tuple[float, Dict]: A tuple containing the VaR value (as a positive loss) and a dictionary of details
                            (e.g., {'xi', 'beta', 'u', 'p_tail'}).

    Notes:
        - If the number of observations or excess values is too small, it falls back to historical VaR.
    """


def es_evt(returns: pd.Series, alpha: float = 0.99, threshold_quantile: float = 0.9) -> Tuple[float, Dict]:
    """
    Calculates Expected Shortfall (ES) using Extreme Value Theory (EVT) with a Generalized Pareto Distribution (GPD).

    ES for EVT is derived from the GPD parameters and the VaR calculated using EVT.
    It represents the expected loss given that the loss exceeds the VaR.

    Args:
        returns (pd.Series): Series of asset returns.
        alpha (float): Confidence level (e.g., 0.99 for 99% ES).
        threshold_quantile (float): Quantile used to define the threshold for extreme losses.

    Returns:
        Tuple[float, Dict]: A tuple containing the ES value (as a positive loss) and a dictionary of details
                            (e.g., {'xi', 'beta', 'u', 'p_tail', 'var_loss'}).

    Notes:
        - If the number of observations or excess values is too small, it falls back to historical ES.
    """


def drawdown(returns: pd.Series) -> Dict:
    """
    Calculates the maximum drawdown and its start/end dates for a series of returns.

    Drawdown measures the peak-to-trough decline during a specific period for an investment,
    portfolio, or fund.

    Args:
        returns (pd.Series): Series of asset or portfolio returns.

    Returns:
        Dict: A dictionary containing:
              - "max_drawdown" (float): The maximum drawdown as a negative percentage.
              - "start" (str): The start date of the maximum drawdown period.
              - "end" (str): The end date of the maximum drawdown period.
    """
    # Calculate cumulative returns
    cum_returns = (1 + returns).cumprod()
    # Calculate the running maximum
    running_max = cum_returns.cummax()
    # Calculate the drawdown
    drawdown = (cum_returns - running_max) / running_max
    
    # Find the maximum drawdown
    max_drawdown = drawdown.min()
    end_date = drawdown.idxmin()
    start_date = cum_returns.index[cum_returns.index.get_loc(end_date) - (cum_returns.iloc[:cum_returns.index.get_loc(end_date)] == running_max.iloc[cum_returns.index.get_loc(end_date)]).iloc[::-1].idxmax()]
    
    return {
        "max_drawdown": max_drawdown,
        "start": start_date.strftime('%Y-%m-%d'),
        "end": end_date.strftime('%Y-%m-%d')
    }


def stress_test(returns_df: pd.DataFrame, assets: List[str], weights: Optional[List[float]], shocks_pct: float = -0.1) -> Dict:
    """
    Performs a stress test by applying a hypothetical shock to the latest returns of specified assets.

    This function simulates the impact of an immediate, adverse market movement on the portfolio's
    return by adjusting the last observed returns by a given percentage shock.

    Args:
        returns_df (pd.DataFrame): DataFrame of historical asset returns.
        assets (List[str]): List of asset tickers to include in the portfolio.
        weights (Optional[List[float]]): Weights of the assets in the portfolio. If None, equal weights are assumed.
        shocks_pct (float): The percentage shock to apply to the latest returns (e.g., -0.1 for a -10% shock).

    Returns:
        Dict: A dictionary containing:
              - "shock" (float): The applied shock percentage.
              - "portfolio_return" (float): The simulated portfolio return after the shock.
              - "asset_returns" (Dict[str, float]): The simulated returns for each asset after the shock.
    """


def backtest_var(returns: pd.Series, alpha: float, method: str = 'historical', ewma_lambda: float = 0.94) -> Dict:
    """
    Performs a backtest of Value at Risk (VaR) using a rolling window.

    This function evaluates the accuracy of a VaR model by comparing predicted VaR values
    with actual portfolio losses over a historical period. It calculates the number of
    exceptions (times actual loss exceeded VaR) and performs Kupiec's POF test and
    Christoffersen's independence test. It also provides a Basel Traffic-Light zone.

    Args:
        returns (pd.Series): Series of portfolio returns.
        alpha (float): Confidence level for VaR calculation.
        method (str): VaR calculation method ('historical', 'std', 'ewma', 'garch', 'evt').
        ewma_lambda (float): Decay factor for the EWMA method.

    Returns:
        Dict: A dictionary containing backtest results, including:
              - "n" (int): Total number of observations in the backtest period.
              - "exceptions" (int): Number of times actual losses exceeded VaR.
              - "exception_rate" (float): The rate of exceptions.
              - "kupiec_lr" (float): Kupiec's Likelihood Ratio statistic.
              - "kupiec_pvalue" (float): P-value for Kupiec's test.
              - "christoffersen_lr_ind" (float): Christoffersen's independence LR statistic.
              - "christoffersen_pvalue" (float): P-value for Christoffersen's independence test.
              - "christoffersen_lr_cc" (float): Christoffersen's conditional coverage LR statistic.
              - "christoffersen_cc_pvalue" (float): P-value for Christoffersen's conditional coverage test.
              - "basel_zone" (str): Basel Traffic-Light zone ('green', 'amber', 'red').
              - "alpha" (float): The confidence level used.
              - "method" (str): The VaR method used for backtesting.

    Raises:
        ValueError: If an invalid VaR method is provided.
    """


# Covariância (Ledoit-Wolf) e atribuição de risco
def covariance_ledoit_wolf(returns_df: pd.DataFrame) -> Dict:
    """
    Calculates the Ledoit-Wolf shrunk covariance matrix for asset returns.

    The Ledoit-Wolf estimator is a shrinkage estimator for the covariance matrix,
    which can be more robust than the sample covariance matrix, especially
    when the number of assets is large relative to the number of observations.

    Args:
        returns_df (pd.DataFrame): DataFrame of historical asset returns.

    Returns:
        Dict: A dictionary containing:
              - "cov" (List[List[float]]): The shrunk covariance matrix as a list of lists.
              - "shrinkage" (float): The shrinkage intensity applied by the Ledoit-Wolf estimator.
              - "columns" (List[str]): The list of asset columns in the covariance matrix.

    Raises:
        RuntimeError: If the 'sklearn' package is not available.
    """


def risk_attribution(returns_df: pd.DataFrame, assets: List[str], weights: Optional[List[float]], method: str = 'std', ewma_lambda: float = 0.94) -> Dict:
    """
    Performs risk attribution for a portfolio, calculating each asset's contribution to total portfolio risk.

    This function calculates the marginal contribution to volatility and, for parametric methods,
    the marginal contribution to VaR. It uses a shrunk covariance matrix for robustness.

    Args:
        returns_df (pd.DataFrame): DataFrame of historical asset returns.
        assets (List[str]): List of asset tickers in the portfolio.
        weights (Optional[List[float]]): Weights of the assets in the portfolio. If None, equal weights are assumed.
        method (str): Method for VaR calculation if marginal VaR is to be computed ('std', 'ewma').
        ewma_lambda (float): Decay factor for the EWMA method.

    Returns:
        Dict: A dictionary containing:
              - "assets" (List[str]): List of asset tickers.
              - "weights" (List[float]): Normalized weights of the assets.
              - "portfolio_vol" (float): Total portfolio volatility.
              - "contribution_vol" (List[float]): Each asset's contribution to portfolio volatility.
              - "contribution_var" (List[float]): Each asset's contribution to portfolio VaR (if applicable).

    Raises:
        ValueError: If no valid assets are found for attribution.
    """


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
    """
    Calculates monthly returns from a DataFrame of daily prices.

    The function first sorts the DataFrame by index (date), then resamples it
    to monthly frequency, taking the last price of each month. Finally, it
    calculates the percentage change between consecutive monthly prices.

    Args:
        df_prices (pd.DataFrame): DataFrame where the index are daily dates
                                  and columns are asset prices.

    Returns:
        pd.DataFrame: DataFrame containing monthly percentage returns for each asset.
    """
    return df_prices.sort_index().resample('M').last().pct_change().dropna(how='all')


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
    """Orquestra a análise de risco, calculando métricas como VaR, ES, drawdown, etc."""
    loader: YFinanceProvider
    config: Settings
    def _load_prices(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Carrega os preços históricos para uma lista de ativos."""
        df = self.loader.fetch_stock_prices(assets, start_date, end_date)
        return df

    def _portfolio_series(self, df_prices: pd.DataFrame, assets: List[str], weights: Optional[List[float]]) -> pd.Series:
        """Calcula a série de retornos do portfólio."""
        rets = compute_returns(df_prices)
        return portfolio_returns(rets, assets, weights)

    def compute_var(self, assets: List[str], start_date: str, end_date: str, alpha: float, method: str, ewma_lambda: float, weights: Optional[List[float]]) -> Dict:
        """Calcula o Value at Risk (VaR) para a carteira.

        Args:
            assets: Lista de tickers dos ativos.
            start_date: Data de início para os dados históricos.
            end_date: Data de fim para os dados históricos.
            alpha: Nível de confiança para o VaR.
            method: Método de cálculo ('historical', 'std', 'ewma', 'garch').
            ewma_lambda: Fator de decaimento para o método EWMA.
            weights: Pesos da carteira.

        Returns:
            Dicionário com o valor do VaR e detalhes do cálculo.
        """
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        if method == 'historical':
            value, details = var_historical(r, alpha)
        else:
            value, details = var_parametric(r, alpha, method=method, ewma_lambda=ewma_lambda)
        return {"var": value, "alpha": alpha, "method": method, "details": details}

    def compute_es(self, assets: List[str], start_date: str, end_date: str, alpha: float, method: str, ewma_lambda: float, weights: Optional[List[float]]) -> Dict:
        """Calcula o Expected Shortfall (ES) para a carteira.

        Args:
            assets: Lista de tickers dos ativos.
            start_date: Data de início para os dados históricos.
            end_date: Data de fim para os dados históricos.
            alpha: Nível de confiança para o ES.
            method: Método de cálculo ('historical', 'std', 'ewma', 'garch').
            ewma_lambda: Fator de decaimento para o método EWMA.
            weights: Pesos da carteira.

        Returns:
            Dicionário com o valor do ES e detalhes do cálculo.
        """
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        if method == 'historical':
            value, details = es_historical(r, alpha)
        else:
            value, details = es_parametric(r, alpha, method=method, ewma_lambda=ewma_lambda)
        return {"es": value, "alpha": alpha, "method": method, "details": details}

    def compute_drawdown(self, assets: List[str], start_date: str, end_date: str, weights: Optional[List[float]]) -> Dict:
        """Calcula o drawdown máximo da carteira.

        Args:
            assets: Lista de tickers dos ativos.
            start_date: Data de início para os dados históricos.
            end_date: Data de fim para os dados históricos.
            weights: Pesos da carteira.

        Returns:
            Dicionário com o drawdown máximo e as datas de início e fim.
        """
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        return drawdown(r)

    def compute_stress(self, assets: List[str], start_date: str, end_date: str, weights: Optional[List[float]], shock_pct: float) -> Dict:
        """Realiza um teste de estresse aplicando um choque aos retornos.

        Args:
            assets: Lista de tickers dos ativos.
            start_date: Data de início para os dados históricos.
            end_date: Data de fim para os dados históricos.
            weights: Pesos da carteira.
            shock_pct: Percentual de choque a ser aplicado.

        Returns:
            Dicionário com o resultado do teste de estresse.
        """
        prices = self._load_prices(assets, start_date, end_date)
        rets = compute_returns(prices)
        return stress_test(rets, assets, weights, shocks_pct=shock_pct)

    def backtest(self, assets: List[str], start_date: str, end_date: str, alpha: float, method: str, ewma_lambda: float, weights: Optional[List[float]]) -> Dict:
        """Realiza um backtest do VaR para avaliar a precisão do modelo.

        Args:
            assets: Lista de tickers dos ativos.
            start_date: Data de início para os dados históricos.
            end_date: Data de fim para os dados históricos.
            alpha: Nível de confiança do VaR.
            method: Método de cálculo do VaR.
            ewma_lambda: Fator de decaimento para o método EWMA.
            weights: Pesos da carteira.

        Returns:
            Dicionário com os resultados do backtest.
        """
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        return backtest_var(r, alpha=alpha, method=method, ewma_lambda=ewma_lambda)

    def compute_covariance(self, assets: List[str], start_date: str, end_date: str) -> Dict:
        """Calcula a matriz de covariância dos retornos dos ativos.

        Args:
            assets: Lista de tickers dos ativos.
            start_date: Data de início para os dados históricos.
            end_date: Data de fim para os dados históricos.

        Returns:
            Dicionário com a matriz de covariância e o fator de shrinkage.
        """
        prices = self._load_prices(assets, start_date, end_date)
        rets = compute_returns(prices)
        return covariance_ledoit_wolf(rets[assets])

    def compute_attribution(self, assets: List[str], start_date: str, end_date: str, weights: Optional[List[float]], method: str, ewma_lambda: float) -> Dict:
        """Realiza a atribuição de risco para a carteira.

        Args:
            assets: Lista de tickers dos ativos.
            start_date: Data de início para os dados históricos.
            end_date: Data de fim para os dados históricos.
            weights: Pesos da carteira.
            method: Método de cálculo.
            ewma_lambda: Fator de decaimento para o método EWMA.

        Returns:
            Dicionário com a contribuição de cada ativo para o risco total.
        """
        prices = self._load_prices(assets, start_date, end_date)
        rets = compute_returns(prices)
        return risk_attribution(rets, assets, weights, method=method, ewma_lambda=ewma_lambda)

    def compare_methods(self, assets: List[str], start_date: str, end_date: str, alpha: float, methods: List[str], ewma_lambda: float, weights: Optional[List[float]]) -> Dict:
        """
        Compares different Value at Risk (VaR) and Expected Shortfall (ES) calculation methods.

        This method facilitates a comparative analysis of how various risk metrics
        perform under different calculation methodologies (e.g., historical, parametric).

        Args:
            assets (List[str]): List of tickers for the assets.
            start_date (str): Start date for historical data.
            end_date (str): End date for historical data.
            alpha (float): Confidence level for risk metrics.
            methods (List[str]): List of methods to be compared.
            ewma_lambda (float): Decay factor for the EWMA method.
            weights (Optional[List[float]]): Portfolio weights.

        Returns:
            Dict: A dictionary containing the results of the comparison for various risk metrics.
                  The structure of the dictionary depends on the methods compared internally.
        """
        prices = self._load_prices(assets, start_date, end_date)
        r = self._portfolio_series(prices, assets, weights)
        
        comparison = {}
        for method in methods:
            var_value, var_details = self.compute_var(assets, start_date, end_date, alpha, method, ewma_lambda, weights)
            es_value, es_details = self.compute_es(assets, start_date, end_date, alpha, method, ewma_lambda, weights)
            comparison[method] = {
                "var": var_value,
                "es": es_value,
            }
        return {"comparison": comparison}

class PortfolioAnalyzer:
    """
    Classe para análise de portfólio baseada em transações.
    
    Esta classe fornece métodos para analisar o desempenho, risco e alocação
    de um portfólio com base em um histórico de transações.
    """
    
    def __init__(self, transactions_df: pd.DataFrame, data_loader: YFinanceProvider = None, config: Settings = None, end_date: Optional[str] = None):
        """
        Inicializa o analisador de portfólio com um DataFrame de transações.
        
        Args:
            transactions_df: DataFrame contendo as transações com as seguintes colunas:
                - Data: data da transação
                - Ativo: código do ativo
                - Quantidade: quantidade negociada (positiva para compra, negativa para venda)
                - Preco: preço unitário da transação
                - Taxas: taxas e custos da transação
            data_loader: Instância de YFinanceProvider para carregar dados de mercado
            config: Instância de Config com parâmetros de configuração
            end_date: Data final da análise. Se None, usa a data atual.
        """
        if transactions_df.empty:
            raise ValueError("Nenhuma transação fornecida")
        required_columns = ['Data', 'Ativo', 'Quantidade', 'Preco']
        if not all(col in transactions_df.columns for col in required_columns):
            raise ValueError(f"O DataFrame de transações deve conter as colunas: {required_columns}")

        self.transactions = transactions_df.copy()
        
        # Converter a coluna de data para datetime, se necessário
        if 'Data' in self.transactions.columns:
            self.transactions['Data'] = pd.to_datetime(self.transactions['Data'])
        
        self.data_loader = data_loader if data_loader else YFinanceProvider()
        self.config = config if config else settings
        
        # Lista de ativos únicos no portfólio
        self.assets = self.transactions['Ativo'].unique().tolist()
        
        # Período de análise
        self.start_date = self.transactions['Data'].min()
        self.end_date = pd.to_datetime(end_date).normalize() if end_date else pd.to_datetime('today').normalize()
        
        # Dados calculados
        self.returns = None
        self.positions = None
        self.portfolio_value = None
        
    def _calculate_positions(self) -> pd.DataFrame:
        """
        Calcula a posição em cada ativo ao longo do tempo com base nas transações.
        
        Returns:
            DataFrame com a posição em cada ativo por data
        """
        # Criar um índice de datas únicas
        dates = pd.date_range(
            start=self.start_date,
            end=self.end_date,
            freq='B',
            name='Data'
        )
        
        # Inicializar DataFrame de posições
        positions = pd.DataFrame(index=dates, columns=self.assets).fillna(0.0)
        
        # Processar cada transação
        for _, tx in self.transactions.iterrows():
            date = tx['Data']
            asset = tx['Ativo']
            quantity = tx['Quantidade']
            
            # Atualizar a posição a partir da data da transação
            positions.loc[date:, asset] += quantity
        
        # Preencher valores ausentes com o último valor válido
        positions = positions.ffill().fillna(0.0)
        
        return positions
    
    def _calculate_portfolio_value(self) -> pd.Series:
        """
        Calcula o valor total do portfólio ao longo do tempo.
        
        Returns:
            Série com o valor do portfólio por data
        """
        if self.positions is None:
            self.positions = self._calculate_positions()
        
        # Obter preços históricos para todos os ativos
        prices = self.data_loader.fetch_stock_prices(
            assets=self.assets,
            start_date=self.start_date.strftime('%Y-%m-%d'),
            end_date=self.end_date.strftime('%Y-%m-%d')
        )
        
        # Calcular o valor de cada posição
        portfolio_value = pd.Series(0.0, index=self.positions.index, name='Valor')
        
        for asset in self.assets:
            if asset in prices.columns:
                # Preencher valores ausentes nos preços com o último valor válido
                asset_prices = prices[asset].reindex(portfolio_value.index).ffill()
                portfolio_value += self.positions[asset] * asset_prices
        
        return portfolio_value
    
    def calculate_returns(self, method: str = 'log') -> pd.Series:
        """
        Calcula os retornos do portfólio.
        
        Args:
            method: Método de cálculo dos retornos ('log' ou 'simple')
            
        Returns:
            Série com os retornos do portfólio
        """
        if self.portfolio_value is None:
            self.portfolio_value = self._calculate_portfolio_value()
        
        if method == 'log':
            returns = np.log(self.portfolio_value / self.portfolio_value.shift(1)).dropna()
        else:  # simple returns
            returns = self.portfolio_value.pct_change().dropna()
            
        self.returns = returns
        return returns
    
    def analyze_performance(self) -> dict:
        """
        Analisa o desempenho do portfólio.
        
        Returns:
            Dicionário com métricas de desempenho
        """
        if self.returns is None:
            self.calculate_returns()
        
        if len(self.returns) < 2:
            return {"error": "Dados insuficientes para análise de desempenho"}
        
        # Calcular métricas de desempenho
        total_return = (self.portfolio_value.iloc[-1] / self.portfolio_value.iloc[0] - 1) * 100  # em %
        annualized_return = (1 + self.returns.mean()) ** 252 - 1  # Supondo 252 dias de negociação por ano
        annualized_vol = self.returns.std() * np.sqrt(252)  # Volatilidade anualizada
        sharpe_ratio = annualized_return / annualized_vol if annualized_vol > 0 else 0
        
        # Calcular drawdown
        cum_returns = (1 + self.returns).cumprod()
        running_max = cum_returns.cummax()
        drawdowns = (cum_returns - running_max) / running_max
        max_drawdown = drawdowns.min() * 100  # em %
        
        # Calcular VaR e ES
        var_95, _ = var_historical(self.returns, alpha=0.95)
        var_95 *= 100  # em %
        es_95, _ = es_historical(self.returns, alpha=0.95)
        es_95 *= 100  # em %
        
        return {
            "retorno_total_%": round(total_return, 2),
            "retorno_anualizado_%": round(annualized_return * 100, 2),
            "volatilidade_anual_%": round(annualized_vol * 100, 2),
            "indice_sharpe": round(sharpe_ratio, 2),
            "max_drawdown_%": round(max_drawdown, 2),
            "var_95%_1d_%": round(var_95, 2),
            "es_95%_1d_%": round(es_95, 2),
            "dias_analisados": len(self.returns),
            "data_inicio": self.start_date.strftime('%Y-%m-%d'),
            "data_fim": self.end_date.strftime('%Y-%m-%d')
        }
    
    def analyze_allocation(self, date: Optional[str] = None) -> dict:
        """
        Analisa a alocação do portfólio em uma data específica.
        
        Args:
            date: Data para análise (formato 'YYYY-MM-DD'). Se None, usa a data mais recente.
            
        Returns:
            Dicionário com a alocação por ativo
        """
        if self.positions is None:
            self.positions = self._calculate_positions()
        
        # Determinar a data de análise
        if date is None:
            analysis_date = self.end_date
        else:
            analysis_date = pd.to_datetime(date)
            if analysis_date < self.start_date or analysis_date > self.end_date:
                return {"error": f"Data fora do intervalo de análise ({self.start_date} a {self.end_date})"}
        
        # Obter posições na data de análise
        positions = self.positions.loc[analysis_date]
        
        # Obter preços na data de análise
        prices = self.data_loader.fetch_stock_prices(
            assets=self.assets,
            start_date=analysis_date.strftime('%Y-%m-%d'),
            end_date=analysis_date.strftime('%Y-%m-%d')
        )
        
        # Calcular valores das posições
        allocation = {}
        total_value = 0.0
        
        for asset in self.assets:
            if asset in prices.columns and not pd.isna(prices.loc[analysis_date, asset]):
                asset_value = positions[asset] * prices.loc[analysis_date, asset]
                if asset_value > 0:  # Apenas incluir ativos com valor positivo
                    allocation[asset] = {
                        'quantidade': positions[asset],
                        'preco_unitario': prices.loc[analysis_date, asset],
                        'valor_total': asset_value
                    }
                    total_value += asset_value
        
        # Calcular percentuais
        for asset in allocation:
            allocation[asset]['percentual'] = (allocation[asset]['valor_total'] / total_value) * 100 if total_value > 0 else 0
        
        return {
            'data_analise': analysis_date.strftime('%Y-%m-%d'),
            'valor_total': total_value,
            'alocacao': allocation
        }
    
    def run_analysis(self) -> dict:
        """
        Executa uma análise completa do portfólio.
        
        Returns:
            Dicionário com os resultados da análise
        """
        # Calcular posições e valor do portfólio
        self.positions = self._calculate_positions()
        self.portfolio_value = self._calculate_portfolio_value()
        
        # Realizar análises
        performance = self.analyze_performance()
        allocation = self.analyze_allocation()
        
        # Retornar resultados consolidados
        return {
            'desempenho': performance,
            'alocacao': allocation,
            'metadados': {
                'ativos': self.assets,
                'periodo_analise': {
                    'inicio': self.start_date.strftime('%Y-%m-%d'),
                    'fim': self.end_date.strftime('%Y-%m-%d'),
                    'dias_uteis': len(self.portfolio_value)
                },
                'transacoes': len(self.transactions)
            }
        }
