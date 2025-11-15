# core/advanced_visualization.py
# Sistema avançado de visualização financeira

import io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from typing import List, Optional, Dict, Tuple, Any
from datetime import datetime, timedelta
import warnings
import logging
warnings.filterwarnings('ignore')

# Configurar estilo
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class AdvancedVisualizer:
    """Sistema avançado de visualização financeira com múltiplos tipos de gráficos."""
    
    def __init__(self, style: str = 'seaborn-v0_8', figsize: Tuple[int, int] = (12, 8)):
        self.style = style
        self.figsize = figsize
        plt.style.use(style)
        
    def _save_plot(self, fig, dpi: int = 150) -> bytes:
        """Salva figura como bytes PNG."""
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        return buf.read()
    
    # ==================== GRÁFICOS DE PREÇOS ====================
    
    def plot_candlestick(self, prices: pd.DataFrame, asset: str, 
                        volume: Optional[pd.Series] = None) -> bytes:
        """Gráfico de candlestick com volume."""
        if asset not in prices.columns:
            raise ValueError(f"Ativo '{asset}' não encontrado")
        
        # Simular OHLC se só tivermos Close
        if 'Open' not in prices.columns:
            # Usar close como aproximação
            ohlc = prices[[asset]].copy()
            ohlc['Open'] = ohlc[asset].shift(1).fillna(ohlc[asset])
            ohlc['High'] = ohlc[asset] * (1 + np.random.normal(0, 0.01, len(ohlc)))
            ohlc['Low'] = ohlc[asset] * (1 - np.random.normal(0, 0.01, len(ohlc)))
            ohlc['Close'] = ohlc[asset]
        else:
            ohlc = prices[['Open', 'High', 'Low', 'Close']]
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 10), 
                                gridspec_kw={'height_ratios': [3, 1]})
        
        # Candlestick
        ax1 = axes[0]
        for i, (date, row) in enumerate(ohlc.iterrows()):
            color = 'green' if row['Close'] >= row['Open'] else 'red'
            # Corpo da vela
            ax1.bar(date, row['Close'] - row['Open'], bottom=row['Open'], 
                   color=color, alpha=0.7, width=0.8)
            # Pavios
            ax1.plot([date, date], [row['Low'], row['High']], color='black', linewidth=1)
        
        ax1.set_title(f'{asset} - Candlestick Chart', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Preço', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # Volume
        ax2 = axes[1]
        if volume is not None:
            ax2.bar(volume.index, volume.values, alpha=0.6, color='blue')
        else:
            # Volume simulado
            vol_sim = np.random.exponential(1000000, len(ohlc))
            ax2.bar(ohlc.index, vol_sim, alpha=0.6, color='blue')
        
        ax2.set_ylabel('Volume', fontsize=12)
        ax2.set_xlabel('Data', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Formatar eixos
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        return self._save_plot(fig)
    
    def plot_price_comparison(self, prices: pd.DataFrame, assets: List[str], 
                            normalize: bool = True) -> bytes:
        """Comparação de preços de múltiplos ativos."""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(assets)))
        
        for i, asset in enumerate(assets):
            if asset in prices.columns:
                series = prices[asset].dropna()
                if normalize:
                    # Normalizar para base 100
                    series = (series / series.iloc[0]) * 100
                    label = f"{asset} (Normalizado)"
                else:
                    label = asset
                
                ax.plot(series.index, series.values, label=label, 
                       linewidth=2, color=colors[i], alpha=0.8)
        
        ax.set_title('Comparação de Preços', fontsize=16, fontweight='bold')
        ax.set_ylabel('Preço' + (' (Base 100)' if normalize else ''), fontsize=12)
        ax.set_xlabel('Data', fontsize=12)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Formatar eixos
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        return self._save_plot(fig)
    
    # ==================== GRÁFICOS DE RISCO ====================
    
    def plot_var_evolution(self, returns: pd.Series, var_values: pd.Series, 
                          alpha: float = 0.95) -> bytes:
        """Evolução do VaR ao longo do tempo."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                      gridspec_kw={'height_ratios': [2, 1]})
        
        # Retornos
        ax1.plot(returns.index, returns.values, alpha=0.7, color='blue', linewidth=1)
        ax1.fill_between(returns.index, -var_values.values, 0, 
                        alpha=0.3, color='red', label=f'VaR {alpha*100}%')
        ax1.axhline(0, color='black', linestyle='--', alpha=0.5)
        ax1.set_title(f'Evolução do VaR {alpha*100}%', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Retornos', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # VaR
        ax2.plot(var_values.index, var_values.values, color='red', linewidth=2)
        ax2.set_ylabel('VaR', fontsize=12)
        ax2.set_xlabel('Data', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        return self._save_plot(fig)
    
    def plot_drawdown(self, returns: pd.Series, title: str = "Drawdown Analysis") -> bytes:
        """Análise de drawdown."""
        # Calcular drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative / running_max) - 1
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                      gridspec_kw={'height_ratios': [2, 1]})
        
        # Performance
        ax1.plot(cumulative.index, cumulative.values, label='Cumulative Return', 
                linewidth=2, color='blue')
        ax1.plot(running_max.index, running_max.values, label='Peak', 
                linewidth=2, color='green', linestyle='--')
        ax1.set_title('Performance e Drawdown', fontsize=16, fontweight='bold')
        ax1.set_ylabel('Cumulative Return', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Drawdown
        ax2.fill_between(drawdown.index, drawdown.values, 0, 
                        alpha=0.7, color='red', label='Drawdown')
        ax2.set_ylabel('Drawdown', fontsize=12)
        ax2.set_xlabel('Data', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Adicionar estatísticas
        max_dd = drawdown.min()
        ax2.text(0.02, 0.95, f'Max Drawdown: {max_dd:.2%}', 
                transform=ax2.transAxes, fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        
        return self._save_plot(fig)
    
    def plot_risk_metrics(self, returns: pd.DataFrame, assets: List[str]) -> bytes:
        """Métricas de risco comparativas."""
        metrics = {}
        for asset in assets:
            if asset in returns.columns:
                ret = returns[asset].dropna()
                metrics[asset] = {
                    'Volatility': ret.std() * np.sqrt(252),
                    'Sharpe': ret.mean() / ret.std() * np.sqrt(252),
                    'Max DD': ((1 + ret).cumprod() / (1 + ret).cumprod().expanding().max() - 1).min(),
                    'VaR 95%': ret.quantile(0.05)
                }
        
        df_metrics = pd.DataFrame(metrics).T
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Métricas de Risco Comparativas', fontsize=16, fontweight='bold')
        
        # Volatilidade
        axes[0,0].bar(df_metrics.index, df_metrics['Volatility'], color='skyblue')
        axes[0,0].set_title('Volatilidade Anualizada')
        axes[0,0].set_ylabel('Volatilidade')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Sharpe Ratio
        axes[0,1].bar(df_metrics.index, df_metrics['Sharpe'], color='lightgreen')
        axes[0,1].set_title('Sharpe Ratio')
        axes[0,1].set_ylabel('Sharpe Ratio')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # Max Drawdown
        axes[1,0].bar(df_metrics.index, df_metrics['Max DD'], color='salmon')
        axes[1,0].set_title('Maximum Drawdown')
        axes[1,0].set_ylabel('Max Drawdown')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # VaR
        axes[1,1].bar(df_metrics.index, df_metrics['VaR 95%'], color='orange')
        axes[1,1].set_title('VaR 95%')
        axes[1,1].set_ylabel('VaR 95%')
        axes[1,1].tick_params(axis='x', rotation=45)
        
        for ax in axes.flat:
            ax.grid(True, alpha=0.3)
        
        return self._save_plot(fig)
    
    # ==================== GRÁFICOS DE CORRELAÇÃO ====================
    
    def plot_correlation_heatmap(self, returns: pd.DataFrame, 
                                assets: Optional[List[str]] = None, 
                                window: Optional[int] = None) -> bytes:
        """Heatmap de correlação entre ativos ou correlação rolante."""
        if assets:
            data = returns[assets]
        else:
            data = returns
        
        if window:
            if len(assets) != 2:
                raise ValueError("Correlação rolante requer exatamente 2 ativos.")
            
            asset1_returns = data[assets[0]]
            asset2_returns = data[assets[1]]
            
            rolling_corr = asset1_returns.rolling(window=window).corr(asset2_returns)
            
            fig, ax = plt.subplots(figsize=(14, 6))
            ax.plot(rolling_corr.index, rolling_corr.values, linewidth=2, color='blue')
            ax.axhline(0, color='black', linestyle='--', alpha=0.5)
            ax.set_title(f'Correlação Rolante {assets[0]} vs {assets[1]} (Janela: {window} dias)', 
                        fontsize=14, fontweight='bold')
            ax.set_ylabel('Correlação', fontsize=12)
            ax.set_xlabel('Data', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            return self._save_plot(fig)
        else:
            corr_matrix = data.corr()
            
            fig, ax = plt.subplots(figsize=(10, 8))
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
            
            sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', 
                       center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
            
            ax.set_title('Matriz de Correlação', fontsize=16, fontweight='bold')
            
            return self._save_plot(fig)
    
    def plot_rolling_correlation(self, returns: pd.DataFrame, 
                                 asset1: str, asset2: str, window: int = 30) -> bytes:
        """Correlação rolante entre dois ativos."""
        if asset1 not in returns.columns or asset2 not in returns.columns:
            raise ValueError("Ativos não encontrados nos dados")
        
        rolling_corr = returns[asset1].rolling(window=window).corr(returns[asset2])
        
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(rolling_corr.index, rolling_corr.values, linewidth=2, color='blue')
        ax.axhline(0, color='black', linestyle='--', alpha=0.5)
        ax.set_title(f'Correlação Rolante {asset1} vs {asset2} (Janela: {window} dias)', 
                    fontsize=14, fontweight='bold')
        ax.set_ylabel('Correlação', fontsize=12)
        ax.set_xlabel('Data', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        return self._save_plot(fig)

    def plot_rolling_beta(self, rolling_beta_series: pd.Series, asset: str, benchmark: str, window: int) -> bytes:
        """Plota o beta rolante."""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        ax.plot(rolling_beta_series.index, rolling_beta_series.values, linewidth=2, color='blue', label=f'Beta Rolante ({asset} vs {benchmark})')
        ax.axhline(1.0, color='red', linestyle='--', linewidth=1.5, label='Beta = 1.0')
        ax.axhline(0.0, color='black', linestyle='-', linewidth=1.0)
        
        ax.set_title(f'Beta Rolante ({window} dias) - {asset} vs {benchmark}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Data', fontsize=12)
        ax.set_ylabel('Beta', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return self._save_plot(fig)

    def plot_underwater(self, returns: pd.Series, asset: str) -> bytes:
        """Gera um gráfico de drawdown (underwater plot)."""
        cumulative_returns = (1 + returns).cumprod()
        peak = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns / peak) - 1

        fig, ax = plt.subplots(figsize=self.figsize)
        
        ax.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
        ax.plot(drawdown.index, drawdown, color='red', alpha=0.8, linewidth=1.5)
        
        max_dd = drawdown.min()
        
        ax.set_title(f'Underwater Plot (Drawdown) - {asset}', fontsize=16, fontweight='bold')
        ax.set_ylabel('Drawdown', fontsize=12)
        ax.set_xlabel('Data', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter('{:.0%}'.format))

        ax.text(0.05, 0.05, f'Max Drawdown: {max_dd:.2%}', transform=ax.transAxes, fontsize=12, verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
        
        return self._save_plot(fig)
    
    # ==================== GRÁFICOS DE DISTRIBUIÇÃO ====================
    
    def plot_return_distribution(self, returns: pd.DataFrame, 
                                assets: List[str]) -> bytes:
        """Distribuição de retornos."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Distribuição de Retornos', fontsize=16, fontweight='bold')
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(assets)))
        
        for i, asset in enumerate(assets):
            if asset in returns.columns:
                ret = returns[asset].dropna()
                
                # Histograma
                ax = axes[i//2, i%2]
                ax.hist(ret, bins=50, alpha=0.7, color=colors[i], density=True)
                ax.axvline(ret.mean(), color='red', linestyle='--', 
                          label=f'Média: {ret.mean():.4f}')
                ax.axvline(ret.median(), color='green', linestyle='--', 
                          label=f'Mediana: {ret.median():.4f}')
                ax.set_title(f'{asset} - Distribuição de Retornos')
                ax.set_xlabel('Retorno')
                ax.set_ylabel('Densidade')
                ax.legend()
                ax.grid(True, alpha=0.3)
        
        return self._save_plot(fig)
    
    def plot_qq_plot(self, returns: pd.Series, asset: str) -> bytes:
        """Q-Q plot para verificar normalidade."""
        from scipy import stats
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Histograma com curva normal
        ax1.hist(returns, bins=50, density=True, alpha=0.7, color='skyblue')
        mu, sigma = returns.mean(), returns.std()
        x = np.linspace(returns.min(), returns.max(), 100)
        ax1.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
                label=f'Normal(μ={mu:.4f}, σ={sigma:.4f})')
        ax1.set_title(f'{asset} - Distribuição vs Normal')
        ax1.set_xlabel('Retorno')
        ax1.set_ylabel('Densidade')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Q-Q plot
        stats.probplot(returns, dist="norm", plot=ax2)
        ax2.set_title(f'{asset} - Q-Q Plot')
        ax2.grid(True, alpha=0.3)
        
        return self._save_plot(fig)
    
    # ==================== GRÁFICOS DE PERFORMANCE ====================
    
    def plot_performance_metrics(self, returns: pd.DataFrame, 
                                benchmark: Optional[pd.Series] = None) -> bytes:
        """Métricas de performance comparativas."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Análise de Performance', fontsize=16, fontweight='bold')
        
        # Retornos acumulados
        ax1 = axes[0, 0]
        cumulative = (1 + returns).cumprod()
        for col in cumulative.columns:
            ax1.plot(cumulative.index, cumulative[col], label=col, linewidth=2)
        if benchmark is not None:
            bench_cum = (1 + benchmark).cumprod()
            ax1.plot(bench_cum.index, bench_cum.values, label='Benchmark', 
                    linewidth=2, linestyle='--', color='black')
        ax1.set_title('Retornos Acumulados')
        ax1.set_ylabel('Cumulative Return')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Rolling Sharpe
        ax2 = axes[0, 1]
        for col in returns.columns:
            rolling_sharpe = returns[col].rolling(252).mean() / returns[col].rolling(252).std() * np.sqrt(252)
            ax2.plot(rolling_sharpe.index, rolling_sharpe.values, label=col, linewidth=2)
        ax2.set_title('Sharpe Ratio Rolante (252 dias)')
        ax2.set_ylabel('Sharpe Ratio')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Rolling Volatility
        ax3 = axes[1, 0]
        for col in returns.columns:
            rolling_vol = returns[col].rolling(30).std() * np.sqrt(252)
            ax3.plot(rolling_vol.index, rolling_vol.values, label=col, linewidth=2)
        ax3.set_title('Volatilidade Rolante (30 dias)')
        ax3.set_ylabel('Volatilidade Anualizada')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Drawdown
        ax4 = axes[1, 1]
        for col in returns.columns:
            cum_ret = (1 + returns[col]).cumprod()
            running_max = cum_ret.expanding().max()
            drawdown = (cum_ret / running_max) - 1
            ax4.fill_between(drawdown.index, drawdown.values, 0, alpha=0.7, label=col)
        ax4.set_title('Drawdown')
        ax4.set_ylabel('Drawdown')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        return self._save_plot(fig)
    
    # ==================== GRÁFICOS DE OTIMIZAÇÃO ====================
    
    def plot_efficient_frontier_advanced(self, returns: pd.DataFrame, 
                                       assets: List[str], n_portfolios: int = 1000) -> bytes:
        """Fronteira eficiente avançada com múltiplas métricas."""
        from scipy.optimize import minimize
        
        # Calcular retornos e covariância
        ret_data = returns[assets].dropna()
        mean_returns = ret_data.mean() * 252
        cov_matrix = ret_data.cov() * 252
        
        # Gerar portfólios aleatórios
        np.random.seed(42)
        portfolio_returns = []
        portfolio_volatilities = []
        portfolio_sharpes = []
        portfolio_weights = []
        
        for _ in range(n_portfolios):
            weights = np.random.random(len(assets))
            weights /= np.sum(weights)
            
            portfolio_return = np.sum(weights * mean_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = portfolio_return / portfolio_volatility
            
            portfolio_returns.append(portfolio_return)
            portfolio_volatilities.append(portfolio_volatility)
            portfolio_sharpes.append(sharpe_ratio)
            portfolio_weights.append(weights)
        
        # Encontrar portfólio ótimo
        max_sharpe_idx = np.argmax(portfolio_sharpes)
        min_vol_idx = np.argmin(portfolio_volatilities)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Fronteira eficiente
        scatter = ax1.scatter(portfolio_volatilities, portfolio_returns, 
                             c=portfolio_sharpes, cmap='viridis', alpha=0.6, s=20)
        ax1.scatter(portfolio_volatilities[max_sharpe_idx], portfolio_returns[max_sharpe_idx], 
                   color='red', marker='*', s=200, label='Max Sharpe')
        ax1.scatter(portfolio_volatilities[min_vol_idx], portfolio_returns[min_vol_idx], 
                   color='blue', marker='*', s=200, label='Min Volatility')
        ax1.set_xlabel('Volatilidade')
        ax1.set_ylabel('Retorno')
        ax1.set_title('Fronteira Eficiente')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=ax1, label='Sharpe Ratio')
        
        # Alocação do portfólio ótimo
        optimal_weights = portfolio_weights[max_sharpe_idx]
        ax2.pie(optimal_weights, labels=assets, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Alocação Ótima (Max Sharpe)')
        
        return self._save_plot(fig)
    
    # ==================== DASHBOARD COMPLETO ====================
    
    def plot_comprehensive_dashboard(self, prices: pd.DataFrame, returns: pd.DataFrame, 
                                   assets: List[str], benchmark: Optional[pd.Series] = None) -> bytes:
        """Dashboard completo com múltiplas visualizações."""
        fig = plt.figure(figsize=(20, 16))
        gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
        # 1. Preços normalizados
        ax1 = fig.add_subplot(gs[0, :2])
        for asset in assets:
            if asset in prices.columns:
                norm_price = (prices[asset] / prices[asset].iloc[0]) * 100
                ax1.plot(norm_price.index, norm_price.values, label=asset, linewidth=2)
        if benchmark is not None:
            norm_bench = (benchmark / benchmark.iloc[0]) * 100
            ax1.plot(norm_bench.index, norm_bench.values, label='Benchmark', 
                    linewidth=2, linestyle='--', color='black')
        ax1.set_title('Preços Normalizados (Base 100)', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Retornos acumulados
        ax2 = fig.add_subplot(gs[0, 2:])
        cumulative = (1 + returns[assets]).cumprod()
        for asset in assets:
            if asset in cumulative.columns:
                ax2.plot(cumulative.index, cumulative[asset], label=asset, linewidth=2)
        ax2.set_title('Retornos Acumulados', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Volatilidade rolante
        ax3 = fig.add_subplot(gs[1, :2])
        for asset in assets:
            if asset in returns.columns:
                rolling_vol = returns[asset].rolling(30).std() * np.sqrt(252)
                ax3.plot(rolling_vol.index, rolling_vol.values, label=asset, linewidth=2)
        ax3.set_title('Volatilidade Rolante (30 dias)', fontweight='bold')
        ax3.set_ylabel('Volatilidade Anualizada')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Correlação
        ax4 = fig.add_subplot(gs[1, 2:])
        corr_matrix = returns[assets].corr()
        im = ax4.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        ax4.set_xticks(range(len(assets)))
        ax4.set_yticks(range(len(assets)))
        ax4.set_xticklabels(assets, rotation=45)
        ax4.set_yticklabels(assets)
        ax4.set_title('Matriz de Correlação', fontweight='bold')
        
        # Adicionar valores na matriz
        for i in range(len(assets)):
            for j in range(len(assets)):
                text = ax4.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                              ha="center", va="center", color="black", fontweight='bold')
        
        plt.colorbar(im, ax=ax4)
        
        # 5. Distribuição de retornos
        ax5 = fig.add_subplot(gs[2, :2])
        for asset in assets:
            if asset in returns.columns:
                ret = returns[asset].dropna()
                ax5.hist(ret, bins=50, alpha=0.6, label=asset, density=True)
        ax5.set_title('Distribuição de Retornos', fontweight='bold')
        ax5.set_xlabel('Retorno')
        ax5.set_ylabel('Densidade')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. Drawdown
        ax6 = fig.add_subplot(gs[2, 2:])
        for asset in assets:
            if asset in returns.columns:
                cum_ret = (1 + returns[asset]).cumprod()
                running_max = cum_ret.expanding().max()
                drawdown = (cum_ret / running_max) - 1
                ax6.fill_between(drawdown.index, drawdown.values, 0, alpha=0.7, label=asset)
        ax6.set_title('Drawdown', fontweight='bold')
        ax6.set_ylabel('Drawdown')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. Métricas de risco
        ax7 = fig.add_subplot(gs[3, :])
        metrics_data = []
        for asset in assets:
            if asset in returns.columns:
                ret = returns[asset].dropna()
                metrics_data.append({
                    'Asset': asset,
                    'Volatility': ret.std() * np.sqrt(252),
                    'Sharpe': ret.mean() / ret.std() * np.sqrt(252),
                    'Max DD': ((1 + ret).cumprod() / (1 + ret).cumprod().expanding().max() - 1).min(),
                    'VaR 95%': ret.quantile(0.05)
                })
        
        metrics_df = pd.DataFrame(metrics_data)
        x = np.arange(len(assets))
        width = 0.2
        
        ax7.bar(x - width, metrics_df['Volatility'], width, label='Volatilidade', alpha=0.8)
        ax7.bar(x, metrics_df['Sharpe'], width, label='Sharpe Ratio', alpha=0.8)
        ax7.bar(x + width, -metrics_df['Max DD'], width, label='Max Drawdown', alpha=0.8)
        
        ax7.set_xlabel('Ativos')
        ax7.set_ylabel('Valores')
        ax7.set_title('Métricas de Risco Comparativas', fontweight='bold')
        ax7.set_xticks(x)
        ax7.set_xticklabels(assets)
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        return self._save_plot(fig)

    def plot_asset_allocation(self, weights: Dict[str, float], title: str = "Alocação de Ativos") -> bytes:
        """Gera um gráfico de pizza (pie chart) da alocação de ativos.

        Parâmetros:
            weights (Dict[str, float]): Dicionário onde as chaves são os nomes dos ativos
                                        e os valores são seus pesos (ou valores monetários).
            title (str): Título do gráfico.

        Retorna:
            bytes: Imagem PNG do gráfico em bytes.
        """
        labels = list(weights.keys())
        sizes = list(weights.values())

        fig, ax = plt.subplots(figsize=(10, 7))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title(title, fontsize=16, fontweight='bold')

        return self._save_plot(fig)

    def plot_cumulative_performance(self, prices: pd.DataFrame, assets: List[str], benchmarks: Optional[List[str]] = None, title: str = "Performance Acumulada") -> bytes:
        """Gera um gráfico de linha da performance acumulada de ativos/portfólio vs. benchmarks.

        Parâmetros:
            prices (pd.DataFrame): DataFrame de preços históricos.
            assets (List[str]): Lista de tickers dos ativos/portfólio a serem plotados.
            benchmarks (Optional[List[str]]): Lista de tickers dos benchmarks para comparação.
            title (str): Título do gráfico.

        Retorna:
            bytes: Imagem PNG do gráfico em bytes.
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        # Calcular retornos acumulados para ativos
        for asset in assets:
            if asset in prices.columns:
                cumulative_returns = (1 + prices[asset].pct_change().fillna(0)).cumprod()
                ax.plot(cumulative_returns.index, cumulative_returns.values, label=asset, linewidth=2)

        # Calcular retornos acumulados para benchmarks
        if benchmarks:
            for benchmark in benchmarks:
                if benchmark in prices.columns: # Assumindo que benchmarks também estão no DataFrame de preços
                    cumulative_returns_bench = (1 + prices[benchmark].pct_change().fillna(0)).cumprod()
                    ax.plot(cumulative_returns_bench.index, cumulative_returns_bench.values, label=f"{benchmark} (Benchmark)", linestyle='--', linewidth=2)
                else:
                    logging.warning(f"Benchmark {benchmark} não encontrado no DataFrame de preços.")

        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_ylabel('Retorno Acumulado', fontsize=12)
        ax.set_xlabel('Data', fontsize=12)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter('{:.0%}'.format))

        # Formatar eixos
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        return self._save_plot(fig)

    def plot_risk_contribution(self, risk_attribution_data: Dict[str, Any], title: str = "Contribuição de Risco por Ativo") -> bytes:
        """Gera um gráfico de barras da contribuição de risco de cada ativo para o portfólio.

        Parâmetros:
            risk_attribution_data (Dict[str, Any]): Dicionário contendo os resultados da função `risk_attribution`,
                                                  incluindo 'assets', 'contribution_vol' e 'contribution_var'.
            title (str): Título do gráfico.

        Retorna:
            bytes: Imagem PNG do gráfico em bytes.
        """
        assets = risk_attribution_data.get('assets', [])
        contribution_vol = risk_attribution_data.get('contribution_vol', [])
        contribution_var = risk_attribution_data.get('contribution_var', [])

        if not assets or not contribution_vol: # contribution_var pode ser NaN
            raise ValueError("Dados insuficientes para gerar o gráfico de contribuição de risco.")

        fig, ax = plt.subplots(figsize=self.figsize)

        # Usar contribution_vol para o gráfico, pois é sempre disponível
        # Para VaR, a contribuição pode ser NaN se o método for inadequado ou dados insuficientes
        y_pos = np.arange(len(assets))
        bars = ax.barh(y_pos, contribution_vol, align='center', color='skyblue')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(assets)
        ax.invert_yaxis()  # Labels read top-to-bottom
        ax.set_xlabel('Contribuição de Volatilidade')
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.xaxis.set_major_formatter(plt.FuncFormatter('{:.2%}'.format))

        # Adicionar rótulos nas barras
        # for i, v in enumerate(contribution_vol):
        #     ax.text(v + 0.05, i, f'{v:.2%}', color='blue', va='center') # Não mostrado diretamente neste exemplo, mas possível

        fig.tight_layout()
        return self._save_plot(fig)


# Funções de conveniência
def create_advanced_visualizer(style: str = 'seaborn-v0_8') -> AdvancedVisualizer:
    """Cria uma instância do visualizador avançado."""
    return AdvancedVisualizer(style=style)
