#!/usr/bin/env python3
"""
Script melhorado para fronteira eficiente com otimização adequada.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

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

def generate_simulated_data():
    """Gera dados simulados mais realistas."""
    print("Gerando dados simulados melhorados...")
    
    # Criar datas
    dates = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
    dates = dates[dates.weekday < 5]  # Apenas dias úteis
    
    # Parâmetros mais realistas para simulação
    np.random.seed(42)
    
    data = {}
    initial_prices = np.random.uniform(20, 150, len(ASSETS))
    
    # Diferentes características por tipo de ativo
    for i, asset in enumerate(ASSETS):
        if 'SA' in asset:  # Ações brasileiras
            daily_return = np.random.normal(0.0008, 0.025, len(dates))
        elif asset in ['GE', 'BA', 'NEE']:  # Ações americanas grandes
            daily_return = np.random.normal(0.0005, 0.018, len(dates))
        elif asset in ['EQIX', 'VAL']:  # Ações de crescimento
            daily_return = np.random.normal(0.001, 0.022, len(dates))
        else:  # Outras ações
            daily_return = np.random.normal(0.0006, 0.028, len(dates))
        
        # Adicionar correlação entre alguns ativos (simplificada)
        if i > 0 and i % 3 == 0:  # Correlacionar a cada 3 ativos
            correlation = 0.3 + np.random.random() * 0.4  # Correlação entre 0.3 e 0.7
            # Aplicar correlação simples
            daily_return = correlation * daily_return + np.sqrt(1 - correlation**2) * daily_return
        
        # Adicionar alguns eventos extremos mais realistas
        extreme_events = np.random.choice(len(dates), size=3, replace=False)
        for event in extreme_events:
            daily_return[event] += np.random.choice([-0.08, 0.08])
        
        # Calcular preços
        prices = [initial_prices[i]]
        for ret in daily_return:
            prices.append(prices[-1] * (1 + ret))
        
        data[asset] = prices[1:]
    
    df = pd.DataFrame(data, index=dates)
    return df

def calculate_returns(prices):
    """Calcula retornos."""
    returns = prices.pct_change().dropna()
    return returns

def portfolio_performance(weights, returns, risk_free_rate=0.02):
    """Calcula performance do portfólio."""
    portfolio_return = np.sum(returns.mean() * weights) * 252
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
    sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std
    return portfolio_return, portfolio_std, sharpe_ratio

def negative_sharpe(weights, returns, risk_free_rate=0.02):
    """Função objetivo para maximizar Sharpe ratio."""
    portfolio_return, portfolio_std, _ = portfolio_performance(weights, returns, risk_free_rate)
    return -(portfolio_return - risk_free_rate) / portfolio_std

def portfolio_volatility(weights, returns):
    """Calcula volatilidade do portfólio."""
    return np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))

def optimize_portfolio(returns, target_return=None, target_volatility=None):
    """Otimiza portfólio usando scipy.optimize."""
    n_assets = len(returns.columns)
    
    # Constraints: soma dos pesos = 1
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    
    # Bounds: pesos entre 0 e 1 (long only)
    bounds = tuple((0, 1) for _ in range(n_assets))
    
    # Initial guess: pesos iguais
    initial_guess = np.array([1/n_assets] * n_assets)
    
    if target_return is not None:
        # Otimizar para retorno específico
        constraints = constraints + ({
            'type': 'eq', 
            'fun': lambda x: np.sum(returns.mean() * x) * 252 - target_return
        })
        result = minimize(portfolio_volatility, initial_guess, 
                         method='SLSQP', bounds=bounds, constraints=constraints,
                         args=(returns,))
    else:
        # Maximizar Sharpe ratio
        result = minimize(negative_sharpe, initial_guess,
                         method='SLSQP', bounds=bounds, constraints=constraints,
                         args=(returns,))
    
    return result.x if result.success else initial_guess

def generate_efficient_frontier(returns, n_portfolios=1000):
    """Gera fronteira eficiente otimizada."""
    print("Gerando fronteira eficiente otimizada...")
    
    # Calcular retornos e covariância
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    
    # Encontrar retornos mínimos e máximos
    min_ret = mean_returns.min()
    max_ret = mean_returns.max()
    target_returns = np.linspace(min_ret, max_ret, n_portfolios)
    
    # Otimizar para cada retorno alvo
    efficient_portfolios = []
    
    print(f"  Otimizando {n_portfolios} portfólios...")
    for i, target_ret in enumerate(target_returns):
        if i % 100 == 0:
            print(f"    Progresso: {i}/{n_portfolios}")
        
        try:
            weights = optimize_portfolio(returns, target_return=target_ret)
            portfolio_return, portfolio_std, sharpe_ratio = portfolio_performance(weights, returns)
            
            efficient_portfolios.append({
                'weights': weights,
                'return': portfolio_return,
                'volatility': portfolio_std,
                'sharpe': sharpe_ratio
            })
        except:
            # Se falhar, usar pesos iguais
            weights = np.array([1/len(returns.columns)] * len(returns.columns))
            portfolio_return, portfolio_std, sharpe_ratio = portfolio_performance(weights, returns)
            efficient_portfolios.append({
                'weights': weights,
                'return': portfolio_return,
                'volatility': portfolio_std,
                'sharpe': sharpe_ratio
            })
    
    return efficient_portfolios

def plot_improved_efficient_frontier(returns, output_file):
    """Gráfico de fronteira eficiente melhorado."""
    print(f"Gerando fronteira eficiente melhorada...")
    
    # Gerar fronteira eficiente
    efficient_portfolios = generate_efficient_frontier(returns, n_portfolios=200)
    
    # Extrair dados
    returns_eff = [p['return'] for p in efficient_portfolios]
    volatilities_eff = [p['volatility'] for p in efficient_portfolios]
    sharpes_eff = [p['sharpe'] for p in efficient_portfolios]
    
    # Encontrar portfólios ótimos
    max_sharpe_idx = np.argmax(sharpes_eff)
    min_vol_idx = np.argmin(volatilities_eff)
    
    # Gerar portfólios aleatórios para comparação
    np.random.seed(42)
    random_returns = []
    random_volatilities = []
    random_sharpes = []
    
    for _ in range(5000):
        weights = np.random.random(len(returns.columns))
        weights /= np.sum(weights)
        
        portfolio_return, portfolio_std, sharpe_ratio = portfolio_performance(weights, returns)
        random_returns.append(portfolio_return)
        random_volatilities.append(portfolio_std)
        random_sharpes.append(sharpe_ratio)
    
    # Criar gráfico
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
    
    # Fronteira eficiente
    ax1.scatter(random_volatilities, random_returns, c=random_sharpes, 
               cmap='viridis', alpha=0.3, s=10, label='Portfólios Aleatórios')
    
    ax1.plot(volatilities_eff, returns_eff, 'r-', linewidth=3, 
            label='Fronteira Eficiente', alpha=0.8)
    
    # Portfólios ótimos
    ax1.scatter(volatilities_eff[max_sharpe_idx], returns_eff[max_sharpe_idx], 
               color='red', marker='*', s=300, label='Max Sharpe', 
               edgecolors='black', linewidth=2)
    ax1.scatter(volatilities_eff[min_vol_idx], returns_eff[min_vol_idx], 
               color='blue', marker='*', s=300, label='Min Volatility',
               edgecolors='black', linewidth=2)
    
    ax1.set_xlabel('Volatilidade (Risco)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Retorno Esperado', fontsize=12, fontweight='bold')
    ax1.set_title('Fronteira Eficiente Otimizada', fontsize=16, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Adicionar informações dos portfólios ótimos
    max_sharpe_portfolio = efficient_portfolios[max_sharpe_idx]
    min_vol_portfolio = efficient_portfolios[min_vol_idx]
    
    info_text = f"""Portfólio Max Sharpe:
Retorno: {max_sharpe_portfolio['return']:.2%}
Volatilidade: {max_sharpe_portfolio['volatility']:.2%}
Sharpe: {max_sharpe_portfolio['sharpe']:.3f}

Portfólio Min Vol:
Retorno: {min_vol_portfolio['return']:.2%}
Volatilidade: {min_vol_portfolio['volatility']:.2%}
Sharpe: {min_vol_portfolio['sharpe']:.3f}"""
    
    ax1.text(0.02, 0.98, info_text, transform=ax1.transAxes, 
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    # Alocação do portfólio ótimo
    optimal_weights = max_sharpe_portfolio['weights']
    colors = plt.cm.Set3(np.linspace(0, 1, len(returns.columns)))
    
    wedges, texts, autotexts = ax2.pie(optimal_weights, labels=returns.columns, 
                                      autopct='%1.1f%%', startangle=90, colors=colors)
    
    # Melhorar legibilidade
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(8)
    
    ax2.set_title('Alocação Ótima (Max Sharpe)', fontsize=14, fontweight='bold')
    
    # Adicionar tabela de pesos
    weight_data = []
    for i, asset in enumerate(returns.columns):
        weight_data.append([asset, f"{optimal_weights[i]:.1%}"])
    
    table = ax2.table(cellText=weight_data, colLabels=['Ativo', 'Peso'],
                     cellLoc='center', loc='bottom', bbox=[0, -0.3, 1, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Salvo em: {output_file}")

def plot_risk_return_analysis(returns, output_file):
    """Análise risco-retorno individual dos ativos."""
    print(f"Gerando análise risco-retorno...")
    
    # Calcular métricas individuais
    individual_returns = returns.mean() * 252
    individual_volatilities = returns.std() * np.sqrt(252)
    individual_sharpes = individual_returns / individual_volatilities
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Scatter plot risco-retorno
    scatter = ax1.scatter(individual_volatilities, individual_returns, 
                         c=individual_sharpes, cmap='RdYlGn', s=200, alpha=0.7)
    
    # Adicionar labels para cada ativo
    for i, asset in enumerate(returns.columns):
        ax1.annotate(asset, (individual_volatilities[i], individual_returns[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    ax1.set_xlabel('Volatilidade (Risco)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Retorno Esperado', fontsize=12, fontweight='bold')
    ax1.set_title('Análise Risco-Retorno Individual', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax1, label='Sharpe Ratio')
    
    # Ranking de Sharpe ratios
    sharpe_data = list(zip(returns.columns, individual_sharpes))
    sharpe_data.sort(key=lambda x: x[1], reverse=True)
    
    assets_ranked = [x[0] for x in sharpe_data]
    sharpes_ranked = [x[1] for x in sharpe_data]
    
    bars = ax2.barh(range(len(assets_ranked)), sharpes_ranked, 
                   color=plt.cm.RdYlGn(np.linspace(0, 1, len(assets_ranked))))
    ax2.set_yticks(range(len(assets_ranked)))
    ax2.set_yticklabels(assets_ranked, fontsize=10)
    ax2.set_xlabel('Sharpe Ratio', fontsize=12, fontweight='bold')
    ax2.set_title('Ranking de Sharpe Ratios', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    
    # Adicionar valores nas barras
    for i, (bar, sharpe) in enumerate(zip(bars, sharpes_ranked)):
        ax2.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{sharpe:.3f}', va='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Salvo em: {output_file}")

def main():
    """Função principal."""
    print("FRONTEIRA EFICIENTE MELHORADA")
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
        
        # Gerar gráficos melhorados
        print(f"\nGerando gráficos melhorados...")
        
        # 1. Fronteira eficiente otimizada
        plot_improved_efficient_frontier(
            returns, 
            os.path.join(OUTPUT_DIR, "improved_efficient_frontier.png")
        )
        
        # 2. Análise risco-retorno
        plot_risk_return_analysis(
            returns, 
            os.path.join(OUTPUT_DIR, "risk_return_analysis.png")
        )
        
        print("\n" + "="*80)
        print("ANALISE MELHORADA CONCLUIDA!")
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
        
        print(f"\nMelhorias implementadas:")
        print(f"   - Otimização matemática adequada (scipy.optimize)")
        print(f"   - 200 portfólios na fronteira eficiente")
        print(f"   - Algoritmo SLSQP para otimização")
        print(f"   - Análise risco-retorno individual")
        print(f"   - Ranking de Sharpe ratios")
        print(f"   - Visualização melhorada")
        
    except Exception as e:
        print(f"\n[ERRO] Erro durante a análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
