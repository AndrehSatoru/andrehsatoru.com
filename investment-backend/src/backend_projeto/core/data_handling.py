# core/data_handling.py
# Classes DataProvider, YFinanceProvider, DataLoader, DataCleaner, DataValidator

import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from bcb import sgs
import numpy as np
import time
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from abc import ABC, abstractmethod
from ..utils.cache import CacheManager
from ..utils.config import Config
from .exceptions import (
    DataProviderError,
    InvalidTransactionFileError,
    DataValidationError,
)

class DataProvider(ABC):
    @abstractmethod
    def fetch_asset_info(self, assets: List[str]) -> Dict[str, str]: pass
    @abstractmethod
    def fetch_stock_prices(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame: pass
    @abstractmethod
    def fetch_dividends(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame: pass
    @abstractmethod
    def fetch_exchange_rates(self, currencies: List[str], start_date: str, end_date: str) -> pd.DataFrame: pass
    @abstractmethod
    def fetch_benchmark_data(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.Series]: pass
    @abstractmethod
    def fetch_market_caps(self, assets: List[str]) -> Dict[str, float]: pass

class YFinanceProvider(DataProvider):
    """Provider para dados do YFinance com retry e circuit breaker."""
    
    def __init__(self, cache_dir: str = 'cache', max_retries: int = 3, backoff_factor: float = 2.0, timeout: int = 30):
        self.cache = CacheManager(cache_dir=cache_dir)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        self.consecutive_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_open = False
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Executa função com retry e backoff exponencial."""
        if self.circuit_open:
            logging.error("[YFinance] Circuit breaker OPEN - bloqueando requisição")
            raise DataProviderError("Circuit breaker aberto - muitas falhas consecutivas")
        
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                result = func(*args, **kwargs)
                # Sucesso - resetar contador de falhas
                self.consecutive_failures = 0
                if self.circuit_open:
                    logging.info("[YFinance] Circuit breaker FECHADO - serviço recuperado")
                    self.circuit_open = False
                return result
            except Exception as e:
                last_exception = e
                wait_time = self.backoff_factor ** attempt
                logging.warning(
                    f"[YFinance] Tentativa {attempt + 1}/{self.max_retries} falhou. "
                    f"Aguardando {wait_time:.1f}s. Erro: {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
        
        # Todas as tentativas falharam
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.circuit_breaker_threshold:
            self.circuit_open = True
            logging.critical(
                f"[YFinance] Circuit breaker ABERTO após {self.consecutive_failures} falhas consecutivas"
            )
        
        raise last_exception
    def fetch_asset_info(self, assets: List[str]) -> Dict[str, str]:
        logging.info("[YFinance] Buscando informação (moeda) dos ativos...")
        asset_currencies = {}
        for asset in assets:
            try:
                default_currency = 'BRL' if '.SA' in asset.upper() else 'USD'
                currency = yf.Ticker(asset).info.get('currency', default_currency)
                asset_currencies[asset] = currency.upper()
                time.sleep(0.1)
            except Exception as e:
                logging.warning(f"[YFinance] Não foi possível buscar a moeda para {asset}. Assumindo padrão. Erro: {e}")
                asset_currencies[asset] = 'BRL' if '.SA' in asset.upper() else 'USD'
        return asset_currencies
    def fetch_stock_prices(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        logging.info(f"[YFinance] Buscando cotações para {len(assets)} ativos...")
        use_cache = pd.to_datetime(end_date).date() < pd.Timestamp.now().date()
        if use_cache:
            cached_df = self.cache.get_dataframe('prices', assets, start_date, end_date)
            if cached_df is not None:
                logging.info(f"[CACHE] HIT: Retornando dados cacheados")
                return cached_df
        logging.info(f"[CACHE] MISS: Buscando dados de cotações via API.")
        end_date_download = pd.to_datetime(end_date) + pd.Timedelta(days=1)
        
        def _download():
            return yf.download(assets, start=start_date, end=end_date_download, auto_adjust=False, progress=False, timeout=self.timeout)['Close']
        
        try:
            df = self._retry_with_backoff(_download)
            if isinstance(df, pd.Series): df = df.to_frame(name=assets[0])
            if use_cache:
                self.cache.set_dataframe(df, 'prices', assets, start_date, end_date)
            return df
        except Exception as e:
            logging.critical(f"[YFinance] Falha crítica ao baixar cotações: {e}")
            raise DataProviderError(
                "Falha ao baixar cotações",
                details={"assets": assets, "start_date": start_date, "end_date": end_date}
            )
    def fetch_dividends(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        logging.info("[YFinance] Buscando histórico de proventos...")
        use_cache = pd.to_datetime(end_date).date() < pd.Timestamp.now().date()
        if use_cache:
            cached_df = self.cache.get_dataframe('dividends', assets, start_date, end_date)
            if cached_df is not None:
                return cached_df
        logging.info(f"[CACHE] MISS: Buscando dados de proventos via API.")
        all_dividends = []
        try:
            for asset in assets:
                ticker = yf.Ticker(asset)
                df_temp = ticker.dividends
                df_temp = df_temp.loc[start_date:end_date]
                if not df_temp.empty:
                    df_temp = df_temp.to_frame(name='ValorPorAcao')
                    df_temp['Ativo'] = asset
                    all_dividends.append(df_temp)
                time.sleep(0.1)
            if not all_dividends: 
                final_df = pd.DataFrame()
            else:
                final_df = pd.concat(all_dividends)
            if use_cache:
                self.cache.set_dataframe(final_df, 'dividends', assets, start_date, end_date)
            return final_df
        except Exception as e:
            logging.error(f"[YFinance] Erro ao buscar proventos: {e}", exc_info=True)
            raise DataProviderError(
                "Falha ao buscar proventos",
                details={"assets": assets, "start_date": start_date, "end_date": end_date}
            )
    def fetch_exchange_rates(self, currencies: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        logging.info(f"[YFinance] Buscando taxas de câmbio para: {currencies}")
        tickers = [f"{currency}BRL=X" for currency in currencies]
        use_cache = pd.to_datetime(end_date).date() < pd.Timestamp.now().date()
        if use_cache:
            cached_df = self.cache.get_dataframe('exchange', currencies, start_date, end_date)
            if cached_df is not None:
                return cached_df
        logging.info(f"[CACHE] MISS: Buscando dados de câmbio via API.")
        try:
            end_date_download = pd.to_datetime(end_date) + pd.Timedelta(days=1)
            exchange_df = yf.download(tickers, start=start_date, end=end_date_download, progress=False, auto_adjust=False)['Close']
            if isinstance(exchange_df, pd.Series): exchange_df = exchange_df.to_frame(name=tickers[0])
            rename_map = {col: col.replace('BRL=X', '') for col in exchange_df.columns}
            exchange_df.rename(columns=rename_map, inplace=True)
            if use_cache:
                self.cache.set_dataframe(exchange_df, 'exchange', currencies, start_date, end_date)
            return exchange_df
        except Exception as e:
            logging.error(f"[YFinance] Falha ao buscar dados de câmbio: {e}", exc_info=True)
            raise DataProviderError(
                "Falha ao buscar dados de câmbio",
                details={"currencies": currencies, "start_date": start_date, "end_date": end_date}
            )
    def fetch_benchmark_data(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.Series]:
        logging.info(f"[YFinance] Buscando dados do benchmark '{ticker}'...")
        use_cache = pd.to_datetime(end_date).date() < pd.Timestamp.now().date()
        if use_cache:
            cached_df = self.cache.get_dataframe('benchmark', [ticker], start_date, end_date)
            if cached_df is not None:
                return cached_df.iloc[:, 0]
        logging.info(f"[CACHE] MISS: Buscando dados do benchmark via API.")
        try:
            end_date_download = (pd.to_datetime(end_date) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            benchmark_df = yf.download(ticker, start=start_date, end=end_date_download, progress=False, auto_adjust=False)
            if benchmark_df.empty or 'Close' not in benchmark_df.columns: return None
            close_series = benchmark_df['Close']
            if isinstance(close_series, pd.DataFrame): close_series = close_series.iloc[:, 0]
            close_series.index = pd.to_datetime(close_series.index).tz_localize(None)
            if use_cache:
                self.cache.set_dataframe(close_series.to_frame(), 'benchmark', [ticker], start_date, end_date)
            return close_series
        except Exception as e:
            logging.error(f"[YFinance] Erro ao buscar dados do benchmark '{ticker}': {e}", exc_info=True)
            raise DataProviderError(
                f"Falha ao buscar dados do benchmark '{ticker}'",
                details={"ticker": ticker, "start_date": start_date, "end_date": end_date}
            )
    def fetch_market_caps(self, assets: List[str]) -> Dict[str, float]:
        logging.info("[YFinance] Buscando market caps...")
        market_caps = {}
        for asset in assets:
            try:
                cap = yf.Ticker(asset).info.get('marketCap')
                if cap:
                    market_caps[asset] = float(cap)
                else:
                    logging.warning(f"Market cap não encontrado para {asset}. Será excluído do cálculo de equilíbrio.")
                    market_caps[asset] = 0.0
                time.sleep(0.1)
            except Exception as e:
                logging.error(f"Falha ao buscar market cap para {asset}: {e}")
                market_caps[asset] = 0.0
        return market_caps

class DataValidator:
    def __init__(self, extreme_return_threshold: float = 0.5, audit_threshold: float = 0.10):
        self.threshold = extreme_return_threshold
        self.audit_threshold = audit_threshold
        self.audit_events = []
        logging.info(f"DataValidator inicializado com threshold de aviso de {self.threshold:.2%} e de auditoria de {self.audit_threshold:.2%}.")
    def validate_and_audit_timeseries(self, df: pd.DataFrame, data_type: str):
        if df is None or df.empty: return
        logging.info(f"Executando auditoria de retornos para dados do tipo: '{data_type}'...")
        daily_returns = df.pct_change(fill_method=None)
        prices_shifted = df.shift(1)
        for asset in daily_returns.columns:
            extreme_events = daily_returns[daily_returns[asset].abs() > self.audit_threshold][asset]
            if not extreme_events.empty:
                for date, ret in extreme_events.items():
                    self.audit_events.append({
                        'Tipo_Dado': data_type, 'Ativo': asset, 'Data': date.strftime('%Y-%m-%d'),
                        'Retorno': ret, 'Valor_Anterior': prices_shifted.loc[date, asset],
                        'Valor_Atual': df.loc[date, asset]
                    })
                    if abs(ret) > self.threshold:
                        logging.warning(f"[VALIDATION] Retorno extremo detectado para '{asset}' ({data_type}) em {date.strftime('%Y-%m-%d')}: {ret:.2%}.")
    def save_audit_report(self, output_dir: Path):
        if not self.audit_events:
            logging.info("Auditoria de dados concluída. Nenhum evento acima do threshold foi encontrado.")
            return
        report_df = pd.DataFrame(self.audit_events)
        report_df.sort_values(by=['Retorno'], ascending=True, inplace=True)
        filename = output_dir / "auditoria_retornos_extremos.csv"
        try:
            report_df.to_csv(filename, index=False, sep=';', decimal=',', float_format='%.4f')
            logging.warning(f"AUDITORIA DE DADOS: {len(report_df)} evento(s) anômalos foram registrados. Verifique o arquivo: {filename}")
        except Exception as e:
            logging.error(f"Falha ao salvar o relatório de auditoria: {e}")

class DataCleaner:
    def __init__(self, adjustments: Dict[str, List[Tuple[str, any]]]):
        self.adjustments = adjustments
        logging.info("DataCleaner inicializado com as correções manuais programadas.")

    def adjust_prices(self, df_prices: pd.DataFrame) -> pd.DataFrame:
        if not self.adjustments or df_prices is None or df_prices.empty:
            return df_prices
        df_adjusted = df_prices.copy()
        for asset, events in self.adjustments.items():
            if asset in df_adjusted.columns:
                for date_str, instruction in sorted(events, key=lambda x: x[0]):
                    try:
                        event_date = pd.to_datetime(date_str)
                        if isinstance(instruction, (int, float)):
                            df_adjusted.loc[df_adjusted.index < event_date, asset] /= instruction
                            logging.info(f"[DataCleaner] Ajuste de Fator ({instruction:.4f}) aplicado para '{asset}' antes de {date_str}.")
                        elif instruction == 'forward_fill':
                            if event_date in df_adjusted.index:
                                loc = df_adjusted.index.get_loc(event_date)
                                if loc > 0:
                                    df_adjusted.loc[event_date, asset] = df_adjusted.iloc[loc - 1][asset]
                                    logging.info(f"[DataCleaner] Correção 'forward_fill' aplicada para '{asset}' no dia {date_str}.")
                    except Exception as e:
                        logging.error(f"Não foi possível aplicar o ajuste para {asset} em {date_str}: {e}")
        return df_adjusted

class DataLoader:
    def __init__(self, provider: DataProvider, config: Config, retries: int = 3, delay: int = 2):
        self.provider = provider
        self.validator = DataValidator()
        self.config = config
        self.retries = retries
        self.delay = delay
        logging.info(f"DataLoader inicializado com o provedor: {provider.__class__.__name__}.")
    def load_transactions(self, filepath: Path) -> pd.DataFrame:
        logging.info(f"Carregando transações de '{filepath}'...")
        try:
            df = pd.read_excel(filepath)
            df['Data'] = pd.to_datetime(df['Data'])
            logging.info("Transações carregadas com sucesso.")
            return df.sort_values(by='Data')
        except FileNotFoundError:
            logging.critical(f"Arquivo de transações '{filepath}' não encontrado.")
            raise InvalidTransactionFileError(
                "Arquivo de transações não encontrado",
                details={"path": str(filepath)}
            )
        except Exception as e:
            logging.critical(f"Erro ao carregar o arquivo de transações: {e}")
            raise InvalidTransactionFileError(
                "Erro ao carregar o arquivo de transações",
                details={"path": str(filepath), "cause": str(e)}
            )
    def fetch_asset_info(self, assets: List[str]) -> Dict[str, str]:
        return self.provider.fetch_asset_info(assets)
    def fetch_stock_prices(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        df = self.provider.fetch_stock_prices(assets, start_date, end_date)
        if df.empty:
            logging.critical("Nenhuma cotação foi baixada. A simulação não pode continuar.")
            raise DataProviderError(
                "Nenhuma cotação foi baixada",
                details={"assets": assets, "start_date": start_date, "end_date": end_date}
            )
        self.validator.validate_and_audit_timeseries(df, data_type="Ações")
        for asset in df.columns:
            if df[asset].isnull().any():
                nan_blocks = df[asset].isnull().astype(int).groupby(df[asset].notnull().astype(int).cumsum()).sum()
                max_consecutive_nans = nan_blocks.max()
                if max_consecutive_nans > self.config.CONSECUTIVE_NAN_THRESHOLD:
                    logging.warning(f"[DATA QUALITY] Ativo '{asset}' tem um máximo de {max_consecutive_nans} cotações faltantes consecutivas. Verifique a liquidez/listagem do ativo.")
        valid_assets = [a for a in df.columns if a in df.columns and df[a].notna().any()]
        df_cleaned = df[valid_assets].ffill().bfill()
        logging.info("Cotações baixadas e processadas com sucesso.")
        return df_cleaned
    def fetch_cdi(self, start_date: str, end_date: str) -> pd.DataFrame:
        logging.info("Buscando dados do CDI no Banco Central...")
        last_error = None
        for attempt in range(self.retries):
            try:
                cdi = sgs.get({'CDI': 12}, start=start_date, end=end_date)
                if cdi.empty:
                    logging.warning("Nenhum dado de CDI retornado pelo BCB.")
                    raise DataProviderError(
                        "BCB retornou dados vazios para CDI",
                        details={"start_date": start_date, "end_date": end_date}
                    )
                cdi['CDI_rate'] = cdi['CDI']
                cdi['fator_diario'] = (1 + cdi['CDI_rate'])**(1 / self.config.DIAS_UTEIS_ANO)
                cdi.drop(columns=['CDI'], inplace=True)
                logging.info("Dados do CDI obtidos com sucesso.")
                return cdi
            except Exception as e:
                last_error = e
                logging.warning(f"Tentativa {attempt + 1}/{self.retries} falhou ao buscar CDI: {e}")
                if attempt < self.retries - 1:
                    time.sleep(self.delay)
        logging.error("Todas as tentativas de buscar CDI falharam.")
        raise DataProviderError(
            "Falha ao buscar CDI após múltiplas tentativas",
            details={"retries": self.retries, "start_date": start_date, "end_date": end_date, "cause": str(last_error)}
        )
    def fetch_dividends(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        dividends_df = self.provider.fetch_dividends(assets, start_date, end_date)
        if not dividends_df.empty:
            if isinstance(dividends_df.index, pd.DatetimeIndex) and dividends_df.index.tz is not None:
                dividends_df.index = dividends_df.index.tz_localize(None)
            logging.info("Histórico de proventos obtido.")
            dividends_df.index.name = 'Date'
            return dividends_df.reset_index().set_index(['Date', 'Ativo'])
        else:
            logging.info("Nenhum provento encontrado para os ativos no período.")
            return pd.DataFrame()
    def fetch_exchange_rates(self, currencies: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        if not currencies: return pd.DataFrame()
        exchange_df = self.provider.fetch_exchange_rates(currencies, start_date, end_date)
        self.validator.validate_and_audit_timeseries(exchange_df, data_type="Câmbio")
        if exchange_df.empty:
            logging.warning("Nenhum dado de câmbio retornado.")
            raise DataProviderError(
                "Nenhum dado de câmbio retornado",
                details={"currencies": currencies, "start_date": start_date, "end_date": end_date}
            )
        all_business_days = pd.date_range(start=start_date, end=end_date, freq='B')
        exchange_df = exchange_df.reindex(all_business_days)
        exchange_df.ffill(inplace=True)
        exchange_df.bfill(inplace=True)
        for currency in currencies:
            if currency not in exchange_df.columns: exchange_df[currency] = np.nan
        logging.info("Dados de câmbio obtidos e preenchidos com sucesso.")
        return exchange_df
    def fetch_benchmark_data(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.Series]:
        benchmark_series = self.provider.fetch_benchmark_data(ticker, start_date, end_date)
        if benchmark_series is None:
            logging.warning(f"Não foi possível baixar dados do benchmark '{ticker}'.")
            raise DataProviderError(
                "Falha ao obter dados do benchmark",
                details={"ticker": ticker, "start_date": start_date, "end_date": end_date}
            )
        logging.info(f"Dados do benchmark '{ticker}' obtidos.")
        return benchmark_series

    # ===== Fama-French & Risk-free helpers =====
    def fetch_ff3_us_monthly(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Baixa fatores Fama-French 3 (EUA) mensais via pandas-datareader.

        Retorna DataFrame com colunas: 'MKT_RF', 'SMB', 'HML', 'RF' (em decimais).
        """
        try:
            ff = pdr.DataReader('F-F_Research_Data_Factors', 'famafrench', start=start_date, end=end_date)
            df = ff[0].copy()  # monthly factors
            # Converter de percent para decimais
            for c in df.columns:
                df[c] = df[c] / 100.0
            # Converter index para fim do mês
            if not isinstance(df.index, pd.DatetimeIndex):
                idx = [pd.Timestamp(year=int(i[0]), month=int(i[1]), day=1) for i in df.index]
                df.index = pd.DatetimeIndex(idx)
            df.index = df.index.to_period('M').to_timestamp('M')
            df = df.rename(columns={'Mkt-RF': 'MKT_RF'})[['MKT_RF', 'SMB', 'HML', 'RF']]
            df = df.loc[(df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))]
            return df
        except Exception as e:
            logging.error(f"Falha ao baixar fatores Fama-French: {e}")
            raise DataProviderError("Falha ao baixar fatores Fama-French", details={"cause": str(e)})

    def fetch_ff5_us_monthly(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Baixa fatores Fama-French 5 (EUA) mensais via pandas-datareader.

        Retorna DataFrame com colunas: 'MKT_RF','SMB','HML','RMW','CMA','RF' (em decimais).
        """
        try:
            ff = pdr.DataReader('F-F_Research_Data_5_Factors_2x3', 'famafrench', start=start_date, end=end_date)
            df = ff[0].copy()
            for c in df.columns:
                df[c] = df[c] / 100.0
            if not isinstance(df.index, pd.DatetimeIndex):
                idx = [pd.Timestamp(year=int(i[0]), month=int(i[1]), day=1) for i in df.index]
                df.index = pd.DatetimeIndex(idx)
            df.index = df.index.to_period('M').to_timestamp('M')
            df = df.rename(columns={'Mkt-RF': 'MKT_RF'})[['MKT_RF', 'SMB', 'HML', 'RMW', 'CMA', 'RF']]
            df = df.loc[(df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))]
            return df
        except Exception as e:
            logging.error(f"Falha ao baixar fatores Fama-French 5: {e}")
            raise DataProviderError("Falha ao baixar fatores Fama-French 5", details={"cause": str(e)})

    def fetch_us10y_monthly_yield(self, start_date: str, end_date: str) -> pd.Series:
        """Baixa a taxa do Treasury 10Y (FRED: DGS10) e agrega para mensal (média). Retorna em percentual anual."""
        try:
            s = pdr.DataReader('DGS10', 'fred', start=start_date, end=end_date)
            s = s['DGS10'].astype(float)
            monthly = s.resample('M').mean()
            monthly.name = 'US10Y'
            return monthly
        except Exception as e:
            logging.error(f"Falha ao baixar US10Y (FRED DGS10): {e}")
            raise DataProviderError("Falha ao baixar US10Y (FRED)", details={"cause": str(e)})

    def compute_monthly_rf_from_cdi(self, start_date: str, end_date: str) -> pd.Series:
        """Aproxima RF mensal a partir do CDI diário (usando fator_diario). Retorna série mensal em decimal."""
        cdi = self.fetch_cdi(start_date, end_date)
        if 'fator_diario' not in cdi.columns:
            raise DataProviderError("CDI sem coluna fator_diario para composição mensal")
        # Compor por mês: produto dos fatores - 1
        monthly = cdi['fator_diario'].resample('M').apply(lambda x: float(x.prod()) - 1.0)
        monthly.name = 'RF'
        return monthly
