# core/ta_visualization.py
# Visualização de análise técnica

import io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import List, Optional
from datetime import datetime

from .technical_analysis import moving_averages, macd_series


def plot_price_with_ma(
    prices: pd.DataFrame,
    asset: str,
    windows: List[int] = [5, 21],
    method: str = "sma",
    figsize: tuple = (12, 6),
) -> bytes:
    """Gera gráfico PNG de preços com médias móveis.
    
    Parâmetros:
        prices: DataFrame com preços (índice = datas, colunas = ativos).
        asset: Ticker do ativo a plotar.
        windows: Janelas das médias móveis.
        method: 'sma' ou 'ema'.
        figsize: Tamanho da figura (largura, altura).
    
    Retorna:
        Bytes do PNG gerado.
    """
    if asset not in prices.columns:
        raise ValueError(f"Ativo '{asset}' não encontrado nos dados")
    
    # Calcular MAs
    ma_df = moving_averages(prices[[asset]], windows=windows, method=method)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plotar preço
    ax.plot(ma_df.index, ma_df[asset], label=f"{asset} (Preço)", linewidth=2, color='black')
    
    # Plotar MAs
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    for i, w in enumerate(windows):
        col = f"{asset}_{method.upper()}_{w}"
        if col in ma_df.columns:
            ax.plot(ma_df.index, ma_df[col], label=f"{method.upper()} {w}", 
                   linewidth=1.5, alpha=0.8, color=colors[i % len(colors)])
    
    ax.set_xlabel("Data", fontsize=12)
    ax.set_ylabel("Preço", fontsize=12)
    ax.set_title(f"{asset} - Preços e Médias Móveis ({method.upper()})", fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def plot_macd(
    prices: pd.DataFrame,
    asset: str,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    figsize: tuple = (12, 8),
) -> bytes:
    """Gera gráfico PNG de preços com MACD.
    
    Parâmetros:
        prices: DataFrame com preços.
        asset: Ticker do ativo.
        fast, slow, signal: Parâmetros do MACD.
        figsize: Tamanho da figura.
    
    Retorna:
        Bytes do PNG gerado.
    """
    if asset not in prices.columns:
        raise ValueError(f"Ativo '{asset}' não encontrado nos dados")
    
    # Calcular MACD
    macd_df = macd_series(prices[asset], fast=fast, slow=slow, signal=signal)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize, sharex=True, 
                                     gridspec_kw={'height_ratios': [2, 1]})
    
    # Subplot 1: Preços
    ax1.plot(prices.index, prices[asset], label=f"{asset} (Preço)", 
            linewidth=2, color='black')
    ax1.set_ylabel("Preço", fontsize=12)
    ax1.set_title(f"{asset} - Preços e MACD", fontsize=14, fontweight='bold')
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: MACD
    ax2.plot(macd_df.index, macd_df['macd'], label='MACD', linewidth=1.5, color='blue')
    ax2.plot(macd_df.index, macd_df['signal'], label='Signal', linewidth=1.5, color='red')
    ax2.bar(macd_df.index, macd_df['hist'], label='Histogram', alpha=0.3, color='gray')
    ax2.axhline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
    ax2.set_xlabel("Data", fontsize=12)
    ax2.set_ylabel("MACD", fontsize=12)
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def plot_combined_ta(
    prices: pd.DataFrame,
    asset: str,
    ma_windows: List[int] = [5, 21],
    ma_method: str = "sma",
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    figsize: tuple = (14, 10),
) -> bytes:
    """Gera gráfico combinado: preços + MAs + MACD.
    
    Parâmetros:
        prices: DataFrame com preços.
        asset: Ticker do ativo.
        ma_windows: Janelas das médias móveis.
        ma_method: 'sma' ou 'ema'.
        macd_fast, macd_slow, macd_signal: Parâmetros do MACD.
        figsize: Tamanho da figura.
    
    Retorna:
        Bytes do PNG gerado.
    """
    if asset not in prices.columns:
        raise ValueError(f"Ativo '{asset}' não encontrado nos dados")
    
    # Calcular indicadores
    ma_df = moving_averages(prices[[asset]], windows=ma_windows, method=ma_method)
    macd_df = macd_series(prices[asset], fast=macd_fast, slow=macd_slow, signal=macd_signal)
    
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(3, 1, height_ratios=[2, 1, 1], hspace=0.3)
    
    # Subplot 1: Preços + MAs
    ax1 = fig.add_subplot(gs[0])
    ax1.plot(ma_df.index, ma_df[asset], label=f"{asset} (Preço)", 
            linewidth=2, color='black', zorder=3)
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    for i, w in enumerate(ma_windows):
        col = f"{asset}_{ma_method.upper()}_{w}"
        if col in ma_df.columns:
            ax1.plot(ma_df.index, ma_df[col], label=f"{ma_method.upper()} {w}", 
                   linewidth=1.5, alpha=0.8, color=colors[i % len(colors)], zorder=2)
    
    ax1.set_ylabel("Preço", fontsize=12)
    ax1.set_title(f"{asset} - Análise Técnica Completa", fontsize=14, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Subplot 2: Volume (se disponível) ou espaço reservado
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    # Placeholder - pode ser expandido para volume real
    ax2.text(0.5, 0.5, 'Volume (não disponível)', 
            ha='center', va='center', transform=ax2.transAxes, fontsize=10, alpha=0.5)
    ax2.set_ylabel("Volume", fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Subplot 3: MACD
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.plot(macd_df.index, macd_df['macd'], label='MACD', linewidth=1.5, color='blue')
    ax3.plot(macd_df.index, macd_df['signal'], label='Signal', linewidth=1.5, color='red')
    ax3.bar(macd_df.index, macd_df['hist'], label='Histogram', alpha=0.3, color='gray')
    ax3.axhline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
    ax3.set_xlabel("Data", fontsize=12)
    ax3.set_ylabel("MACD", fontsize=12)
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()
