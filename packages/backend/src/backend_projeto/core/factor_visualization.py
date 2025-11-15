"""
This module provides functions for visualizing Fama-French factors and betas.

It uses `matplotlib` to generate plots of time series of Fama-French factors
and bar charts of asset betas against these factors.
"""
import io
from typing import List, Optional, Dict

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_ff_factors(factors: pd.DataFrame, title: str = "Fama-French Factors (Monthly)") -> bytes:
    """
    Plots time series of Fama-French factors (lines).

    Expects a DataFrame with standardized factor columns.

    Args:
        factors (pd.DataFrame): Monthly DataFrame with columns like MKT_RF, SMB, HML, RMW, CMA.
        title (str): Title of the plot. Defaults to "Fama-French Factors (Monthly)".

    Returns:
        bytes: PNG image of the plot in bytes format.

    Raises:
        ValueError: If no valid factors are found for plotting.
    """
    allowed = [c for c in ["MKT_RF", "SMB", "HML", "RMW", "CMA"] if c in factors.columns]
    if not allowed:
        raise ValueError("Nenhum fator válido encontrado para plotagem")

    fig, ax = plt.subplots(figsize=(12, 6))
    for c in allowed:
        ax.plot(factors.index, factors[c], label=c)
    ax.set_title(title)
    ax.set_xlabel("Data (mês)")
    ax.set_ylabel("Retorno mensal (decimal)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def plot_ff_betas(betas: Dict[str, float], model: str = "FF3", title: Optional[str] = None) -> bytes:
    """
    Plots bar chart of asset betas for Fama-French 3 or 5 factor models.

    Args:
        betas (Dict[str, float]): Dictionary containing beta values.
                                  Expected keys for FF3: beta_mkt, beta_smb, beta_hml.
                                  Expected keys for FF5: beta_mkt, beta_smb, beta_hml, beta_rmw, beta_cma.
        model (str): The Fama-French model used ("FF3" or "FF5"). Defaults to "FF3".
        title (Optional[str]): Title of the plot. If None, a default title is generated.

    Returns:
        bytes: PNG image of the plot in bytes format.
    """
    if model.upper() == "FF3":
        order = ["beta_mkt", "beta_smb", "beta_hml"]
        labels = ["MKT", "SMB", "HML"]
    else:
        order = ["beta_mkt", "beta_smb", "beta_hml", "RMW", "CMA"]  # labels map below
        labels = ["MKT", "SMB", "HML", "RMW", "CMA"]
    vals = [betas.get(k, 0.0) for k in order]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, vals, color=["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f"][0:len(labels)])
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_ylabel("Beta")
    ax.set_title(title or f"Fama-French {model} Betas")
    for i, v in enumerate(vals):
        ax.text(i, v + (0.01 if v >= 0 else -0.01), f"{v:.2f}", ha='center', va='bottom' if v>=0 else 'top', fontsize=9)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()
