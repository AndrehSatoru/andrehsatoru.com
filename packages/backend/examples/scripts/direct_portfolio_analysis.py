#!/usr/bin/env python3
"""
Script para análise direta de portfólio sem usar a API.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import yfinance as yf
import os

# Configurações
OUTPUT_DIR = "portfolio_analysis_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Ativos especificados
ASSETS = [
    "EQTL3.SA", "CPFE3.SA", "EMBR3.SA", "DIRR3.SA", "LAVV3.SA", 
    "AZZA3.SA", "PRIO3.SA", "TFCO4.SA", "VAL", "SBSP3.SA", 
    "EQIX", "GE", "BA", "MC.PA", "ITX.MC", "NEE", "VALE3.SA", "AURA33.SA"
]

# Período de análise
START_DATE = "2023-01-01"
END_DATE = "2024-12-31"

def fetch_data():
    """Busca dados dos ativos."""
    print("Buscando dados dos ativos...")
    data = {}
    
    for asset in ASSETS:
        try:
            print(f"  - {asset}")
            ticker = yf.Ticker(asset)
            hist = ticker.history(start=START_DATE, end=END_DATE)
            if not hist.empty:
                data[asset] = hist['Close']
            else:
                print(f"    [AVISO] Sem dados para {asset}")
        except Exception as e:
            print(f"    [ERRO] Erro ao buscar {asset}: {e}")
    
    if not data:
        raise ValueError("Nenhum dado foi obtido")
    
    df = pd.DataFrame(data)
    df = df.dropna()
    
    print(f"Dados obtidos: {len(df)} dias, {len(df.columns)} ativos")
    return df

def calculate_returns(prices):
    """Calcula retornos."""
    returns = prices.pct_change().dropna()
    return returns

def plot_price_comparison(prices, output_file):
    """Gráfico de comparação de preços."""
    print(f"Gerando gráfico de comparação de preços...")
    
    # Normalizar para base 100
    normalized = (prices / prices.iloc[0]) * 100
    
    plt.figure(figsize=(16, 10))
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(normalized.columns)))
    
    for i, asset in enumerate(normalized.columns):
        plt.plot(normalized.index, normalized[asset], 
                label=asset, linewidth=2, color=colors[i], alpha=0.8)
    
    plt.title('Comparação de Preços Normalizados (Base 100)', fontsize=16, fontweight='bold')
    plt.xlabel('Data', fontsize=12)
    plt.ylabel('Preço Normalizado', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Salvo em: {output_file}")

def plot_correlation_heatmap(returns, output_file):
    """Gráfico de correlação."""
    print(f"Gerando matriz de correlação...")
    
    corr_matrix = returns.corr()
    
    plt.figure(figsize=(14, 12))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', 
               center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
    
    plt.title('Matriz de Correlação', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Salvo em: {output_file}")

def plot_risk_metrics(returns, output_file):
    """Gráfico de métricas de risco."""
    print(f"Gerando métricas de risco...")
    
    metrics_data = []
    for asset in returns.columns:
        ret = returns[asset].dropna()
        metrics_data.append({
            'Asset': asset,
            'Volatility': ret.std() * np.sqrt(252),
            'Sharpe': ret.mean() / ret.std() * np.sqrt(252),
            'Max_DD': ((1 + ret).cumprod() / (1 + ret).cumprod().expanding().max() - 1).min(),
            'VaR_95': ret.quantile(0.05),
            'Skewness': ret.skew(),
            'Kurtosis': ret.kurtosis()
        })
    
    df_metrics = pd.DataFrame(metrics_data)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Métricas de Risco Comparativas', fontsize=16, fontweight='bold')
    
    metrics = ['Volatility', 'Sharpe', 'Max_DD', 'VaR_95', 'Skewness', 'Kurtosis']
    positions = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]
    
    for i, (metric, pos) in enumerate(zip(metrics, positions)):
        ax = axes[pos[0], pos[1]]
        ax.bar(df_metrics['Asset'], df_metrics[metric], alpha=0.8)
        ax.set_title(metric)
        ax.set_ylabel(metric)
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Salvo em: {output_file}")

def plot_return_distribution(returns, output_file):
    """Gráfico de distribuição de retornos."""
    print(f"Gerando distribuição de retornos...")
    
    n_assets = len(returns.columns)
    n_cols = 3
    n_rows = (n_assets + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 6*n_rows))
    fig.suptitle('Distribuição de Retornos', fontsize=16, fontweight='bold')
    
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    colors = plt.cm.Set3(np.linspace(0, 1, n_assets))
    
    for i, asset in enumerate(returns.columns):
        row = i // n_cols
        col = i % n_cols
        ax = axes[row, col]
        
        ret = returns[asset].dropna()
        ax.hist(ret, bins=50, alpha=0.7, color=colors[i], density=True)
        ax.axvline(ret.mean(), color='red', linestyle='--', 
                  label=f'Média: {ret.mean():.4f}')
        ax.axvline(ret.median(), color='green', linestyle='--', 
                  label=f'Mediana: {ret.median():.4f}')
        ax.set_title(f'{asset}')
        ax.set_xlabel('Retorno')
        ax.set_ylabel('Densidade')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    # Remover eixos vazios
    for i in range(n_assets, n_rows * n_cols):
        row = i // n_cols
        col = i % n_cols
        axes[row, col].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Salvo em: {output_file}")

def plot_performance_analysis(returns, output_file):
    """Gráfico de análise de performance."""
    print(f"Gerando análise de performance...")
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Análise de Performance', fontsize=16, fontweight='bold')
    
    # Retornos acumulados
    ax1 = axes[0, 0]
    cumulative = (1 + returns).cumprod()
    for asset in cumulative.columns:
        ax1.plot(cumulative.index, cumulative[asset], label=asset, linewidth=2)
    ax1.set_title('Retornos Acumulados')
    ax1.set_ylabel('Cumulative Return')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Rolling Sharpe
    ax2 = axes[0, 1]
    for asset in returns.columns:
        rolling_sharpe = returns[asset].rolling(252).mean() / returns[asset].rolling(252).std() * np.sqrt(252)
        ax2.plot(rolling_sharpe.index, rolling_sharpe.values, label=asset, linewidth=2)
    ax2.set_title('Sharpe Ratio Rolante (252 dias)')
    ax2.set_ylabel('Sharpe Ratio')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # Rolling Volatility
    ax3 = axes[1, 0]
    for asset in returns.columns:
        rolling_vol = returns[asset].rolling(30).std() * np.sqrt(252)
        ax3.plot(rolling_vol.index, rolling_vol.values, label=asset, linewidth=2)
    ax3.set_title('Volatilidade Rolante (30 dias)')
    ax3.set_ylabel('Volatilidade Anualizada')
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    # Drawdown
    ax4 = axes[1, 1]
    for asset in returns.columns:
        cum_ret = (1 + returns[asset]).cumprod()
        running_max = cum_ret.expanding().max()
        drawdown = (cum_ret / running_max) - 1
        ax4.fill_between(drawdown.index, drawdown.values, 0, alpha=0.7, label=asset)
    ax4.set_title('Drawdown')
    ax4.set_ylabel('Drawdown')
    ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Salvo em: {output_file}")

def main():
    """Função principal."""
    print("ANALISE DIRETA DE PORTFOLIO")
    print("="*80)
    print(f"Diretorio de saida: {OUTPUT_DIR}")
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total de ativos: {len(ASSETS)}")
    
    try:
        # Buscar dados
        prices = fetch_data()
        returns = calculate_returns(prices)
        
        print(f"\nDados processados:")
        print(f"  - Período: {prices.index[0].strftime('%Y-%m-%d')} a {prices.index[-1].strftime('%Y-%m-%d')}")
        print(f"  - Ativos com dados: {len(prices.columns)}")
        print(f"  - Dias úteis: {len(prices)}")
        
        # Gerar gráficos
        print(f"\nGerando gráficos...")
        
        # 1. Comparação de preços
        plot_price_comparison(
            prices, 
            os.path.join(OUTPUT_DIR, "price_comparison_normalized.png")
        )
        
        # 2. Matriz de correlação
        plot_correlation_heatmap(
            returns, 
            os.path.join(OUTPUT_DIR, "correlation_heatmap.png")
        )
        
        # 3. Métricas de risco
        plot_risk_metrics(
            returns, 
            os.path.join(OUTPUT_DIR, "risk_metrics_comparison.png")
        )
        
        # 4. Distribuição de retornos
        plot_return_distribution(
            returns, 
            os.path.join(OUTPUT_DIR, "return_distribution.png")
        )
        
        # 5. Análise de performance
        plot_performance_analysis(
            returns, 
            os.path.join(OUTPUT_DIR, "performance_analysis.png")
        )
        
        print("\n" + "="*80)
        print("ANALISE CONCLUIDA!")
        print("="*80)
        print(f"Arquivos gerados em: {OUTPUT_DIR}")
        print(f"Total de ativos analisados: {len(prices.columns)}")
        print(f"Concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Listar arquivos gerados
        files = os.listdir(OUTPUT_DIR)
        print(f"\nArquivos gerados ({len(files)}):")
        for file in sorted(files):
            file_path = os.path.join(OUTPUT_DIR, file)
            size = os.path.getsize(file_path)
            print(f"   - {file} ({size:,} bytes)")
        
        # Resumo dos ativos
        print(f"\nAtivos analisados:")
        for i, asset in enumerate(prices.columns, 1):
            print(f"   {i:2d}. {asset}")
        
        print(f"\nTipos de análise gerados:")
        print(f"   - Comparação de preços normalizados")
        print(f"   - Matriz de correlação")
        print(f"   - Métricas de risco comparativas")
        print(f"   - Distribuição de retornos")
        print(f"   - Análise de performance")
        
    except Exception as e:
        print(f"\n[ERRO] Erro durante a análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


