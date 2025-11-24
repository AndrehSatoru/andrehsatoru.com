# core/comprehensive_visualization.py
# Utilitário abrangente para geração de todos os gráficos e criação de PNGs

import os
import io
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backend_projeto.domain.technical_analysis import moving_averages, macd_series
from backend_projeto.infrastructure.visualization.ta_visualization import plot_price_with_ma, plot_macd, plot_combined_ta
from backend_projeto.infrastructure.visualization.visualization import efficient_frontier_image
from backend_projeto.infrastructure.visualization.factor_visualization import plot_ff_factors, plot_ff_betas
from backend_projeto.infrastructure.utils.config import Settings
from backend_projeto.infrastructure.data_handling import YFinanceProvider


class ComprehensiveVisualizer:
    """Utilitário abrangente para geração de todos os tipos de gráficos e salvamento em PNG."""

    def __init__(self, config: Settings = None, output_dir: str = "generated_plots"):
        """Inicializa o visualizador.

        Args:
            config: Configuração da aplicação
            output_dir: Diretório onde salvar os gráficos
        """
        self.config = config or Settings()
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)

        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)

    def generate_all_charts(
        self,
        assets: List[str],
        start_date: str,
        end_date: str,
        loader: YFinanceProvider,
        plot_configs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Gera todos os tipos de gráficos disponíveis e salva como PNG.

        Args:
            assets: Lista de ativos para análise
            start_date: Data de início
            end_date: Data de fim
            loader: YFinanceProvider para buscar dados
            plot_configs: Configurações específicas para cada tipo de gráfico

        Returns:
            Dicionário com caminhos dos arquivos gerados
        """
        self.logger.info(f"Gerando gráficos para {len(assets)} ativos de {start_date} a {end_date}")

        plot_configs = plot_configs or {}
        generated_files = {}

        try:
            # Buscar dados de preços
            prices = loader.fetch_stock_prices(assets, start_date, end_date)

            for asset in assets:
                if asset not in prices.columns:
                    self.logger.warning(f"Ativo {asset} não encontrado nos dados")
                    continue

                # 1. Gráficos de Análise Técnica
                ta_charts = self._generate_technical_analysis_charts(prices, asset, plot_configs)
                generated_files.update(ta_charts)

                # 2. Gráficos de Fatores Fama-French (se disponível)
                try:
                    ff_charts = self._generate_fama_french_charts(loader, asset, start_date, end_date, plot_configs)
                    generated_files.update(ff_charts)
                except Exception as e:
                    self.logger.warning(f"Erro ao gerar gráficos FF para {asset}: {e}")

            # 3. Fronteira Eficiente (para múltiplos ativos)
            if len(assets) >= 2:
                try:
                    frontier_chart = self._generate_efficient_frontier_chart(loader, assets, start_date, end_date, plot_configs)
                    generated_files.update(frontier_chart)
                except Exception as e:
                    self.logger.warning(f"Erro ao gerar fronteira eficiente: {e}")

            self.logger.info(f"Gerados {len(generated_files)} gráficos com sucesso")
            return generated_files

        except Exception as e:
            self.logger.error(f"Erro ao gerar gráficos: {e}")
            raise

    def _generate_technical_analysis_charts(
        self, prices: pd.DataFrame, asset: str, plot_configs: Dict[str, Any]
    ) -> Dict[str, str]:
        """Gera gráficos de análise técnica para um ativo."""
        generated_files = {}

        # Configurações padrão para TA
        ta_config = plot_configs.get('technical_analysis', {})
        ma_windows = ta_config.get('ma_windows', [5, 21])
        ma_method = ta_config.get('ma_method', 'sma')
        macd_fast = ta_config.get('macd_fast', 12)
        macd_slow = ta_config.get('macd_slow', 26)
        macd_signal = ta_config.get('macd_signal', 9)

        try:
            # Gráfico de Médias Móveis
            ma_bytes = plot_price_with_ma(prices, asset, windows=ma_windows, method=ma_method)
            ma_file = self._save_chart_bytes(ma_bytes, f"{asset}_moving_averages.png")
            generated_files[f"{asset}_ma"] = ma_file

            # Gráfico MACD
            macd_bytes = plot_macd(prices, asset, fast=macd_fast, slow=macd_slow, signal=macd_signal)
            macd_file = self._save_chart_bytes(macd_bytes, f"{asset}_macd.png")
            generated_files[f"{asset}_macd"] = macd_file

            # Gráfico Combinado
            combined_bytes = plot_combined_ta(
                prices, asset,
                ma_windows=ma_windows, ma_method=ma_method,
                macd_fast=macd_fast, macd_slow=macd_slow, macd_signal=macd_signal
            )
            combined_file = self._save_chart_bytes(combined_bytes, f"{asset}_combined_ta.png")
            generated_files[f"{asset}_combined"] = combined_file

        except Exception as e:
            self.logger.error(f"Erro ao gerar gráficos TA para {asset}: {e}")

        return generated_files

    def _generate_fama_french_charts(
        self, loader: YFinanceProvider, asset: str, start_date: str, end_date: str, plot_configs: Dict[str, Any]
    ) -> Dict[str, str]:
        """Gera gráficos de fatores Fama-French para um ativo."""
        generated_files = {}

        # Configurações padrão para FF
        ff_config = plot_configs.get('fama_french', {})
        model = ff_config.get('model', 'ff3')
        rf_source = ff_config.get('rf_source', 'selic')
        convert_to_usd = ff_config.get('convert_to_usd', False)

        try:
            # Gráfico de Fatores (FF3 ou FF5)
            if model == 'ff3':
                ff = loader.fetch_ff3_us_monthly(start_date, end_date)
                factors = ff[['MKT_RF', 'SMB', 'HML']]
            else:
                ff = loader.fetch_ff5_us_monthly(start_date, end_date)
                factors = ff[['MKT_RF', 'SMB', 'HML', 'RMW', 'CMA']]

            factors_bytes = plot_ff_factors(factors)
            factors_file = self._save_chart_bytes(factors_bytes, f"{asset}_{model}_factors.png")
            generated_files[f"{asset}_{model}_factors"] = factors_file

            # Gráfico de Betas do ativo
            prices = loader.fetch_stock_prices([asset], start_date, end_date)
            if convert_to_usd:
                # Conversão seria implementada aqui se necessário
                pass

            # Calcular betas (simplificado - na prática usaria o RiskEngine)
            betas = self._calculate_asset_betas(prices, factors, model, rf_source, loader, start_date, end_date)

            if betas:
                betas_bytes = plot_ff_betas(betas, model=model, title=f"{asset} - {model} Betas")
                betas_file = self._save_chart_bytes(betas_bytes, f"{asset}_{model}_betas.png")
                generated_files[f"{asset}_{model}_betas"] = betas_file

        except Exception as e:
            self.logger.error(f"Erro ao gerar gráficos FF para {asset}: {e}")

        return generated_files

    def _calculate_asset_betas(
        self, prices: pd.DataFrame, factors: pd.DataFrame, model: str, rf_source: str,
        loader: YFinanceProvider, start_date: str, end_date: str
    ) -> Dict[str, float]:
        """Calcula betas de um ativo usando modelo Fama-French (simplificado)."""
        # Esta é uma implementação simplificada
        # Na prática, usaria as funções existentes do RiskEngine
        try:
            from backend_projeto.domain.analysis import ff3_metrics, ff5_metrics

            # RF mensal
            if rf_source == 'ff':
                rf_m = factors['RF'] if 'RF' in factors.columns else pd.Series(0, index=factors.index)
            elif rf_source == 'selic':
                rf_m = loader.compute_monthly_rf_from_cdi(start_date, end_date)
            else:
                us10y = loader.fetch_us10y_monthly_yield(start_date, end_date)
                rf_m = ((1.0 + (us10y / 100.0)) ** (1.0 / 12.0) - 1.0)

            if model == 'ff3':
                result = ff3_metrics(prices, factors[['MKT_RF', 'SMB', 'HML']], rf_m, [prices.columns[0]])
            else:
                result = ff5_metrics(prices, factors, rf_m, [prices.columns[0]])

            asset_result = result.get('results', {}).get(prices.columns[0], {})
            return {
                'beta_mkt': asset_result.get('beta_mkt', 0),
                'beta_smb': asset_result.get('beta_smb', 0),
                'beta_hml': asset_result.get('beta_hml', 0),
                'beta_rmw': asset_result.get('beta_rmw', 0),
                'beta_cma': asset_result.get('beta_cma', 0),
            }
        except Exception as e:
            self.logger.warning(f"Erro ao calcular betas: {e}")
            return {}

    def _generate_efficient_frontier_chart(
        self, loader: YFinanceProvider, assets: List[str], start_date: str, end_date: str, plot_configs: Dict[str, Any]
    ) -> Dict[str, str]:
        """Gera gráfico da fronteira eficiente."""
        generated_files = {}

        # Configurações padrão para fronteira eficiente
        frontier_config = plot_configs.get('efficient_frontier', {})
        n_samples = frontier_config.get('n_samples', 5000)
        rf = frontier_config.get('rf', 0.0)

        try:
            frontier_bytes = efficient_frontier_image(
                loader, self.config, assets, start_date, end_date,
                n_samples=n_samples, rf=rf
            )
            frontier_file = self._save_chart_bytes(frontier_bytes, "efficient_frontier.png")
            generated_files["efficient_frontier"] = frontier_file

        except Exception as e:
            self.logger.error(f"Erro ao gerar fronteira eficiente: {e}")

        return generated_files

    def _save_chart_bytes(self, chart_bytes: bytes, filename: str) -> str:
        """Salva bytes de gráfico em arquivo PNG."""
        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, 'wb') as f:
                f.write(chart_bytes)
            self.logger.debug(f"Gráfico salvo: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Erro ao salvar gráfico {filename}: {e}")
            raise

    def generate_batch_charts(
        self,
        chart_requests: List[Dict[str, Any]],
        loader: YFinanceProvider,
        parallel: bool = False
    ) -> Dict[str, str]:
        """Gera múltiplos gráficos em lote.

        Args:
            chart_requests: Lista de dicionários com configurações de gráficos
            loader: YFinanceProvider para buscar dados
            parallel: Se deve processar em paralelo (não implementado)

        Returns:
            Dicionário com caminhos dos arquivos gerados
        """
        all_files = {}

        for request in chart_requests:
            try:
                chart_type = request.get('type', 'all')
                assets = request.get('assets', [])
                start_date = request.get('start_date')
                end_date = request.get('end_date')
                plot_configs = request.get('plot_configs', {})

                if chart_type == 'all':
                    files = self.generate_all_charts(assets, start_date, end_date, loader, plot_configs)
                else:
                    # Gera apenas o tipo específico
                    files = self._generate_specific_chart_type(chart_type, assets, start_date, end_date, loader, plot_configs)

                all_files.update(files)

            except Exception as e:
                self.logger.error(f"Erro ao gerar gráficos do lote: {e}")

        return all_files

    def _generate_specific_chart_type(
        self, chart_type: str, assets: List[str], start_date: str, end_date: str,
        loader: YFinanceProvider, plot_configs: Dict[str, Any]
    ) -> Dict[str, str]:
        """Gera apenas um tipo específico de gráfico."""
        if chart_type == 'technical_analysis':
            prices = loader.fetch_stock_prices(assets, start_date, end_date)
            return self._generate_technical_analysis_charts(prices, assets[0] if assets else '', plot_configs)
        elif chart_type == 'fama_french':
            return self._generate_fama_french_charts(loader, assets[0] if assets else '', start_date, end_date, plot_configs)
        elif chart_type == 'efficient_frontier':
            return self._generate_efficient_frontier_chart(loader, assets, start_date, end_date, plot_configs)
        else:
            raise ValueError(f"Tipo de gráfico não suportado: {chart_type}")

    def list_generated_files(self) -> List[str]:
        """Lista todos os arquivos de gráficos gerados."""
        if not os.path.exists(self.output_dir):
            return []

        files = []
        for filename in os.listdir(self.output_dir):
            if filename.endswith('.png'):
                filepath = os.path.join(self.output_dir, filename)
                files.append(filepath)

        return sorted(files)

    def cleanup_old_files(self, days_old: int = 7) -> int:
        """Remove arquivos de gráficos mais antigos que X dias.

        Args:
            days_old: Número de dias para considerar arquivos como antigos

        Returns:
            Número de arquivos removidos
        """
        if not os.path.exists(self.output_dir):
            return 0

        import time
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        removed_count = 0

        for filename in os.listdir(self.output_dir):
            if filename.endswith('.png'):
                filepath = os.path.join(self.output_dir, filename)
                if os.path.getmtime(filepath) < cutoff_time:
                    try:
                        os.remove(filepath)
                        removed_count += 1
                        self.logger.debug(f"Arquivo removido: {filepath}")
                    except Exception as e:
                        self.logger.error(f"Erro ao remover arquivo {filepath}: {e}")

        self.logger.info(f"Removidos {removed_count} arquivos antigos")
        return removed_count


# Função de conveniência para uso rápido
def generate_comprehensive_charts(
    assets: List[str],
    start_date: str,
    end_date: str,
    loader: YFinanceProvider,
    output_dir: str = "generated_plots",
    plot_configs: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """Função de conveniência para gerar todos os gráficos de uma vez."""
    visualizer = ComprehensiveVisualizer(output_dir=output_dir)
    return visualizer.generate_all_charts(assets, start_date, end_date, loader, plot_configs)