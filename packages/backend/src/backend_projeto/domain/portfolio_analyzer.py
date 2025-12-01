"""
Módulo para análise de portfólio baseada em transações.

Este módulo contém a classe PortfolioAnalyzer que fornece métodos para analisar
o desempenho, risco e alocação de um portfólio com base em um histórico de transações.
"""

import logging
from typing import Optional
import math

import numpy as np
import pandas as pd

from backend_projeto.infrastructure.utils.config import Settings, settings
from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.domain.risk_metrics import var_historical, es_historical
from backend_projeto.domain.covariance import risk_attribution


def calculate_rolling_beta(asset_returns: pd.Series, benchmark_returns: pd.Series, window: int = 60) -> pd.Series:
    """
    Calculates the rolling beta of an asset's returns against a benchmark's returns.
    
    Args:
        asset_returns: Series of asset returns
        benchmark_returns: Series of benchmark returns
        window: Rolling window size in days
        
    Returns:
        Series of rolling beta values
    """
    asset_returns, benchmark_returns = asset_returns.align(benchmark_returns, join='inner')
    rolling_cov = asset_returns.rolling(window=window).cov(benchmark_returns)
    rolling_var = benchmark_returns.rolling(window=window).var()
    rolling_beta = rolling_cov / rolling_var
    return rolling_beta.dropna()


class PortfolioAnalyzer:
    """
    Classe para análise de portfólio baseada em transações.
    
    Esta classe fornece métodos para analisar o desempenho, risco e alocação
    de um portfólio com base em um histórico de transações.
    """
    
    def __init__(self, transactions_df: pd.DataFrame, data_loader: YFinanceProvider = None, config: Settings = None, start_date: Optional[str] = None, end_date: Optional[str] = None, initial_value: float = 0.0):
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
            start_date: Data inicial da análise. Se None, usa a data da primeira transação.
            end_date: Data final da análise. Se None, usa a data atual.
            initial_value: Valor inicial do portfólio (capital disponível)
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
        # Se start_date foi fornecido, usa ele; caso contrário, usa a data da primeira transação
        if start_date:
            self.start_date = pd.to_datetime(start_date).normalize()
        else:
            self.start_date = self.transactions['Data'].min()
        self.end_date = pd.to_datetime(end_date).normalize() if end_date else pd.to_datetime('today').normalize()
        
        # Valor inicial do portfólio (capital disponível)
        self.initial_value = initial_value
        
        # Calcular total investido em ativos
        self.total_invested = sum(
            row['Preco'] * row['Quantidade'] 
            for _, row in self.transactions.iterrows() 
            if row['Quantidade'] > 0
        )
        
        # Caixa = valor inicial - total investido
        self.cash = max(0, self.initial_value - self.total_invested)
        
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
            tx_date = pd.to_datetime(tx['Data']).normalize()
            asset = tx['Ativo']
            quantity = tx['Quantidade']
            
            # Encontrar o primeiro dia útil >= data da transação
            valid_dates = dates[dates >= tx_date]
            if len(valid_dates) > 0:
                start_from = valid_dates[0]
                # Atualizar a posição a partir da data da transação
                positions.loc[start_from:, asset] += quantity
                logging.debug(f"Posição {asset}: +{quantity} a partir de {start_from}")
            else:
                logging.warning(f"Data {tx_date} está fora do range de posições")
        
        # Preencher valores ausentes com o último valor válido
        positions = positions.ffill().fillna(0.0)
        
        return positions
    
    def _calculate_portfolio_value(self) -> pd.Series:
        """
        Calcula o valor total do portfólio ao longo do tempo.
        Inclui o valor dos ativos + caixa disponível.
        
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
        
        # Calcular o valor de cada posição (ativos)
        portfolio_value = pd.Series(0.0, index=self.positions.index, name='Valor')
        
        for asset in self.assets:
            if asset in prices.columns:
                # Preencher valores ausentes nos preços com o último valor válido
                asset_prices = prices[asset].reindex(portfolio_value.index).ffill()
                portfolio_value += self.positions[asset] * asset_prices
        
        # Buscar taxas diárias do CDI para o período
        try:
            cdi_rates = self.data_loader.fetch_cdi_daily(
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            # Alinhar com o índice do portfólio
            cdi_rates = cdi_rates.reindex(self.positions.index).fillna(0.0)
        except Exception as e:
            logging.warning(f"Erro ao buscar CDI, usando taxa zero: {e}")
            cdi_rates = pd.Series(0.0, index=self.positions.index)
        
        # Buscar dividendos para todos os ativos
        try:
            dividends_df = self.data_loader.fetch_dividends(
                assets=self.assets,
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            logging.info(f"Dividendos encontrados: {len(dividends_df)} registros")
        except Exception as e:
            logging.warning(f"Erro ao buscar dividendos: {e}")
            dividends_df = pd.DataFrame()
        
        # Calcular o caixa acumulado ao longo do tempo com rendimento do CDI
        # Caixa começa com initial_value e:
        # 1. Rende CDI diariamente
        # 2. Diminui a cada compra
        # 3. Aumenta com dividendos recebidos
        cash_series = pd.Series(0.0, index=self.positions.index, name='Caixa')
        current_cash = self.initial_value
        
        # Criar um dicionário com as transações por data para acesso eficiente
        # Mapear cada transação para o primeiro dia útil disponível no índice
        transactions_by_date = {}
        position_dates = self.positions.index
        
        for _, tx in self.transactions.iterrows():
            # Normalizar a data da transação (remover hora)
            tx_date = pd.to_datetime(tx['Data']).normalize()
            tx_value = tx['Preco'] * tx['Quantidade']
            
            # Encontrar o primeiro dia útil >= data da transação
            valid_dates = position_dates[position_dates >= tx_date]
            if len(valid_dates) > 0:
                mapped_date = valid_dates[0]
                if mapped_date not in transactions_by_date:
                    transactions_by_date[mapped_date] = 0.0
                transactions_by_date[mapped_date] += tx_value
                logging.debug(f"Transação mapeada: {tx_date} -> {mapped_date}, valor: R$ {tx_value:.2f}")
            else:
                logging.warning(f"Transação em {tx_date} está fora do range de posições")
        
        # Criar dicionário de dividendos por data e ativo
        # O formato de dividends_df é: índice=Date, colunas=['ValorPorAcao', 'Ativo']
        dividends_by_date = {}
        if not dividends_df.empty and 'ValorPorAcao' in dividends_df.columns and 'Ativo' in dividends_df.columns:
            for div_date, div_row in dividends_df.iterrows():
                div_date_normalized = pd.to_datetime(div_date).normalize()
                asset = div_row['Ativo']
                div_value = div_row['ValorPorAcao']
                
                # Encontrar o primeiro dia útil >= data do dividendo
                valid_dates = position_dates[position_dates >= div_date_normalized]
                if len(valid_dates) > 0:
                    mapped_date = valid_dates[0]
                    if mapped_date not in dividends_by_date:
                        dividends_by_date[mapped_date] = {}
                    if asset not in dividends_by_date[mapped_date]:
                        dividends_by_date[mapped_date][asset] = 0.0
                    dividends_by_date[mapped_date][asset] += div_value
                    logging.debug(f"Dividendo mapeado: {asset} em {div_date_normalized} -> {mapped_date}, valor/ação: R$ {div_value:.4f}")
        
        logging.info(f"Transações por data: {transactions_by_date}")
        logging.info(f"Total a descontar do caixa: {sum(transactions_by_date.values())}")
        logging.info(f"Dividendos por data: {len(dividends_by_date)} datas com dividendos")
        logging.info(f"Caixa inicial: {current_cash}")
        
        total_dividends_received = 0.0
        
        # Processar cada dia
        for date in self.positions.index:
            # Aplicar rendimento do CDI ao caixa do dia anterior
            if date in cdi_rates.index and cdi_rates[date] > 0:
                current_cash *= (1 + cdi_rates[date])
            
            # Subtrair transações do dia (se houver)
            if date in transactions_by_date:
                tx_value = transactions_by_date[date]
                logging.info(f"Descontando R$ {tx_value:.2f} do caixa em {date}")
                current_cash -= tx_value
            
            # Adicionar dividendos recebidos ao caixa
            if date in dividends_by_date:
                for asset, div_per_share in dividends_by_date[date].items():
                    # Quantidade de ações do ativo nesta data
                    shares = self.positions.loc[date, asset] if asset in self.positions.columns else 0
                    dividend_value = shares * div_per_share
                    if dividend_value > 0:
                        current_cash += dividend_value
                        total_dividends_received += dividend_value
                        logging.info(f"Dividendo recebido: {asset} - {shares:.2f} ações x R$ {div_per_share:.4f} = R$ {dividend_value:.2f}")
            
            # Garantir que o caixa não seja negativo
            current_cash = max(0, current_cash)
            
            # Registrar o caixa do dia
            cash_series[date] = current_cash
        
        logging.info(f"Caixa final: {current_cash}")
        logging.info(f"Total de dividendos recebidos: R$ {total_dividends_received:.2f}")
        
        # Atualizar self.cash com o valor final (incluindo CDI e dividendos)
        self.cash = current_cash
        
        # Valor total = ativos + caixa
        portfolio_value += cash_series
        
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
        
        # Remover valores NaN para cálculos
        valid_portfolio = self.portfolio_value.dropna()
        
        if valid_portfolio.empty or len(valid_portfolio) < 2:
            return {"error": "Dados insuficientes para análise de desempenho"}
        
        # Calcular métricas de desempenho usando valores válidos
        initial_value = valid_portfolio.iloc[0]
        final_value = valid_portfolio.iloc[-1]
        total_return = (final_value / initial_value - 1) * 100  # em %
        
        # CAGR (Compound Annual Growth Rate) - retorno anualizado correto
        n_years = len(valid_portfolio) / 252  # anos de análise
        if n_years > 0 and initial_value > 0:
            cagr = (pow(final_value / initial_value, 1 / n_years) - 1)
        else:
            cagr = 0
        
        # Volatilidade anualizada (usando retornos simples para consistência)
        simple_returns = valid_portfolio.pct_change().dropna()
        annualized_vol = simple_returns.std() * np.sqrt(252)
        
        # Sharpe Ratio usando CAGR e volatilidade anualizada
        # Assumindo taxa livre de risco de 0% para simplificar
        sharpe_ratio = cagr / annualized_vol if annualized_vol > 0 else 0
        
        # Calcular drawdown
        cum_returns = (1 + simple_returns).cumprod()
        running_max = cum_returns.cummax()
        drawdowns = (cum_returns - running_max) / running_max
        max_drawdown = drawdowns.min() * 100  # em %
        
        # Calcular VaR e ES usando retornos simples
        var_95, _ = var_historical(simple_returns, alpha=0.95)
        var_95 *= 100  # em %
        es_95, _ = es_historical(simple_returns, alpha=0.95)
        es_95 *= 100  # em %
        
        return {
            "retorno_total_%": round(total_return, 2),
            "retorno_anualizado_%": round(cagr * 100, 2),
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
        
        # Obter preços - buscar um intervalo maior para garantir que temos dados
        # (considerando fins de semana e feriados)
        start_fetch = (analysis_date - pd.Timedelta(days=10)).strftime('%Y-%m-%d')
        end_fetch = analysis_date.strftime('%Y-%m-%d')
        
        prices = self.data_loader.fetch_stock_prices(
            assets=self.assets,
            start_date=start_fetch,
            end_date=end_fetch
        )
        
        # Usar a última data disponível nos preços
        if prices.empty:
            return {"error": f"Não foi possível obter preços para os ativos na data {analysis_date}"}
        
        # Pegar a última data disponível (mais recente)
        available_date = prices.index[-1]
        
        # Calcular valores das posições
        allocation = {}
        total_assets_value = 0.0
        
        for asset in self.assets:
            if asset in prices.columns and not pd.isna(prices.loc[available_date, asset]):
                asset_value = positions[asset] * prices.loc[available_date, asset]
                if asset_value > 0:  # Apenas incluir ativos com valor positivo
                    allocation[asset] = {
                        'quantidade': positions[asset],
                        'preco_unitario': float(prices.loc[available_date, asset]),
                        'valor_total': float(asset_value)
                    }
                    total_assets_value += asset_value
        
        # Adicionar Caixa à alocação se houver valor inicial definido
        if self.cash > 0:
            allocation['Caixa'] = {
                'quantidade': 1,
                'preco_unitario': float(self.cash),
                'valor_total': float(self.cash)
            }
        
        # Valor total inclui ativos + caixa
        total_value = total_assets_value + self.cash
        
        # Calcular percentuais
        for asset in allocation:
            allocation[asset]['percentual'] = (allocation[asset]['valor_total'] / total_value) * 100 if total_value > 0 else 0
        
        return {
            'data_analise': analysis_date.strftime('%Y-%m-%d'),
            'valor_total': total_value,
            'valor_investido': total_assets_value,
            'caixa': self.cash,
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
        
        # Gerar série temporal de performance para gráficos
        performance_series = self._generate_performance_series()
        
        # Gerar retornos mensais para tabela de rentabilidade
        monthly_returns = self._generate_monthly_returns()
        
        # Gerar histórico de evolução da alocação
        allocation_history = self._generate_allocation_history()
        
        # Gerar retornos anualizados rolling
        rolling_annualized_returns = self._generate_rolling_annualized_returns()
        
        # Gerar contribuição de risco
        risk_contribution = self._generate_risk_contribution()
        
        # Gerar evolução do beta
        beta_evolution = self._generate_beta_evolution()
        
        # Gerar matriz de betas individuais
        beta_matrix = self._generate_beta_matrix()
        
        # Gerar matriz de correlação
        correlation_matrix = self._generate_correlation_matrix()
        
        # Gerar estatísticas dos ativos individuais (para fronteira eficiente)
        asset_stats = self._generate_asset_stats()
        
        # Gerar distribuição de retornos
        returns_distribution = self._generate_returns_distribution()
        
        # Gerar simulação Monte Carlo
        monte_carlo = self._generate_monte_carlo_simulation()
        
        # Gerar testes de estresse
        stress_tests = self._generate_stress_tests()
        
        # Gerar análise Fama-French
        fama_french = self._generate_fama_french_analysis()
        
        # Gerar otimização Markowitz
        markowitz_optimization = self._generate_markowitz_optimization()
        
        # Gerar backtest do VaR
        var_backtest = self._generate_var_backtest()
        
        # Gerar atribuição de risco detalhada
        risk_attribution_detailed = self._generate_risk_attribution_detailed()
        
        # Gerar análise CAPM
        capm_analysis = self._generate_capm_analysis()
        
        # Gerar Incremental VaR
        incremental_var_analysis = self._generate_incremental_var()
        
        # Retornar resultados consolidados
        return {
            'desempenho': performance,
            'alocacao': allocation,
            'performance': performance_series,
            'monthly_returns': monthly_returns,
            'allocation_history': allocation_history,
            'rolling_annualized_returns': rolling_annualized_returns,
            'risk_contribution': risk_contribution,
            'beta_evolution': beta_evolution,
            'beta_matrix': beta_matrix,
            'correlation_matrix': correlation_matrix,
            'asset_stats': asset_stats,
            'returns_distribution': returns_distribution,
            'monte_carlo': monte_carlo,
            'stress_tests': stress_tests,
            'fama_french': fama_french,
            'markowitz_optimization': markowitz_optimization,
            'var_backtest': var_backtest,
            'risk_attribution_detailed': risk_attribution_detailed,
            'capm_analysis': capm_analysis,
            'incremental_var': incremental_var_analysis,
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
    
    def _generate_allocation_history(self) -> list:
        """
        Gera histórico de evolução da alocação percentual por ativo (incluindo caixa).
        
        Returns:
            Lista de dicionários com data e percentual de cada ativo + caixa
        """
        if self.positions is None or self.portfolio_value is None:
            return []
        
        # Obter preços históricos para todos os ativos
        prices = self.data_loader.fetch_stock_prices(
            assets=self.assets,
            start_date=self.start_date.strftime('%Y-%m-%d'),
            end_date=self.end_date.strftime('%Y-%m-%d')
        )
        
        # Remover valores NaN do portfolio
        valid_portfolio = self.portfolio_value.dropna()
        if valid_portfolio.empty:
            return []
        
        # Calcular valor de cada ativo ao longo do tempo
        asset_values = pd.DataFrame(index=self.positions.index, columns=self.assets)
        for asset in self.assets:
            if asset in prices.columns:
                asset_prices = prices[asset].reindex(self.positions.index).ffill()
                asset_values[asset] = self.positions[asset] * asset_prices
            else:
                asset_values[asset] = 0.0
        
        # Amostrar para não sobrecarregar (máximo 250 pontos)
        step = max(1, len(valid_portfolio) // 250)
        
        result = []
        for i in range(0, len(valid_portfolio), step):
            date = valid_portfolio.index[i]
            portfolio_val = valid_portfolio.iloc[i]
            
            if date not in asset_values.index or pd.isna(portfolio_val) or portfolio_val <= 0:
                continue
            
            entry = {'date': date.strftime('%Y-%m-%d')}
            
            # Calcular valor total dos ativos
            total_asset_value = 0.0
            for asset in self.assets:
                asset_val = asset_values.loc[date, asset]
                if pd.notna(asset_val) and asset_val > 0:
                    # Percentual em relação ao valor TOTAL do portfólio (ativos + caixa)
                    pct = (float(asset_val) / float(portfolio_val)) * 100
                    entry[asset] = round(pct, 2)
                    total_asset_value += float(asset_val)
                else:
                    entry[asset] = 0.0
            
            # Calcular caixa como diferença entre valor do portfólio e valor dos ativos
            caixa_pct = ((float(portfolio_val) - total_asset_value) / float(portfolio_val)) * 100
            entry['Caixa'] = round(max(0, caixa_pct), 2)
            
            result.append(entry)
        
        return result
    
    def _generate_rolling_annualized_returns(self, window_days: int = 252) -> list:
        """
        Gera série de retornos anualizados rolling (252 dias úteis).
        Benchmark: CDI + 2% ao ano
        
        Args:
            window_days: Janela em dias úteis para cálculo (padrão: 252 = 1 ano)
            
        Returns:
            Lista de dicionários com data, retorno anualizado do portfolio e benchmark (CDI+2%)
        """
        if self.portfolio_value is None or self.portfolio_value.empty:
            return []
        
        valid_portfolio = self.portfolio_value.dropna()
        if len(valid_portfolio) < window_days:
            # Se não tem dados suficientes, usar janela menor
            window_days = max(20, len(valid_portfolio) // 2)
        
        if len(valid_portfolio) < 20:
            return []
        
        # Calcular retornos diários
        daily_returns = valid_portfolio.pct_change().dropna()
        
        # Calcular retorno anualizado rolling
        # Retorno anualizado = (1 + retorno_acumulado)^(252/dias) - 1
        rolling_cumulative = (1 + daily_returns).rolling(window=window_days).apply(
            lambda x: x.prod() - 1, raw=True
        )
        
        # Anualizar o retorno
        rolling_annualized = rolling_cumulative.apply(
            lambda x: ((1 + x) ** (252 / window_days) - 1) * 100 if pd.notna(x) else None
        )
        
        # Calcular benchmark (CDI + 2%) rolling annualized
        try:
            cdi_rates = self.data_loader.fetch_cdi_daily(
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            cdi_rates = cdi_rates.reindex(valid_portfolio.index).fillna(0.0)
            
            # Adicionar spread de 2% ao ano ao CDI (convertido para taxa diária)
            # 2% ao ano = (1.02)^(1/252) - 1 por dia
            daily_spread = (1.02) ** (1/252) - 1
            cdi_plus_spread = cdi_rates + daily_spread
            
            # Retorno acumulado do CDI+2% rolling
            rolling_cdi_cumulative = cdi_plus_spread.rolling(window=window_days).apply(
                lambda x: (1 + x).prod() - 1, raw=True
            )
            rolling_cdi_annualized = rolling_cdi_cumulative.apply(
                lambda x: ((1 + x) ** (252 / window_days) - 1) * 100 if pd.notna(x) else None
            )
        except Exception as e:
            logging.warning(f"Erro ao calcular CDI+2% rolling: {e}")
            # CDI aproximado de 12% + 2% = 14%
            rolling_cdi_annualized = pd.Series(14.0, index=rolling_annualized.index)
        
        # Amostrar para não sobrecarregar (pegar 1 ponto por mês aproximadamente)
        valid_data = rolling_annualized.dropna()
        if valid_data.empty:
            return []
        
        # Agrupar por mês
        result = []
        monthly_groups = valid_data.groupby(pd.Grouper(freq='M'))
        
        for month_end, group in monthly_groups:
            if group.empty:
                continue
            
            # Pegar o último valor do mês
            last_date = group.index[-1]
            portfolio_ret = group.iloc[-1]
            
            benchmark_ret = 14.0  # Fallback CDI+2%
            if last_date in rolling_cdi_annualized.index:
                cdi_val = rolling_cdi_annualized.loc[last_date]
                if pd.notna(cdi_val):
                    benchmark_ret = cdi_val
            
            result.append({
                'date': last_date.strftime('%Y-%m'),
                'portfolio': round(portfolio_ret, 1) if pd.notna(portfolio_ret) else 0,
                'benchmark': round(benchmark_ret, 1) if pd.notna(benchmark_ret) else 14.0
            })
        
        return result
    
    def _generate_risk_contribution(self) -> list:
        """
        Gera dados de contribuição de risco (volatilidade) por ativo.
        
        Returns:
            Lista de dicionários ordenados por contribuição, com asset e contribution
        """
        if not self.assets or self.positions is None:
            return []
        
        try:
            # Buscar preços dos ativos
            prices = self.data_loader.fetch_stock_prices(
                assets=self.assets,
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            
            if prices.empty:
                return []
            
            # Calcular retornos diários
            returns = prices.pct_change().dropna()
            
            if returns.empty or len(returns) < 20:
                return []
            
            # Obter pesos atuais dos ativos
            allocation = self.analyze_allocation()
            weights = []
            valid_assets = []
            
            for asset in self.assets:
                if asset in allocation['alocacao'] and asset in returns.columns:
                    pct = allocation['alocacao'][asset].get('percentual', 0)
                    if pct > 0:
                        weights.append(pct / 100)  # Converter para fração
                        valid_assets.append(asset)
            
            if not valid_assets or len(valid_assets) < 2:
                return []
            
            # Normalizar pesos
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            else:
                return []
            
            # Usar a função risk_attribution existente
            result = risk_attribution(
                returns_df=returns,
                assets=valid_assets,
                weights=weights
            )
            
            # Converter contribuições para percentuais
            contribution_vol = result.get('contribution_vol', [])
            portfolio_vol = result.get('portfolio_vol', 0)
            
            if portfolio_vol == 0:
                return []
            
            # Calcular contribuição percentual de cada ativo
            risk_data = []
            for i, asset in enumerate(valid_assets):
                if i < len(contribution_vol):
                    # Contribuição como % da volatilidade total
                    pct_contribution = (contribution_vol[i] / portfolio_vol) * 100
                    risk_data.append({
                        'asset': asset,
                        'contribution': round(abs(pct_contribution), 1)
                    })
            
            # Ordenar por contribuição (maior primeiro)
            risk_data.sort(key=lambda x: x['contribution'], reverse=True)
            
            return risk_data
            
        except Exception as e:
            logging.warning(f"Erro ao calcular contribuição de risco: {e}")
            return []
    
    def _generate_beta_matrix(self) -> list:
        """
        Gera matriz de betas e R² individuais de cada ativo em relação ao IBOVESPA.
        
        O beta é calculado usando regressão linear dos retornos do ativo contra
        os retornos do benchmark (IBOVESPA):
        
        Beta = Cov(R_ativo, R_mercado) / Var(R_mercado)
        
        Returns:
            Lista de dicionários com ativo, beta, r_squared e peso na carteira
        """
        if not self.assets:
            return []
        
        try:
            # Buscar dados do IBOVESPA (benchmark)
            ibov_prices = self.data_loader.fetch_stock_prices(
                assets=['^BVSP'],
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            
            if ibov_prices.empty or '^BVSP' not in ibov_prices.columns:
                logging.warning("Não foi possível obter dados do IBOVESPA para cálculo da matriz de beta")
                return []
            
            # Buscar preços dos ativos
            asset_prices = self.data_loader.fetch_stock_prices(
                assets=self.assets,
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            
            if asset_prices.empty:
                return []
            
            # Juntar e calcular retornos
            combined = asset_prices.join(ibov_prices[['^BVSP']], how='inner')
            returns = combined.pct_change().dropna()
            
            if len(returns) < 30:  # Precisamos de pelo menos 30 observações
                return []
            
            # Retornos do benchmark
            bench_returns = returns['^BVSP'].values
            
            # Calcular peso de cada ativo na carteira atual
            allocation = self.analyze_allocation()
            weights = {}
            if allocation and 'alocacao' in allocation:
                for asset, data in allocation['alocacao'].items():
                    if asset != 'Caixa':
                        weights[asset] = data.get('percentual', 0) / 100
            
            result = []
            total_weight = 0
            sum_beta_weighted = 0
            sum_r2_weighted = 0
            
            for asset in self.assets:
                if asset not in returns.columns:
                    continue
                
                asset_returns = returns[asset].values
                
                # Regressão linear: R_asset = alpha + beta * R_market + epsilon
                # Usando fórmula direta: beta = Cov(asset, market) / Var(market)
                cov_matrix = np.cov(asset_returns, bench_returns)
                cov_asset_bench = cov_matrix[0, 1]
                var_bench = cov_matrix[1, 1]
                
                if var_bench == 0:
                    continue
                
                beta = cov_asset_bench / var_bench
                
                # Calcular R² (coeficiente de determinação)
                # R² = Cor(asset, market)²
                correlation = np.corrcoef(asset_returns, bench_returns)[0, 1]
                r_squared = correlation ** 2
                
                weight = weights.get(asset, 0)
                
                result.append({
                    'asset': asset.replace('.SA', ''),
                    'beta': round(float(beta), 2),
                    'r_squared': round(float(r_squared), 2),
                    'weight': round(float(weight), 4)
                })
                
                total_weight += weight
                sum_beta_weighted += beta * weight
                sum_r2_weighted += r_squared * weight
            
            # Calcular médias ponderadas
            avg_beta = sum_beta_weighted / total_weight if total_weight > 0 else 0
            avg_r_squared = sum_r2_weighted / total_weight if total_weight > 0 else 0
            
            return {
                'items': result,
                'avg_beta': round(float(avg_beta), 2),
                'avg_r_squared': round(float(avg_r_squared), 2)
            }
            
        except Exception as e:
            logging.warning(f"Erro ao calcular matriz de beta: {e}")
            return []
    
    def _generate_correlation_matrix(self) -> dict:
        """
        Gera matriz de correlação entre os retornos dos ativos da carteira.
        
        A correlação de Pearson mede a relação linear entre dois ativos:
        - 1.0: correlação positiva perfeita
        - 0.0: sem correlação linear
        - -1.0: correlação negativa perfeita
        
        Returns:
            Dicionário com matriz de correlação e estatísticas
        """
        if not self.assets or len(self.assets) < 2:
            return {}
        
        try:
            # Buscar preços dos ativos
            asset_prices = self.data_loader.fetch_stock_prices(
                assets=self.assets,
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            
            if asset_prices.empty:
                return {}
            
            # Calcular retornos
            returns = asset_prices.pct_change().dropna()
            
            if len(returns) < 30:  # Precisamos de pelo menos 30 observações
                return {}
            
            # Filtrar apenas ativos que existem nos dados
            available_assets = [a for a in self.assets if a in returns.columns]
            
            if len(available_assets) < 2:
                return {}
            
            # Calcular matriz de correlação
            corr_matrix = returns[available_assets].corr()
            
            # Converter para formato de lista para o frontend
            assets_clean = [a.replace('.SA', '') for a in available_assets]
            matrix = []
            correlations = []
            
            for i, asset_i in enumerate(available_assets):
                row = []
                for j, asset_j in enumerate(available_assets):
                    corr_value = round(float(corr_matrix.loc[asset_i, asset_j]), 2)
                    row.append(corr_value)
                    
                    # Coletar correlações únicas (excluindo diagonal)
                    if i < j:
                        correlations.append(corr_value)
                
                matrix.append(row)
            
            # Calcular estatísticas
            if correlations:
                avg_corr = sum(correlations) / len(correlations)
                max_corr = max(correlations)
                min_corr = min(correlations)
            else:
                avg_corr = max_corr = min_corr = 0
            
            return {
                'assets': assets_clean,
                'matrix': matrix,
                'avg_correlation': round(float(avg_corr), 2),
                'max_correlation': round(float(max_corr), 2),
                'min_correlation': round(float(min_corr), 2)
            }
            
        except Exception as e:
            logging.warning(f"Erro ao calcular matriz de correlação: {e}")
            return {}

    def _generate_asset_stats(self) -> list:
        """
        Gera estatísticas de retorno e volatilidade de cada ativo individual.
        
        Usado para plotar ativos na fronteira eficiente.
        
        Returns:
            Lista com nome, retorno anualizado e volatilidade anualizada de cada ativo
        """
        if not self.assets:
            return []
        
        try:
            # Buscar preços dos ativos
            asset_prices = self.data_loader.fetch_stock_prices(
                assets=self.assets,
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            
            if asset_prices.empty:
                return []
            
            # Calcular retornos
            returns = asset_prices.pct_change().dropna()
            
            if len(returns) < 30:
                return []
            
            result = []
            for asset in self.assets:
                if asset not in returns.columns:
                    continue
                
                asset_returns = returns[asset].dropna()
                
                if len(asset_returns) < 30:
                    continue
                
                # Retorno anualizado
                mean_daily = asset_returns.mean()
                annual_return = mean_daily * 252 * 100  # Em percentual
                
                # Volatilidade anualizada
                std_daily = asset_returns.std()
                annual_volatility = std_daily * np.sqrt(252) * 100  # Em percentual
                
                result.append({
                    'asset': asset.replace('.SA', ''),
                    'return': round(float(annual_return), 2),
                    'volatility': round(float(annual_volatility), 2)
                })
            
            return result
            
        except Exception as e:
            logging.warning(f"Erro ao calcular estatísticas dos ativos: {e}")
            return []

    def _generate_returns_distribution(self) -> dict:
        """
        Gera histograma da distribuição dos retornos diários do portfólio.
        
        Returns:
            Dicionário com bins do histograma e estatísticas
        """
        if self.portfolio_value is None or self.portfolio_value.empty:
            return {}
        
        try:
            # Calcular retornos do portfólio
            portfolio_returns = self.portfolio_value.pct_change().dropna() * 100  # Em percentual
            
            if len(portfolio_returns) < 30:
                return {}
            
            # Definir bins para o histograma (de -5% a +5% em incrementos de 0.5%)
            bin_edges = np.arange(-5, 5.5, 0.5)
            
            # Contar frequência em cada bin
            hist, edges = np.histogram(portfolio_returns, bins=bin_edges)
            
            # Criar dados do histograma
            distribution = []
            for i in range(len(hist)):
                bin_center = (edges[i] + edges[i + 1]) / 2
                distribution.append({
                    'range': f"{bin_center:.1f}%",
                    'frequency': int(hist[i]),
                    'returns': round(float(bin_center), 2)
                })
            
            # Calcular estatísticas
            mean_return = float(portfolio_returns.mean())
            std_return = float(portfolio_returns.std())
            skewness = float(portfolio_returns.skew())
            kurtosis = float(portfolio_returns.kurtosis())
            
            # Calcular VaR e CVaR (95%)
            var_95 = float(np.percentile(portfolio_returns, 5))
            cvar_95 = float(portfolio_returns[portfolio_returns <= var_95].mean())
            
            return {
                'distribution': distribution,
                'stats': {
                    'mean': round(mean_return, 2),
                    'std': round(std_return, 2),
                    'skewness': round(skewness, 2),
                    'kurtosis': round(kurtosis, 2),
                    'var_95': round(var_95, 2),
                    'cvar_95': round(cvar_95, 2),
                    'n_observations': len(portfolio_returns)
                }
            }
            
        except Exception as e:
            logging.warning(f"Erro ao calcular distribuição de retornos: {e}")
            return {}

    def _generate_beta_evolution(self, window: int = 60) -> list:
        """
        Gera série temporal de evolução do beta da carteira em relação ao IBOVESPA.
        
        Args:
            window: Janela em dias úteis para cálculo do beta rolling (padrão: 60)
            
        Returns:
            Lista de dicionários com data e valor do beta
        """
        if self.portfolio_value is None or self.portfolio_value.empty:
            return []
        
        try:
            # Buscar dados do IBOVESPA (benchmark)
            ibov_prices = self.data_loader.fetch_stock_prices(
                assets=['^BVSP'],
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            
            if ibov_prices.empty or '^BVSP' not in ibov_prices.columns:
                logging.warning("Não foi possível obter dados do IBOVESPA para cálculo do beta")
                return []
            
            ibov_series = ibov_prices['^BVSP'].dropna()
            
            # Calcular retornos do portfólio
            valid_portfolio = self.portfolio_value.dropna()
            if len(valid_portfolio) < window:
                return []
            
            portfolio_returns = valid_portfolio.pct_change().dropna()
            
            # Calcular retornos do IBOVESPA
            ibov_returns = ibov_series.pct_change().dropna()
            
            # Calcular beta rolling usando a função existente
            rolling_beta = calculate_rolling_beta(
                asset_returns=portfolio_returns,
                benchmark_returns=ibov_returns,
                window=window
            )
            
            if rolling_beta.empty:
                return []
            
            # Agrupar por mês para não sobrecarregar o gráfico
            result = []
            monthly_groups = rolling_beta.groupby(pd.Grouper(freq='M'))
            
            for month_end, group in monthly_groups:
                if group.empty:
                    continue
                
                # Pegar o último valor do mês
                last_date = group.index[-1]
                beta_value = group.iloc[-1]
                
                if pd.notna(beta_value):
                    result.append({
                        'date': last_date.strftime('%Y-%m'),
                        'beta': round(float(beta_value), 2)
                    })
            
            return result
            
        except Exception as e:
            logging.warning(f"Erro ao calcular evolução do beta: {e}")
            return []
    
    def _generate_monte_carlo_simulation(self, n_paths: int = 100000, n_days: int = 252) -> dict:
        """
        Gera simulação de Monte Carlo comparativa usando MGB com GARCH e Bootstrap Histórico.
        
        Args:
            n_paths: Número de simulações (padrão: 100000)
            n_days: Número de dias para simular (padrão: 252 = 1 ano)
            
        Returns:
            Dicionário com dados de distribuição para o gráfico
        """
        if self.portfolio_value is None or self.portfolio_value.empty:
            return {}
        
        try:
            valid_portfolio = self.portfolio_value.dropna()
            if len(valid_portfolio) < 60:
                return {}
            
            # Calcular retornos diários
            returns = valid_portfolio.pct_change().dropna()
            if len(returns) < 30:
                return {}
            
            # Valor inicial = valor atual da carteira
            initial_value = float(valid_portfolio.iloc[-1])
            
            # ==== MGB (Geometric Brownian Motion) com volatilidade histórica ====
            # mu e sigma são DIÁRIOS
            mu_daily = float(returns.mean())  # Retorno médio diário
            sigma_daily = float(returns.std())  # Volatilidade diária
            
            # Drift e volatilidade anualizados (para exibição)
            annual_drift = mu_daily * 252
            annual_volatility = sigma_daily * np.sqrt(252)
            
            # Simular MGB: S(t+dt) = S(t) * exp((mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z)
            # Como dt = 1 dia e mu/sigma já são diários, usamos diretamente:
            np.random.seed(42)  # Para reprodutibilidade
            
            # Gerar choques diários
            Z = np.random.standard_normal(size=(n_days, n_paths))
            daily_log_returns = (mu_daily - 0.5 * sigma_daily ** 2) + sigma_daily * Z
            
            # Acumular retornos log e converter para preços
            cumulative_log_returns = np.cumsum(daily_log_returns, axis=0)
            paths_mgb = initial_value * np.exp(cumulative_log_returns)
            terminal_mgb = paths_mgb[-1, :]
            
            # ==== Bootstrap Histórico ====
            np.random.seed(123)  # Seed diferente para bootstrap
            
            # Usar retornos históricos aleatoriamente
            historical_returns = returns.values
            bootstrap_paths = np.zeros((n_days, n_paths))
            
            for path in range(n_paths):
                # Selecionar retornos aleatórios do histórico
                sampled_returns = np.random.choice(historical_returns, size=n_days, replace=True)
                bootstrap_paths[:, path] = initial_value * np.cumprod(1 + sampled_returns)
            
            terminal_bootstrap = bootstrap_paths[-1, :]
            
            # ==== Gerar histograma para ambas distribuições ====
            # Determinar range baseado nos dados
            all_terminal = np.concatenate([terminal_mgb, terminal_bootstrap])
            min_val = np.percentile(all_terminal, 0.5)
            max_val = np.percentile(all_terminal, 99.5)
            
            # Com 50k simulações, podemos usar mais bins para melhor resolução
            n_bins = 50
            bins = np.linspace(min_val, max_val, n_bins + 1)
            bin_centers = (bins[:-1] + bins[1:]) / 2
            
            # Calcular histogramas com contagem
            hist_mgb, _ = np.histogram(terminal_mgb, bins=bins)
            hist_bootstrap, _ = np.histogram(terminal_bootstrap, bins=bins)
            
            # Normalizar para percentual (0-100) de simulações em cada bin
            hist_mgb_pct = (hist_mgb / n_paths) * 100
            hist_bootstrap_pct = (hist_bootstrap / n_paths) * 100
            
            # Função para formatar valores monetários
            def format_currency(value):
                if abs(value) >= 1_000_000_000:
                    return f"R$ {value / 1_000_000_000:.1f}B"
                elif abs(value) >= 1_000_000:
                    return f"R$ {value / 1_000_000:.1f}M"
                elif abs(value) >= 1_000:
                    return f"R$ {value / 1_000:.0f}K"
                else:
                    return f"R$ {value:.0f}"
            
            # Criar dados para o gráfico
            distribution_data = []
            for i in range(n_bins):
                value = bin_centers[i]
                distribution_data.append({
                    'value': float(value),
                    'valueLabel': format_currency(value),
                    'mgb': float(hist_mgb_pct[i]) if hist_mgb_pct[i] > 0.01 else 0,
                    'bootstrap': float(hist_bootstrap_pct[i]) if hist_bootstrap_pct[i] > 0.01 else 0
                })
            
            # Calcular estatísticas
            return {
                'distribution': distribution_data,
                'initialValue': initial_value,
                'mgb': {
                    'median': float(np.median(terminal_mgb)),
                    'mean': float(np.mean(terminal_mgb)),
                    'std': float(np.std(terminal_mgb)),
                    'percentile_5': float(np.percentile(terminal_mgb, 5)),
                    'percentile_95': float(np.percentile(terminal_mgb, 95)),
                    'drift_annual': float(annual_drift * 100),  # Em percentual
                    'volatility_annual': float(annual_volatility * 100)  # Volatilidade anualizada em %
                },
                'bootstrap': {
                    'median': float(np.median(terminal_bootstrap)),
                    'mean': float(np.mean(terminal_bootstrap)),
                    'std': float(np.std(terminal_bootstrap)),
                    'percentile_5': float(np.percentile(terminal_bootstrap, 5)),
                    'percentile_95': float(np.percentile(terminal_bootstrap, 95))
                },
                'params': {
                    'n_paths': n_paths,
                    'n_days': n_days
                }
            }
            
        except Exception as e:
            logging.warning(f"Erro ao gerar simulação Monte Carlo: {e}")
            return {}
    
    def _generate_stress_tests(self) -> list:
        """
        Gera testes de estresse simulando diferentes cenários adversos.
        
        Calcula o impacto no portfólio baseado na volatilidade histórica
        e na correlação dos ativos sob diferentes cenários de crise.
        
        Returns:
            Lista de cenários de estresse com impacto estimado
        """
        if self.portfolio_value is None or self.portfolio_value.empty:
            return []
        
        try:
            valid_portfolio = self.portfolio_value.dropna()
            if len(valid_portfolio) < 30:
                return []
            
            # Calcular retornos diários
            returns = valid_portfolio.pct_change().dropna()
            if len(returns) < 20:
                return []
            
            # Calcular estatísticas históricas
            daily_volatility = float(returns.std())
            annual_volatility = daily_volatility * np.sqrt(252)
            
            # Calcular drawdown máximo histórico
            cumulative = (1 + returns).cumprod()
            peak = cumulative.expanding(min_periods=1).max()
            drawdown = (cumulative / peak) - 1
            max_drawdown = float(drawdown.min())
            
            # Calcular VaR histórico 99%
            var_99 = float(np.percentile(returns, 1))
            
            # Obter dados do IBOVESPA para correlação (se disponível)
            try:
                ibov_prices = self.data_loader.fetch_stock_prices(
                    assets=['^BVSP'],
                    start_date=self.start_date.strftime('%Y-%m-%d'),
                    end_date=self.end_date.strftime('%Y-%m-%d')
                )
                if not ibov_prices.empty and '^BVSP' in ibov_prices.columns:
                    ibov_returns = ibov_prices['^BVSP'].pct_change().dropna()
                    # Alinhar datas
                    common_dates = returns.index.intersection(ibov_returns.index)
                    if len(common_dates) > 20:
                        correlation = float(returns.loc[common_dates].corr(ibov_returns.loc[common_dates]))
                    else:
                        correlation = 0.7  # Fallback
                else:
                    correlation = 0.7
            except Exception:
                correlation = 0.7  # Fallback se não conseguir calcular
            
            # Definir cenários de estresse com choques baseados em dados históricos reais
            # Os valores são multiplicados pela volatilidade/correlação do portfólio
            scenarios = [
                {
                    "scenario": "Crise 2008",
                    "type": "historical",
                    "base_shock": -0.50,  # Queda de ~50% no auge da crise
                    "description": "Crise financeira global de 2008"
                },
                {
                    "scenario": "COVID-19",
                    "type": "historical",
                    "base_shock": -0.35,  # Queda de ~35% em março/2020
                    "description": "Pandemia COVID-19 (março 2020)"
                },
                {
                    "scenario": "Crise Subprime",
                    "type": "historical",
                    "base_shock": -0.42,  # Impacto da crise subprime no Brasil
                    "description": "Crise do subprime americano"
                },
                {
                    "scenario": "Choque Taxa +3%",
                    "type": "hypothetical",
                    "base_shock": -0.15,  # Impacto de alta de juros
                    "description": "Aumento de 3 pontos percentuais na taxa Selic"
                },
                {
                    "scenario": "Recessão Global",
                    "type": "hypothetical",
                    "base_shock": -0.30,  # Cenário de recessão global
                    "description": "Cenário de recessão econômica global"
                },
                {
                    "scenario": "Crise Cambial",
                    "type": "hypothetical",
                    "base_shock": -0.25,  # Desvalorização cambial
                    "description": "Desvalorização cambial severa"
                },
            ]
            
            results = []
            for scenario in scenarios:
                # Ajustar o impacto baseado nas características do portfólio
                # - Portfólios mais voláteis tendem a ter quedas maiores
                # - Maior correlação com mercado = maior impacto em crises
                vol_factor = min(annual_volatility / 0.25, 1.5)  # Normalizado pela vol média de mercado
                correlation_factor = abs(correlation)
                
                # Para cenários históricos, usar max_drawdown como referência adicional
                if scenario["type"] == "historical":
                    # O impacto é proporcional ao drawdown histórico máximo
                    impact = scenario["base_shock"] * correlation_factor * vol_factor
                    # Limitar ao drawdown máximo observado como piso
                    if max_drawdown < 0:
                        impact = max(impact, max_drawdown * 1.2)
                else:
                    # Para cenários hipotéticos, usar VaR como base
                    impact = scenario["base_shock"] * vol_factor
                
                # Garantir que o impacto esteja em range razoável
                impact = max(min(impact, -0.05), -0.60)  # Entre -5% e -60%
                
                results.append({
                    "scenario": scenario["scenario"],
                    "impact": round(impact * 100, 1),  # Converter para percentual
                    "type": scenario["type"],
                    "description": scenario["description"]
                })
            
            # Ordenar por impacto (mais severo primeiro)
            results.sort(key=lambda x: x["impact"])
            
            return results
            
        except Exception as e:
            logging.warning(f"Erro ao gerar testes de estresse: {e}")
            return []
    
    def _generate_performance_series(self) -> list:
        """
        Gera série temporal de performance para gráficos.
        
        Returns:
            Lista de dicionários com data, valor do portfólio, benchmark e ibovespa
        """
        if self.portfolio_value is None or self.portfolio_value.empty:
            return []
        
        # Remover valores NaN do portfolio_value
        valid_portfolio = self.portfolio_value.dropna()
        
        if valid_portfolio.empty:
            return []
        
        # Calcular benchmark (CDI + 2% anual)
        # CDI aproximado de 12% ao ano, então benchmark = 14% ao ano
        annual_rate = 0.14
        daily_rate = (1 + annual_rate) ** (1/252) - 1
        
        initial_value = valid_portfolio.iloc[0]
        benchmark_values = [initial_value]
        
        for i in range(1, len(valid_portfolio)):
            benchmark_values.append(benchmark_values[-1] * (1 + daily_rate))
        
        # Buscar dados do Ibovespa
        ibov_series = None
        try:
            ibov_prices = self.data_loader.fetch_stock_prices(
                assets=['^BVSP'],
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            if not ibov_prices.empty and '^BVSP' in ibov_prices.columns:
                ibov_series = ibov_prices['^BVSP'].dropna()
                # Normalizar para começar no mesmo valor do portfólio
                if len(ibov_series) > 0:
                    ibov_initial = ibov_series.iloc[0]
                    ibov_series = ibov_series / ibov_initial * initial_value
                    # Converter o índice para string de data para facilitar a busca
                    ibov_dict = {d.strftime('%Y-%m-%d'): v for d, v in ibov_series.items()}
                    logging.info(f"Ibovespa: {len(ibov_dict)} pontos carregados")
        except Exception as e:
            logging.warning(f"Não foi possível obter dados do Ibovespa: {e}")
            ibov_dict = {}
        
        # Criar lista de dados para o gráfico (amostrar para não sobrecarregar)
        # Pegar no máximo 250 pontos para o gráfico
        step = max(1, len(valid_portfolio) // 250)
        
        result = []
        for i in range(0, len(valid_portfolio), step):
            date = valid_portfolio.index[i]
            portfolio_val = valid_portfolio.iloc[i]
            # Pular se ainda for NaN
            if pd.isna(portfolio_val):
                continue
            
            date_str = date.strftime('%Y-%m-%d')
            data_point = {
                'date': date_str,
                'portfolio': round(float(portfolio_val), 2),
                'benchmark': round(float(benchmark_values[i]), 2)
            }
            
            # Adicionar Ibovespa se disponível (usando dict para busca mais rápida)
            if ibov_series is not None and date_str in ibov_dict:
                ibov_val = ibov_dict[date_str]
                if not pd.isna(ibov_val):
                    data_point['ibovespa'] = round(float(ibov_val), 2)
            
            result.append(data_point)
        
        # Garantir que o último ponto está incluído
        if len(valid_portfolio) > 0:
            last_idx = len(valid_portfolio) - 1
            if last_idx % step != 0:
                date = valid_portfolio.index[last_idx]
                portfolio_val = valid_portfolio.iloc[last_idx]
                if not pd.isna(portfolio_val):
                    date_str = date.strftime('%Y-%m-%d')
                    data_point = {
                        'date': date_str,
                        'portfolio': round(float(portfolio_val), 2),
                        'benchmark': round(float(benchmark_values[last_idx]), 2)
                    }
                    
                    # Adicionar Ibovespa se disponível
                    if ibov_series is not None and date_str in ibov_dict:
                        ibov_val = ibov_dict[date_str]
                        if not pd.isna(ibov_val):
                            data_point['ibovespa'] = round(float(ibov_val), 2)
                    
                    result.append(data_point)
        
        return result

    def _generate_monthly_returns(self) -> list:
        """
        Gera tabela de retornos mensais do portfólio.
        
        Returns:
            Lista de dicionários com retornos mensais por ano
        """
        def safe_float(value) -> float | None:
            """Convert value to float, returning None for NaN/Infinity."""
            if value is None:
                return None
            try:
                f = float(value)
                if math.isnan(f) or math.isinf(f):
                    return None
                return round(f, 2)
            except (ValueError, TypeError):
                return None
        
        if self.portfolio_value is None or self.portfolio_value.empty:
            return []
        
        # Remover valores NaN
        valid_portfolio = self.portfolio_value.dropna()
        
        if valid_portfolio.empty:
            return []
        
        # Calcular retornos mensais do portfólio
        # Agrupar por mês e pegar o último valor
        monthly_values = valid_portfolio.resample('M').last()
        
        # Calcular retornos mensais (incluindo o primeiro mês)
        # O primeiro mês é calculado em relação ao valor inicial
        monthly_returns = pd.Series(index=monthly_values.index, dtype=float)
        
        for i, (date, value) in enumerate(monthly_values.items()):
            if i == 0:
                # Primeiro mês: retorno em relação ao valor inicial
                if self.initial_value > 0:
                    monthly_returns[date] = ((value / self.initial_value) - 1) * 100
                else:
                    monthly_returns[date] = 0.0
            else:
                # Meses subsequentes: retorno em relação ao mês anterior
                prev_value = monthly_values.iloc[i - 1]
                if prev_value > 0:
                    monthly_returns[date] = ((value / prev_value) - 1) * 100
                else:
                    monthly_returns[date] = 0.0
        
        # Buscar CDI mensal usando o método existente
        try:
            cdi_monthly = self.data_loader.compute_monthly_rf_from_cdi(
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            # Converter para percentual
            cdi_monthly = cdi_monthly * 100
        except Exception as e:
            logging.warning(f"Erro ao buscar CDI mensal: {e}")
            cdi_monthly = pd.Series(dtype=float)
        
        # Mapear meses para nomes
        month_map = {1: 'jan', 2: 'fev', 3: 'mar', 4: 'abr', 5: 'mai', 6: 'jun',
                     7: 'jul', 8: 'ago', 9: 'set_', 10: 'out', 11: 'nov', 12: 'dez'}
        
        # Obter anos únicos - usar monthly_values em vez de monthly_returns.dropna()
        years = sorted(set(monthly_values.index.year))
        result = []
        
        acum_fdo = 0.0
        acum_cdi = 0.0
        
        for year in years:
            year_data = monthly_returns[monthly_returns.index.year == year]
            year_cdi = cdi_monthly[cdi_monthly.index.year == year] if not cdi_monthly.empty else pd.Series()
            
            row = {'year': year}
            year_acum = 1.0
            year_cdi_acum = 1.0
            
            for month in range(1, 13):
                month_key = month_map[month]
                
                # Retorno do portfólio
                month_data = year_data[year_data.index.month == month]
                if not month_data.empty:
                    val = safe_float(month_data.iloc[0])
                    row[month_key] = val
                    if val is not None:
                        year_acum *= (1 + val / 100)
                else:
                    row[month_key] = None
                
                # CDI do mês
                if not year_cdi.empty:
                    month_cdi = year_cdi[year_cdi.index.month == month]
                    if not month_cdi.empty:
                        cdi_val = safe_float(month_cdi.iloc[0])
                        if cdi_val is not None:
                            year_cdi_acum *= (1 + cdi_val / 100)
            
            # Acumulado do ano do portfólio
            acum_ano = safe_float((year_acum - 1) * 100)
            row['acumAno'] = acum_ano
            
            # CDI do ano (anualizado, não acumulado)
            cdi_ano = safe_float((year_cdi_acum - 1) * 100) if not year_cdi.empty else None
            row['cdi'] = cdi_ano
            
            # Acumulado do fundo desde o início
            acum_fdo = ((1 + acum_fdo / 100) * year_acum - 1) * 100
            row['acumFdo'] = safe_float(acum_fdo)
            
            # Acumulado do CDI desde o início (composto)
            if cdi_ano is not None:
                acum_cdi = ((1 + acum_cdi / 100) * year_cdi_acum - 1) * 100
            row['acumCdi'] = safe_float(acum_cdi)
            
            result.append(row)
        
        return result

    def _generate_fama_french_analysis(self) -> dict:
        """
        Gera análise Fama-French 3 fatores para o portfólio.
        
        Returns:
            Dicionário com exposição aos fatores MKT, SMB, HML para cada ativo
        """
        try:
            # Obter preços históricos
            prices = self.data_loader.fetch_stock_prices(
                assets=self.assets,
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            
            if prices.empty:
                return {'error': 'Sem dados de preços', 'items': []}
            
            # Obter fatores FF3
            try:
                ff3 = self.data_loader.fetch_ff3_us_monthly(
                    self.start_date.strftime('%Y-%m-%d'),
                    self.end_date.strftime('%Y-%m-%d')
                )
                rf_m = self.data_loader.compute_monthly_rf_from_cdi(
                    self.start_date.strftime('%Y-%m-%d'),
                    self.end_date.strftime('%Y-%m-%d')
                )
            except Exception as e:
                logging.warning(f"Erro ao buscar fatores FF3: {e}")
                return {'error': str(e), 'items': []}
            
            if ff3 is None or ff3.empty:
                return {'error': 'Fatores FF3 não disponíveis', 'items': []}
            
            factors = ff3[['MKT_RF', 'SMB', 'HML']]
            
            # Calcular retornos mensais
            monthly_prices = prices.resample('M').last()
            monthly_returns = monthly_prices.pct_change().dropna()
            
            # Alinhar datas
            common_idx = factors.index.intersection(monthly_returns.index)
            if len(common_idx) < 5:
                return {'error': 'Insuficiente número de observações', 'items': []}
            
            factors = factors.loc[common_idx]
            monthly_returns = monthly_returns.loc[common_idx]
            rf_aligned = rf_m.reindex(common_idx).fillna(0)
            
            items = []
            avg_mkt = 0.0
            avg_smb = 0.0
            avg_hml = 0.0
            
            # Calcular pesos atuais
            weights = {}
            if self.positions is not None and self.portfolio_value is not None:
                latest_prices = prices.iloc[-1] if len(prices) > 0 else pd.Series()
                latest_positions = self.positions.iloc[-1] if len(self.positions) > 0 else pd.Series()
                latest_value = self.portfolio_value.iloc[-1] if len(self.portfolio_value) > 0 else 1
                
                for asset in self.assets:
                    if asset in latest_prices.index and asset in latest_positions.index:
                        asset_value = latest_positions[asset] * latest_prices[asset]
                        weights[asset] = asset_value / latest_value if latest_value > 0 else 0
                    else:
                        weights[asset] = 1.0 / len(self.assets)
            else:
                for asset in self.assets:
                    weights[asset] = 1.0 / len(self.assets)
            
            for asset in self.assets:
                if asset not in monthly_returns.columns:
                    continue
                
                excess_ret = monthly_returns[asset] - rf_aligned
                X = factors.values
                y = excess_ret.values
                
                # Regressão OLS
                X_with_const = np.column_stack([np.ones(len(X)), X])
                
                try:
                    # (X'X)^(-1) X'y
                    beta = np.linalg.lstsq(X_with_const, y, rcond=None)[0]
                    
                    # Calcular R²
                    y_pred = X_with_const @ beta
                    ss_res = np.sum((y - y_pred) ** 2)
                    ss_tot = np.sum((y - np.mean(y)) ** 2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                    
                    alpha_monthly = beta[0]
                    mkt_beta = beta[1]
                    smb_beta = beta[2]
                    hml_beta = beta[3]
                    
                    # Anualizar alpha
                    alpha_annual = ((1 + alpha_monthly) ** 12 - 1) * 100
                    
                    weight = weights.get(asset, 0)
                    items.append({
                        'asset': asset.replace('.SA', ''),
                        'weight': round(weight * 100, 2),
                        'alpha': round(alpha_annual, 2),
                        'mkt_beta': round(mkt_beta, 3),
                        'smb_beta': round(smb_beta, 3),
                        'hml_beta': round(hml_beta, 3),
                        'r_squared': round(r_squared, 3),
                        'n_obs': len(y)
                    })
                    
                    avg_mkt += mkt_beta * weight
                    avg_smb += smb_beta * weight
                    avg_hml += hml_beta * weight
                    
                except Exception as e:
                    logging.warning(f"Erro na regressão FF3 para {asset}: {e}")
                    continue
            
            return {
                'items': items,
                'portfolio_exposure': {
                    'mkt_beta': round(avg_mkt, 3),
                    'smb_beta': round(avg_smb, 3),
                    'hml_beta': round(avg_hml, 3)
                },
                'factor_descriptions': {
                    'MKT': 'Prêmio de Mercado (retorno do mercado - taxa livre de risco)',
                    'SMB': 'Small Minus Big (empresas menores vs maiores)',
                    'HML': 'High Minus Low (valor vs crescimento)'
                }
            }
            
        except Exception as e:
            logging.error(f"Erro ao gerar análise Fama-French: {e}")
            return {'error': str(e), 'items': []}

    def _generate_markowitz_optimization(self) -> dict:
        """
        Gera sugestão de alocação ótima usando Markowitz.
        
        Returns:
            Dicionário com pesos ótimos para diferentes objetivos
        """
        try:
            # Obter preços históricos
            prices = self.data_loader.fetch_stock_prices(
                assets=self.assets,
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            
            if prices.empty or len(self.assets) < 2:
                return {'error': 'Dados insuficientes para otimização', 'portfolios': []}
            
            # Calcular retornos diários
            returns = prices.pct_change().dropna()
            
            if returns.empty or len(returns) < 20:
                return {'error': 'Histórico insuficiente para otimização', 'portfolios': []}
            
            # Estatísticas anualizadas
            mean_returns = returns.mean() * 252
            cov_matrix = returns.cov() * 252
            
            n_assets = len(self.assets)
            
            # Taxa livre de risco (CDI aproximado)
            try:
                cdi_rates = self.data_loader.fetch_cdi_daily(
                    self.start_date.strftime('%Y-%m-%d'),
                    self.end_date.strftime('%Y-%m-%d')
                )
                rf = ((1 + cdi_rates.mean()) ** 252 - 1) if not cdi_rates.empty else 0.12
            except:
                rf = 0.12  # 12% fallback
            
            # Simulação de portfolios
            n_portfolios = 5000
            results = []
            
            np.random.seed(42)
            for _ in range(n_portfolios):
                # Pesos aleatórios (long only)
                weights = np.random.random(n_assets)
                weights /= weights.sum()
                
                # Retorno e volatilidade
                port_return = np.sum(mean_returns.values * weights)
                port_vol = np.sqrt(weights @ cov_matrix.values @ weights)
                sharpe = (port_return - rf) / port_vol if port_vol > 0 else 0
                
                results.append({
                    'weights': weights,
                    'return': port_return,
                    'volatility': port_vol,
                    'sharpe': sharpe
                })
            
            # Encontrar portfólios ótimos
            results_sorted_sharpe = sorted(results, key=lambda x: x['sharpe'], reverse=True)
            results_sorted_vol = sorted(results, key=lambda x: x['volatility'])
            results_sorted_ret = sorted(results, key=lambda x: x['return'], reverse=True)
            
            # Max Sharpe
            max_sharpe = results_sorted_sharpe[0]
            # Min Volatility
            min_vol = results_sorted_vol[0]
            # Max Return (com vol < 1.5x min vol)
            max_ret = None
            for r in results_sorted_ret:
                if r['volatility'] <= min_vol['volatility'] * 1.5:
                    max_ret = r
                    break
            if max_ret is None:
                max_ret = results_sorted_ret[0]
            
            # Pesos atuais
            current_weights = {}
            if self.positions is not None and self.portfolio_value is not None:
                latest_prices = prices.iloc[-1] if len(prices) > 0 else pd.Series()
                latest_positions = self.positions.iloc[-1] if len(self.positions) > 0 else pd.Series()
                latest_value = self.portfolio_value.iloc[-1] if len(self.portfolio_value) > 0 else 1
                
                for i, asset in enumerate(self.assets):
                    if asset in latest_prices.index and asset in latest_positions.index:
                        asset_value = latest_positions[asset] * latest_prices[asset]
                        current_weights[asset] = asset_value / latest_value if latest_value > 0 else 0
                    else:
                        current_weights[asset] = 0
            
            current_w = np.array([current_weights.get(a, 0) for a in self.assets])
            current_w = current_w / current_w.sum() if current_w.sum() > 0 else np.ones(n_assets) / n_assets
            current_return = np.sum(mean_returns.values * current_w)
            current_vol = np.sqrt(current_w @ cov_matrix.values @ current_w)
            current_sharpe = (current_return - rf) / current_vol if current_vol > 0 else 0
            
            def format_portfolio(opt_result, name):
                weights_dict = {}
                for i, asset in enumerate(self.assets):
                    weights_dict[asset.replace('.SA', '')] = round(opt_result['weights'][i] * 100, 1)
                return {
                    'name': name,
                    'weights': weights_dict,
                    'expected_return': round(opt_result['return'] * 100, 2),
                    'volatility': round(opt_result['volatility'] * 100, 2),
                    'sharpe_ratio': round(opt_result['sharpe'], 3)
                }
            
            # Fronteira eficiente (10 pontos)
            frontier = []
            vol_range = np.linspace(min_vol['volatility'], max(r['volatility'] for r in results) * 0.8, 10)
            for target_vol in vol_range:
                # Encontrar portfolio com maior retorno para essa volatilidade
                candidates = [r for r in results if abs(r['volatility'] - target_vol) < 0.02]
                if candidates:
                    best = max(candidates, key=lambda x: x['return'])
                    frontier.append({
                        'return': round(best['return'] * 100, 2),
                        'volatility': round(best['volatility'] * 100, 2),
                        'sharpe': round(best['sharpe'], 3)
                    })
            
            return {
                'current_portfolio': {
                    'name': 'Portfólio Atual',
                    'weights': {a.replace('.SA', ''): round(current_weights.get(a, 0) * 100, 1) for a in self.assets},
                    'expected_return': round(current_return * 100, 2),
                    'volatility': round(current_vol * 100, 2),
                    'sharpe_ratio': round(current_sharpe, 3)
                },
                'optimal_portfolios': [
                    format_portfolio(max_sharpe, 'Máximo Sharpe'),
                    format_portfolio(min_vol, 'Mínima Volatilidade'),
                    format_portfolio(max_ret, 'Máximo Retorno')
                ],
                'frontier': frontier,
                'risk_free_rate': round(rf * 100, 2)
            }
            
        except Exception as e:
            logging.error(f"Erro ao gerar otimização Markowitz: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e), 'portfolios': []}

    def _generate_var_backtest(self) -> dict:
        """
        Gera backtest do VaR para validar o modelo.
        
        Returns:
            Dicionário com resultados do backtest (exceções, zona Basel, etc.)
        """
        try:
            if self.portfolio_value is None or self.portfolio_value.empty:
                return {'error': 'Sem dados de portfólio', 'results': {}}
            
            valid_portfolio = self.portfolio_value.dropna()
            if len(valid_portfolio) < 100:
                return {'error': 'Histórico insuficiente para backtest (mínimo 100 dias)', 'results': {}}
            
            # Calcular retornos diários do portfólio
            portfolio_returns = valid_portfolio.pct_change().dropna()
            
            if len(portfolio_returns) < 100:
                return {'error': 'Retornos insuficientes para backtest', 'results': {}}
            
            # Parâmetros
            confidence_level = 0.99
            window = 252  # 1 ano
            
            # Rolling VaR
            exceptions = []
            var_series = []
            return_series = []
            
            for i in range(window, len(portfolio_returns)):
                hist_returns = portfolio_returns.iloc[i-window:i]
                
                # VaR histórico
                var_99 = np.percentile(hist_returns, (1 - confidence_level) * 100)
                
                # Retorno real no dia seguinte
                actual_return = portfolio_returns.iloc[i]
                
                var_series.append({
                    'date': portfolio_returns.index[i].strftime('%Y-%m-%d'),
                    'var': round(float(var_99) * 100, 2),
                    'return': round(float(actual_return) * 100, 2),
                    'exception': bool(actual_return < var_99)
                })
                
                if actual_return < var_99:
                    exceptions.append({
                        'date': portfolio_returns.index[i].strftime('%Y-%m-%d'),
                        'var': round(var_99 * 100, 2),
                        'actual_return': round(actual_return * 100, 2),
                        'breach': round((actual_return - var_99) * 100, 2)
                    })
            
            n_obs = len(var_series)
            n_exceptions = len(exceptions)
            exception_rate = n_exceptions / n_obs if n_obs > 0 else 0
            expected_rate = 1 - confidence_level  # 1% para 99%
            
            # Teste de Kupiec (POF Test)
            # H0: taxa de exceções = 1 - alpha
            if n_obs > 0 and n_exceptions > 0:
                p = expected_rate
                LR_pof = 2 * (n_exceptions * np.log(n_exceptions / (n_obs * p)) + 
                            (n_obs - n_exceptions) * np.log((n_obs - n_exceptions) / (n_obs * (1 - p))))
            else:
                LR_pof = 0
            
            # Zona Basel (baseado em número de exceções em 250 dias)
            # Verde: 0-4, Amarelo: 5-9, Vermelho: 10+
            scaled_exceptions = int(n_exceptions * (250 / n_obs)) if n_obs > 0 else 0
            if scaled_exceptions <= 4:
                basel_zone = 'green'
                basel_description = 'Modelo bem calibrado'
            elif scaled_exceptions <= 9:
                basel_zone = 'yellow'
                basel_description = 'Modelo pode precisar de ajustes'
            else:
                basel_zone = 'red'
                basel_description = 'Modelo subestima o risco'
            
            # Pegar últimos 90 dias para visualização
            recent_var_series = var_series[-90:] if len(var_series) > 90 else var_series
            
            return {
                'summary': {
                    'n_observations': n_obs,
                    'n_exceptions': n_exceptions,
                    'exception_rate': round(exception_rate * 100, 2),
                    'expected_rate': round(expected_rate * 100, 2),
                    'confidence_level': confidence_level * 100,
                    'kupiec_lr': round(float(LR_pof), 2),
                    'kupiec_critical': 6.635,  # Chi-square 1 df, 99%
                    'kupiec_pass': bool(LR_pof < 6.635)
                },
                'basel': {
                    'zone': basel_zone,
                    'description': basel_description,
                    'scaled_exceptions': scaled_exceptions
                },
                'exceptions': exceptions[-10:],  # Últimas 10 exceções
                'var_series': recent_var_series
            }
            
        except Exception as e:
            logging.error(f"Erro ao gerar backtest do VaR: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e), 'results': {}}

    def _generate_risk_attribution_detailed(self) -> dict:
        """
        Gera atribuição de risco detalhada por ativo.
        
        Returns:
            Dicionário com contribuição de cada ativo para volatilidade e VaR
        """
        try:
            # Obter preços históricos
            prices = self.data_loader.fetch_stock_prices(
                assets=self.assets,
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            
            if prices.empty:
                return {'error': 'Sem dados de preços', 'items': []}
            
            # Calcular retornos
            returns = prices.pct_change().dropna()
            
            if returns.empty:
                return {'error': 'Sem dados de retornos', 'items': []}
            
            # Calcular pesos atuais
            weights = []
            if self.positions is not None and self.portfolio_value is not None:
                latest_prices = prices.iloc[-1] if len(prices) > 0 else pd.Series()
                latest_positions = self.positions.iloc[-1] if len(self.positions) > 0 else pd.Series()
                latest_value = self.portfolio_value.iloc[-1] if len(self.portfolio_value) > 0 else 1
                
                for asset in self.assets:
                    if asset in latest_prices.index and asset in latest_positions.index:
                        asset_value = latest_positions[asset] * latest_prices[asset]
                        w = asset_value / latest_value if latest_value > 0 else 0
                    else:
                        w = 1.0 / len(self.assets)
                    weights.append(w)
            else:
                weights = [1.0 / len(self.assets)] * len(self.assets)
            
            weights = np.array(weights)
            weights = weights / weights.sum()  # Normalizar
            
            # Matriz de covariância
            cov_matrix = returns.cov().values * 252  # Anualizada
            
            # Volatilidade do portfólio
            port_vol = np.sqrt(weights @ cov_matrix @ weights)
            
            # Contribuição marginal para volatilidade (MCR)
            mcr = (cov_matrix @ weights) / port_vol if port_vol > 0 else np.zeros(len(weights))
            
            # Contribuição de risco (RC = w * MCR)
            rc = weights * mcr
            
            # Contribuição percentual
            rc_pct = (rc / port_vol) * 100 if port_vol > 0 else np.zeros(len(weights))
            
            # VaR individual
            var_99 = 2.33  # z-score para 99%
            
            items = []
            for i, asset in enumerate(self.assets):
                asset_vol = np.sqrt(cov_matrix[i, i])
                asset_var = asset_vol * var_99 * weights[i]
                
                items.append({
                    'asset': asset.replace('.SA', ''),
                    'weight': round(weights[i] * 100, 2),
                    'volatility': round(asset_vol * 100, 2),
                    'marginal_contribution': round(mcr[i] * 100, 2),
                    'risk_contribution': round(rc[i] * 100, 2),
                    'risk_contribution_pct': round(rc_pct[i], 1),
                    'var_contribution': round(asset_var * 100, 2)
                })
            
            # Ordenar por contribuição de risco
            items.sort(key=lambda x: x['risk_contribution_pct'], reverse=True)
            
            return {
                'items': items,
                'portfolio_volatility': round(port_vol * 100, 2),
                'portfolio_var_99': round(port_vol * var_99 * 100, 2),
                'concentration': {
                    'top3_risk': round(sum(x['risk_contribution_pct'] for x in items[:3]), 1),
                    'hhi': round(sum((x['risk_contribution_pct']/100)**2 for x in items) * 10000, 0)
                }
            }
            
        except Exception as e:
            logging.error(f"Erro ao gerar atribuição de risco: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e), 'items': []}

    def _generate_capm_analysis(self) -> dict:
        """
        Gera análise CAPM para cada ativo do portfólio.
        
        Returns:
            Dicionário com alpha, beta, Sharpe de cada ativo
        """
        try:
            # Obter preços históricos
            prices = self.data_loader.fetch_stock_prices(
                assets=self.assets,
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            
            if prices.empty:
                return {'error': 'Sem dados de preços', 'items': []}
            
            # Obter benchmark (IBOVESPA) - usar fetch_stock_prices que já tem cache funcionando
            try:
                ibov_prices = self.data_loader.fetch_stock_prices(
                    assets=['^BVSP'],
                    start_date=self.start_date.strftime('%Y-%m-%d'),
                    end_date=self.end_date.strftime('%Y-%m-%d')
                )
                if ibov_prices.empty:
                    return {'error': 'Dados do IBOVESPA não disponíveis', 'items': []}
                # Extrair a série do IBOVESPA
                if '^BVSP' in ibov_prices.columns:
                    ibov = ibov_prices['^BVSP']
                else:
                    ibov = ibov_prices.iloc[:, 0]  # Pegar primeira coluna
            except Exception as e:
                logging.warning(f"Erro ao buscar IBOVESPA: {e}")
                return {'error': 'Benchmark não disponível', 'items': []}
            
            if ibov is None or len(ibov) == 0:
                return {'error': 'Dados do IBOVESPA não disponíveis', 'items': []}
            
            # Calcular retornos
            returns = prices.pct_change().dropna()
            ibov_returns = ibov.pct_change().dropna()
            
            # Taxa livre de risco
            try:
                cdi_rates = self.data_loader.fetch_cdi_daily(
                    self.start_date.strftime('%Y-%m-%d'),
                    self.end_date.strftime('%Y-%m-%d')
                )
                rf_daily = cdi_rates.mean() if not cdi_rates.empty else 0.0004  # ~12% a.a.
            except:
                rf_daily = 0.0004
            
            rf_annual = (1 + rf_daily) ** 252 - 1
            
            # Alinhar datas
            common_idx = returns.index.intersection(ibov_returns.index)
            returns = returns.loc[common_idx]
            ibov_returns = ibov_returns.loc[common_idx]
            
            # Calcular pesos atuais
            weights = {}
            if self.positions is not None and self.portfolio_value is not None:
                latest_prices = prices.iloc[-1] if len(prices) > 0 else pd.Series()
                latest_positions = self.positions.iloc[-1] if len(self.positions) > 0 else pd.Series()
                latest_value = self.portfolio_value.iloc[-1] if len(self.portfolio_value) > 0 else 1
                
                for asset in self.assets:
                    if asset in latest_prices.index and asset in latest_positions.index:
                        asset_value = latest_positions[asset] * latest_prices[asset]
                        weights[asset] = asset_value / latest_value if latest_value > 0 else 0
                    else:
                        weights[asset] = 1.0 / len(self.assets)
            else:
                for asset in self.assets:
                    weights[asset] = 1.0 / len(self.assets)
            
            items = []
            portfolio_beta = 0.0
            portfolio_alpha = 0.0
            
            for asset in self.assets:
                if asset not in returns.columns:
                    continue
                
                asset_ret = returns[asset]
                
                # Excess returns
                excess_asset = asset_ret - rf_daily
                excess_market = ibov_returns - rf_daily
                
                # Regressão CAPM: R_i - Rf = alpha + beta * (R_m - Rf)
                X = excess_market.values.reshape(-1, 1)
                y = excess_asset.values
                
                # Adicionar constante
                X_with_const = np.column_stack([np.ones(len(X)), X])
                
                try:
                    beta_coef = np.linalg.lstsq(X_with_const, y, rcond=None)[0]
                    alpha_daily = beta_coef[0]
                    beta = beta_coef[1]
                    
                    # R²
                    y_pred = X_with_const @ beta_coef
                    ss_res = np.sum((y - y_pred) ** 2)
                    ss_tot = np.sum((y - np.mean(y)) ** 2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                    
                    # Anualizar alpha
                    alpha_annual = ((1 + alpha_daily) ** 252 - 1) * 100
                    
                    # Sharpe do ativo
                    asset_return_annual = (1 + asset_ret.mean()) ** 252 - 1
                    asset_vol_annual = asset_ret.std() * np.sqrt(252)
                    sharpe = (asset_return_annual - rf_annual) / asset_vol_annual if asset_vol_annual > 0 else 0
                    
                    # Treynor ratio
                    treynor = (asset_return_annual - rf_annual) / beta if beta != 0 else 0
                    
                    weight = weights.get(asset, 0)
                    items.append({
                        'asset': asset.replace('.SA', ''),
                        'weight': round(weight * 100, 2),
                        'alpha': round(alpha_annual, 2),
                        'beta': round(beta, 3),
                        'r_squared': round(r_squared, 3),
                        'sharpe': round(sharpe, 3),
                        'treynor': round(treynor * 100, 2),
                        'annualized_return': round(asset_return_annual * 100, 2),
                        'annualized_volatility': round(asset_vol_annual * 100, 2)
                    })
                    
                    portfolio_beta += beta * weight
                    portfolio_alpha += alpha_annual * weight
                    
                except Exception as e:
                    logging.warning(f"Erro no CAPM para {asset}: {e}")
                    continue
            
            # Ordenar por alpha (performance ajustada ao risco)
            items.sort(key=lambda x: x['alpha'], reverse=True)
            
            return {
                'items': items,
                'portfolio_metrics': {
                    'beta': round(portfolio_beta, 3),
                    'alpha': round(portfolio_alpha, 2)
                },
                'benchmark': 'IBOVESPA',
                'risk_free_rate': round(rf_annual * 100, 2)
            }
            
        except Exception as e:
            logging.error(f"Erro ao gerar análise CAPM: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e), 'items': []}

    def _generate_incremental_var(self) -> dict:
        """
        Gera Incremental VaR - impacto de cada ativo no VaR do portfólio.
        
        Returns:
            Dicionário com IVaR e MVaR para cada ativo
        """
        try:
            # Obter preços históricos
            prices = self.data_loader.fetch_stock_prices(
                assets=self.assets,
                start_date=self.start_date.strftime('%Y-%m-%d'),
                end_date=self.end_date.strftime('%Y-%m-%d')
            )
            
            if prices.empty:
                return {'error': 'Sem dados de preços', 'items': []}
            
            # Calcular retornos
            returns = prices.pct_change().dropna()
            
            if returns.empty:
                return {'error': 'Sem dados de retornos', 'items': []}
            
            # Calcular pesos atuais
            weights = []
            weights_dict = {}
            if self.positions is not None and self.portfolio_value is not None:
                latest_prices = prices.iloc[-1] if len(prices) > 0 else pd.Series()
                latest_positions = self.positions.iloc[-1] if len(self.positions) > 0 else pd.Series()
                latest_value = self.portfolio_value.iloc[-1] if len(self.portfolio_value) > 0 else 1
                
                for asset in self.assets:
                    if asset in latest_prices.index and asset in latest_positions.index:
                        asset_value = latest_positions[asset] * latest_prices[asset]
                        w = asset_value / latest_value if latest_value > 0 else 0
                    else:
                        w = 1.0 / len(self.assets)
                    weights.append(w)
                    weights_dict[asset] = w
            else:
                for asset in self.assets:
                    w = 1.0 / len(self.assets)
                    weights.append(w)
                    weights_dict[asset] = w
            
            weights = np.array(weights)
            weights = weights / weights.sum()  # Normalizar
            
            # VaR paramétrico a 99%
            confidence = 0.99
            z_score = 2.33  # Para 99%
            
            # Matriz de covariância anualizada
            cov_matrix = returns.cov().values * 252
            
            # VaR do portfólio atual
            port_vol = np.sqrt(weights @ cov_matrix @ weights)
            port_var = port_vol * z_score
            
            # Calcular retornos do portfólio
            port_returns = (returns @ weights).dropna()
            
            items = []
            
            for i, asset in enumerate(self.assets):
                # Incremental VaR: VaR(port + delta) - VaR(port)
                # Aproximação: delta * w * MVaR
                delta = 0.01  # 1% de incremento
                
                # Marginal VaR (derivada parcial do VaR em relação ao peso)
                mvar = (cov_matrix @ weights)[i] / port_vol * z_score if port_vol > 0 else 0
                
                # Incremental VaR
                ivar = mvar * weights[i]
                
                # Component VaR (contribuição para o VaR)
                cvar_contrib = weights[i] * mvar
                cvar_pct = (cvar_contrib / port_var) * 100 if port_var > 0 else 0
                
                # VaR individual do ativo
                asset_vol = np.sqrt(cov_matrix[i, i])
                asset_var = asset_vol * z_score
                
                # Diversification benefit
                div_benefit = asset_var * weights[i] - cvar_contrib
                
                items.append({
                    'asset': asset.replace('.SA', ''),
                    'weight': round(weights[i] * 100, 2),
                    'individual_var': round(asset_var * 100, 2),
                    'marginal_var': round(mvar * 100, 4),
                    'incremental_var': round(ivar * 100, 4),
                    'component_var': round(cvar_contrib * 100, 2),
                    'var_contribution_pct': round(cvar_pct, 1),
                    'diversification_benefit': round(div_benefit * 100, 2)
                })
            
            # Ordenar por contribuição ao VaR
            items.sort(key=lambda x: x['var_contribution_pct'], reverse=True)
            
            # Benefício de diversificação total
            sum_individual_var = sum(item['individual_var'] * item['weight'] / 100 for item in items)
            total_div_benefit = sum_individual_var - port_var * 100
            
            return {
                'items': items,
                'portfolio_var': round(port_var * 100, 2),
                'undiversified_var': round(sum_individual_var, 2),
                'diversification_benefit': round(total_div_benefit, 2),
                'diversification_ratio': round(sum_individual_var / (port_var * 100), 2) if port_var > 0 else 1,
                'confidence_level': confidence * 100
            }
            
        except Exception as e:
            logging.error(f"Erro ao gerar Incremental VaR: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e), 'items': []}
