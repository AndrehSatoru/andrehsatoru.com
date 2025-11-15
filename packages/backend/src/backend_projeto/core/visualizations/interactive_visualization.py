# core/interactive_visualization.py
# Visualizações interativas usando Plotly

import io
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
import json

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express as px
    from plotly.utils import PlotlyJSONEncoder
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Plotly não disponível. Instale com: pip install plotly")

class InteractiveVisualizer:
    """Sistema de visualização interativa usando Plotly."""
    
    def __init__(self):
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly é necessário para visualizações interativas")
    
    def _save_plot(self, fig) -> bytes:
        """Converte figura Plotly para bytes JSON."""
        json_str = json.dumps(fig, cls=PlotlyJSONEncoder)
        return json_str.encode('utf-8')
    
    def plot_interactive_candlestick(self, prices: pd.DataFrame, asset: str) -> bytes:
        """Gráfico de candlestick interativo."""
        if asset not in prices.columns:
            raise ValueError(f"Ativo '{asset}' não encontrado")
        
        # Simular OHLC se necessário
        if 'Open' not in prices.columns:
            ohlc_data = prices[[asset]].copy()
            ohlc_data['Open'] = ohlc_data[asset].shift(1).fillna(ohlc_data[asset])
            ohlc_data['High'] = ohlc_data[asset] * (1 + np.random.normal(0, 0.01, len(ohlc_data)))
            ohlc_data['Low'] = ohlc_data[asset] * (1 - np.random.normal(0, 0.01, len(ohlc_data)))
            ohlc_data['Close'] = ohlc_data[asset]
        else:
            ohlc_data = prices[['Open', 'High', 'Low', 'Close']]
        
        fig = go.Figure(data=go.Candlestick(
            x=ohlc_data.index,
            open=ohlc_data['Open'],
            high=ohlc_data['High'],
            low=ohlc_data['Low'],
            close=ohlc_data['Close'],
            name=asset
        ))
        
        fig.update_layout(
            title=f'{asset} - Candlestick Chart',
            xaxis_title='Data',
            yaxis_title='Preço',
            template='plotly_white',
            height=600
        )
        
        return self._save_plot(fig)
    
    def plot_interactive_portfolio_analysis(self, returns: pd.DataFrame, 
                                          assets: List[str], 
                                          benchmark: Optional[pd.Series] = None) -> bytes:
        """Análise interativa de portfólio."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Retornos Acumulados', 'Volatilidade Rolante', 
                          'Drawdown', 'Distribuição de Retornos'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Retornos acumulados
        cumulative = (1 + returns[assets]).cumprod()
        for asset in assets:
            if asset in cumulative.columns:
                fig.add_trace(
                    go.Scatter(x=cumulative.index, y=cumulative[asset], 
                             name=asset, line=dict(width=2)),
                    row=1, col=1
                )
        
        if benchmark is not None:
            bench_cum = (1 + benchmark).cumprod()
            fig.add_trace(
                go.Scatter(x=bench_cum.index, y=bench_cum.values, 
                          name='Benchmark', line=dict(width=2, dash='dash')),
                row=1, col=1
            )
        
        # Volatilidade rolante
        for asset in assets:
            if asset in returns.columns:
                rolling_vol = returns[asset].rolling(30).std() * np.sqrt(252)
                fig.add_trace(
                    go.Scatter(x=rolling_vol.index, y=rolling_vol.values, 
                              name=f'{asset} Vol', line=dict(width=2)),
                    row=1, col=2
                )
        
        # Drawdown
        for asset in assets:
            if asset in returns.columns:
                cum_ret = (1 + returns[asset]).cumprod()
                running_max = cum_ret.expanding().max()
                drawdown = (cum_ret / running_max) - 1
                fig.add_trace(
                    go.Scatter(x=drawdown.index, y=drawdown.values, 
                             name=f'{asset} DD', fill='tonexty'),
                    row=2, col=1
                )
        
        # Distribuição de retornos
        for asset in assets:
            if asset in returns.columns:
                ret = returns[asset].dropna()
                fig.add_trace(
                    go.Histogram(x=ret, name=f'{asset} Dist', opacity=0.7),
                    row=2, col=2
                )
        
        fig.update_layout(
            title='Análise Interativa de Portfólio',
            height=800,
            showlegend=True,
            template='plotly_white'
        )
        
        return self._save_plot(fig)
    
    def plot_interactive_efficient_frontier(self, returns: pd.DataFrame, 
                                          assets: List[str], n_portfolios: int = 1000) -> bytes:
        """Fronteira eficiente interativa."""
        # Calcular retornos e covariância
        ret_data = returns[assets].dropna()
        mean_returns = ret_data.mean() * 252
        cov_matrix = ret_data.cov() * 252
        
        # Gerar portfólios aleatórios
        np.random.seed(42)
        portfolio_returns = []
        portfolio_volatilities = []
        portfolio_sharpes = []
        
        for _ in range(n_portfolios):
            weights = np.random.random(len(assets))
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
        
        fig = go.Figure()
        
        # Adicionar portfólios
        fig.add_trace(go.Scatter(
            x=portfolio_volatilities,
            y=portfolio_returns,
            mode='markers',
            marker=dict(
                size=8,
                color=portfolio_sharpes,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sharpe Ratio")
            ),
            name='Portfólios',
            hovertemplate='<b>Volatilidade:</b> %{x:.3f}<br>' +
                         '<b>Retorno:</b> %{y:.3f}<br>' +
                         '<b>Sharpe:</b> %{marker.color:.3f}<extra></extra>'
        ))
        
        # Portfólio ótimo
        fig.add_trace(go.Scatter(
            x=[portfolio_volatilities[max_sharpe_idx]],
            y=[portfolio_returns[max_sharpe_idx]],
            mode='markers',
            marker=dict(size=15, color='red', symbol='star'),
            name='Max Sharpe',
            hovertemplate='<b>Max Sharpe Portfolio</b><br>' +
                         '<b>Volatilidade:</b> %{x:.3f}<br>' +
                         '<b>Retorno:</b> %{y:.3f}<extra></extra>'
        ))
        
        # Portfólio de mínima variância
        fig.add_trace(go.Scatter(
            x=[portfolio_volatilities[min_vol_idx]],
            y=[portfolio_returns[min_vol_idx]],
            mode='markers',
            marker=dict(size=15, color='blue', symbol='diamond'),
            name='Min Volatility',
            hovertemplate='<b>Min Volatility Portfolio</b><br>' +
                         '<b>Volatilidade:</b> %{x:.3f}<br>' +
                         '<b>Retorno:</b> %{y:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Fronteira Eficiente Interativa',
            xaxis_title='Volatilidade',
            yaxis_title='Retorno Esperado',
            template='plotly_white',
            height=600
        )
        
        return self._save_plot(fig)
    
    def plot_interactive_risk_metrics(self, returns: pd.DataFrame, 
                                    assets: List[str]) -> bytes:
        """Métricas de risco interativas."""
        metrics_data = []
        for asset in assets:
            if asset in returns.columns:
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
        
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=('Volatilidade', 'Sharpe Ratio', 'Max Drawdown',
                          'VaR 95%', 'Skewness', 'Kurtosis'),
            specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
        )
        
        metrics = ['Volatility', 'Sharpe', 'Max_DD', 'VaR_95', 'Skewness', 'Kurtosis']
        positions = [(1,1), (1,2), (1,3), (2,1), (2,2), (2,3)]
        
        for i, (metric, pos) in enumerate(zip(metrics, positions)):
            fig.add_trace(
                go.Bar(x=df_metrics['Asset'], y=df_metrics[metric], 
                      name=metric, showlegend=False),
                row=pos[0], col=pos[1]
            )
        
        fig.update_layout(
            title='Métricas de Risco Interativas',
            height=800,
            template='plotly_white'
        )
        
        return self._save_plot(fig)
    
    def plot_interactive_correlation_matrix(self, returns: pd.DataFrame, 
                                          assets: List[str]) -> bytes:
        """Matriz de correlação interativa."""
        corr_matrix = returns[assets].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Matriz de Correlação Interativa',
            template='plotly_white',
            height=600
        )
        
        return self._save_plot(fig)
    
    def plot_interactive_monte_carlo(self, returns: pd.Series, 
                                   n_simulations: int = 1000, 
                                   n_days: int = 252) -> bytes:
        """Simulação Monte Carlo interativa."""
        # Parâmetros
        mu = returns.mean()
        sigma = returns.std()
        
        # Simulações
        np.random.seed(42)
        simulations = []
        for _ in range(n_simulations):
            random_walk = np.random.normal(mu, sigma, n_days)
            price_path = (1 + random_walk).cumprod()
            simulations.append(price_path)
        
        simulations = np.array(simulations)
        
        fig = go.Figure()
        
        # Adicionar algumas trajetórias
        for i in range(min(100, n_simulations)):
            fig.add_trace(go.Scatter(
                x=list(range(n_days)),
                y=simulations[i],
                mode='lines',
                line=dict(width=1, color='lightblue'),
                showlegend=False,
                opacity=0.3
            ))
        
        # Percentis
        percentiles = [5, 25, 50, 75, 95]
        colors = ['red', 'orange', 'green', 'orange', 'red']
        
        for p, color in zip(percentiles, colors):
            fig.add_trace(go.Scatter(
                x=list(range(n_days)),
                y=np.percentile(simulations, p, axis=0),
                mode='lines',
                line=dict(width=2, color=color),
                name=f'{p}th Percentile',
                opacity=0.8
            ))
        
        fig.update_layout(
            title=f'Simulação Monte Carlo ({n_simulations} simulações)',
            xaxis_title='Dias',
            yaxis_title='Preço Normalizado',
            template='plotly_white',
            height=600
        )
        
        return self._save_plot(fig)


def create_interactive_visualizer() -> InteractiveVisualizer:
    """Cria uma instância do visualizador interativo."""
    return InteractiveVisualizer()
