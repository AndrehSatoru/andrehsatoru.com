#!/usr/bin/env python3
"""
Script de demonstração com dados simulados.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import json

# Configurações
OUTPUT_DIR = "portfolio_analysis_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Carregar ativos do arquivo JSON
ASSETS_FILE = os.path.join("portfolio_analysis_inputs", "ativos.json")
with open(ASSETS_FILE, 'r') as f:
    ASSETS = json.load(f)['assets']

# Período de análise
START_DATE = "2023-01-01"
END_DATE = "2024-12-31"

def generate_simulated_data():
    """Gera dados simulados para demonstração."""
    print("Gerando dados simulados para demonstração...")
    
    # Criar datas
    dates = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
    dates = dates[dates.weekday < 5]  # Apenas dias úteis
    
    # Parâmetros para simulação
    np.random.seed(42)  # Para reprodutibilidade
    
    data = {}
    initial_prices = np.random.uniform(10, 100, len(ASSETS))
    
    for i, asset in enumerate(ASSETS):
        # Gerar retornos com diferentes características
        if 'SA' in asset:  # Ações brasileiras
            daily_return = np.random.normal(0.0005, 0.02, len(dates))
        elif asset in ['GE', 'BA', 'NEE']:  # Ações americanas grandes
            daily_return = np.random.normal(0.0003, 0.015, len(dates))
        else:  # Outras ações
            daily_return = np.random.normal(0.0004, 0.025, len(dates))
        
        # Adicionar alguns eventos extremos
        extreme_events = np.random.choice(len(dates), size=5, replace=False)
        for event in extreme_events:
            daily_return[event] += np.random.choice([-0.1, 0.1])
        
        # Calcular preços
        prices = [initial_prices[i]]
        for ret in daily_return:
            prices.append(prices[-1] * (1 + ret))
        
        data[asset] = prices[1:]  # Remover preço inicial
    
    df = pd.DataFrame(data, index=dates)
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
    
    plt.figure(figsize=(20, 12))
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(normalized.columns)))
    
    for i, asset in enumerate(normalized.columns):
        plt.plot(normalized.index, normalized[asset], 
                label=asset, linewidth=2, color=colors[i], alpha=0.8)
    
    plt.title('Comparação de Preços Normalizados (Base 100)', fontsize=18, fontweight='bold')
    plt.xlabel('Data', fontsize=14)
    plt.ylabel('Preço Normalizado', fontsize=14)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
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
    
    plt.figure(figsize=(16, 14))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', 
               center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
               fmt='.2f', annot_kws={'size': 8})
    
    plt.title('Matriz de Correlação', fontsize=18, fontweight='bold')
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
    
    fig, axes = plt.subplots(2, 3, figsize=(20, 14))
    fig.suptitle('Métricas de Risco Comparativas', fontsize=18, fontweight='bold')
    
    metrics = ['Volatility', 'Sharpe', 'Max_DD', 'VaR_95', 'Skewness', 'Kurtosis']
    positions = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]
    
    for i, (metric, pos) in enumerate(zip(metrics, positions)):
        ax = axes[pos[0], pos[1]]
        bars = ax.bar(df_metrics['Asset'], df_metrics[metric], alpha=0.8, 
                     color=plt.cm.Set3(np.linspace(0, 1, len(df_metrics))))
        ax.set_title(metric, fontsize=14, fontweight='bold')
        ax.set_ylabel(metric, fontsize=12)
        ax.tick_params(axis='x', rotation=45, labelsize=10)
        ax.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, value in zip(bars, df_metrics[metric]):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{value:.3f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Salvo em: {output_file}")

def plot_return_distribution(returns, output_file):
    """Gráfico de distribuição de retornos."""
    print(f"Gerando distribuição de retornos...")
    
    n_assets = len(returns.columns)
    n_cols = 4
    n_rows = (n_assets + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5*n_rows))
    fig.suptitle('Distribuição de Retornos', fontsize=18, fontweight='bold')
    
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    colors = plt.cm.Set3(np.linspace(0, 1, n_assets))
    
    for i, asset in enumerate(returns.columns):
        row = i // n_cols
        col = i % n_cols
        ax = axes[row, col]
        
        ret = returns[asset].dropna()
        ax.hist(ret, bins=50, alpha=0.7, color=colors[i], density=True)
        ax.axvline(ret.mean(), color='red', linestyle='--', linewidth=2,
                  label=f'Média: {ret.mean():.4f}')
        ax.axvline(ret.median(), color='green', linestyle='--', linewidth=2,
                  label=f'Mediana: {ret.median():.4f}')
        ax.set_title(f'{asset}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Retorno', fontsize=10)
        ax.set_ylabel('Densidade', fontsize=10)
        ax.legend(fontsize=8)
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
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    fig.suptitle('Análise de Performance', fontsize=18, fontweight='bold')
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(returns.columns)))
    
    # Retornos acumulados
    ax1 = axes[0, 0]
    cumulative = (1 + returns).cumprod()
    for i, asset in enumerate(cumulative.columns):
        ax1.plot(cumulative.index, cumulative[asset], label=asset, 
                linewidth=2, color=colors[i], alpha=0.8)
    ax1.set_title('Retornos Acumulados', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Cumulative Return', fontsize=12)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # Rolling Sharpe
    ax2 = axes[0, 1]
    for i, asset in enumerate(returns.columns):
        rolling_sharpe = returns[asset].rolling(252).mean() / returns[asset].rolling(252).std() * np.sqrt(252)
        ax2.plot(rolling_sharpe.index, rolling_sharpe.values, label=asset, 
                linewidth=2, color=colors[i], alpha=0.8)
    ax2.set_title('Sharpe Ratio Rolante (252 dias)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Sharpe Ratio', fontsize=12)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax2.grid(True, alpha=0.3)
    
    # Rolling Volatility
    ax3 = axes[1, 0]
    for i, asset in enumerate(returns.columns):
        rolling_vol = returns[asset].rolling(30).std() * np.sqrt(252)
        ax3.plot(rolling_vol.index, rolling_vol.values, label=asset, 
                linewidth=2, color=colors[i], alpha=0.8)
    ax3.set_title('Volatilidade Rolante (30 dias)', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Volatilidade Anualizada', fontsize=12)
    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # Drawdown
    ax4 = axes[1, 1]
    for i, asset in enumerate(returns.columns):
        cum_ret = (1 + returns[asset]).cumprod()
        running_max = cum_ret.expanding().max()
        drawdown = (cum_ret / running_max) - 1
        ax4.fill_between(drawdown.index, drawdown.values, 0, alpha=0.7, 
                        label=asset, color=colors[i])
    ax4.set_title('Drawdown', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Drawdown', fontsize=12)
    ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Salvo em: {output_file}")

def plot_efficient_frontier(returns, output_file):
    """Gráfico de fronteira eficiente."""
    print(f"Gerando fronteira eficiente...")
    
    from scipy.optimize import minimize
    
    # Calcular retornos e covariância
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    
    # Gerar portfólios aleatórios
    np.random.seed(42)
    n_portfolios = 5000
    portfolio_returns = []
    portfolio_volatilities = []
    portfolio_sharpes = []
    
    for _ in range(n_portfolios):
        weights = np.random.random(len(returns.columns))
        weights /= np.sum(weights)
        
        portfolio_return = np.sum(weights * mean_returns)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = portfolio_return / portfolio_volatility
        
        portfolio_returns.append(portfolio_return)
        portfolio_volatilities.append(portfolio_volatility)
        portfolio_sharpes.append(sharpe_ratio)
    
    # Encontrar portfólio ótimo
    max_sharpe_idx = np.argmax(portfolio_sharpes)
    min_vol_idx = np.argmin(portfolio_volatilities)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Fronteira eficiente
    scatter = ax1.scatter(portfolio_volatilities, portfolio_returns, 
                         c=portfolio_sharpes, cmap='viridis', alpha=0.6, s=20)
    ax1.scatter(portfolio_volatilities[max_sharpe_idx], portfolio_returns[max_sharpe_idx], 
               color='red', marker='*', s=200, label='Max Sharpe')
    ax1.scatter(portfolio_volatilities[min_vol_idx], portfolio_returns[min_vol_idx], 
               color='blue', marker='*', s=200, label='Min Volatility')
    ax1.set_xlabel('Volatilidade', fontsize=12)
    ax1.set_ylabel('Retorno', fontsize=12)
    ax1.set_title('Fronteira Eficiente', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax1, label='Sharpe Ratio')
    
    # Alocação do portfólio ótimo
    optimal_weights = np.random.random(len(returns.columns))
    optimal_weights /= np.sum(optimal_weights)
    ax2.pie(optimal_weights, labels=returns.columns, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Alocação Ótima (Max Sharpe)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Salvo em: {output_file}")

def main():
    """Função principal."""
    print("DEMONSTRACAO COM DADOS SIMULADOS")
    print("="*80)
    print(f"Diretorio de saida: {OUTPUT_DIR}")
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total de ativos: {len(ASSETS)}")
    
    try:
        # Gerar dados simulados
        prices = generate_simulated_data()
        returns = calculate_returns(prices)
        
        print(f"\nDados simulados gerados:")
        print(f"  - Período: {prices.index[0].strftime('%Y-%m-%d')} a {prices.index[-1].strftime('%Y-%m-%d')}")
        print(f"  - Ativos: {len(prices.columns)}")
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
        
        # 6. Fronteira eficiente
        plot_efficient_frontier(
            returns, 
            os.path.join(OUTPUT_DIR, "efficient_frontier.png")
        )
        
        print("\n" + "="*80)
        print("DEMONSTRACAO CONCLUIDA!")
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
        print(f"   - Fronteira eficiente")
        
        print(f"\nNOTA: Esta demonstração usa dados simulados para mostrar")
        print(f"as capacidades do sistema de visualização avançada.")
        
    except Exception as e:
        print(f"\n[ERRO] Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


