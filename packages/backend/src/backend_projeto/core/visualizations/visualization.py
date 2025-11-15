# visualization.py

import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend não interativo para geração de imagens
import matplotlib.pyplot as plt
from typing import List, Optional

from backend_projeto.utils.config import Settings
from backend_projeto.core.data_handling import YFinanceProvider


def _returns_from_prices(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.sort_index().pct_change().dropna(how="all")


def _annualize_mean_cov(rets: pd.DataFrame, dias_uteis: int):
    mu = rets.mean().values * dias_uteis
    cov = rets.cov().values * dias_uteis
    return mu, cov


def efficient_frontier_image(
    loader: YFinanceProvider,
    config: Settings,
    assets: List[str],
    start_date: str,
    end_date: str,
    n_samples: int = 5000,
    long_only: bool = True,
    max_weight: Optional[float] = None,
    rf: float = 0.0,
) -> bytes:
    """Gera um gráfico (PNG) da fronteira eficiente por amostragem aleatória de carteiras.

    Observação: implementação suporta apenas *long_only* no momento.
    """
    if not long_only:
        raise ValueError("A visualização suporta apenas long_only=True no momento.")

    prices = loader.fetch_stock_prices(assets, start_date, end_date)
    rets = _returns_from_prices(prices)[assets].dropna()
    if rets.shape[1] < 2:
        raise ValueError("São necessários pelo menos 2 ativos para a fronteira eficiente")

    mu, cov = _annualize_mean_cov(rets, config.DIAS_UTEIS_ANO)
    n = len(assets)

    R = []
    V = []
    S = []

    i = 0
    maxw = 1.0 if max_weight is None else float(max_weight)
    while i < n_samples:
        # amostra Dirichlet para pesos positivos que somam 1
        w = np.random.dirichlet(np.ones(n))
        if max_weight is not None and (w.max() > maxw):
            continue  # respeitar limite por ativo
        ret = float(w @ mu)
        vol = float(np.sqrt(max(w @ cov @ w, 0.0)))
        sharpe = (ret - rf) / (vol + 1e-12)
        R.append(ret)
        V.append(vol)
        S.append(sharpe)
        i += 1

    R = np.array(R)
    V = np.array(V)
    S = np.array(S)

    best = int(np.argmax(S))

    plt.figure(figsize=(10, 6)) # Aumentar um pouco o tamanho para melhor visualização
    sc = plt.scatter(V, R, c=S, cmap="viridis", s=12, alpha=0.85, label="Portfólios Simulados")
    plt.colorbar(sc, label="Sharpe Ratio")
    
    # Portfólio de Máximo Sharpe (Tangência)
    plt.scatter([V[best]], [R[best]], color="red", marker="*", s=200, label="Max Sharpe Portfólio")
    
    # Capital Market Line (CML)
    # A CML conecta o risk-free rate ao portfólio de tangência
    # Equação da CML: E(Rp) = Rf + (E(Rm) - Rf) / Std(Rm) * Std(Rp)
    # Onde (E(Rm) - Rf) / Std(Rm) é o Sharpe Ratio do portfólio de tangência
    
    sharpe_tangency = S[best]
    vol_tangency = V[best]
    ret_tangency = R[best]

    # Gerar pontos para a linha CML
    x_cml = np.linspace(0, max(V) * 1.1, 100) # Vai de 0 até um pouco além da volatilidade máxima
    y_cml = rf + sharpe_tangency * x_cml
    
    plt.plot(x_cml, y_cml, color='green', linestyle='--', linewidth=2, label="Capital Market Line (CML)")
    
    plt.xlabel("Volatilidade (Desvio Padrão Anualizado)")
    plt.ylabel("Retorno Anualizado")
    plt.title("Fronteira Eficiente e Capital Market Line", fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150)
    plt.close()
    buf.seek(0)
    return buf.read()
