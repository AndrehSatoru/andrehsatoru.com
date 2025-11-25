"""
This module provides an abstraction layer for fetching financial data from various sources.

It defines a `DataProvider` abstract base class and concrete implementations
like `YFinanceProvider`, `FinnhubProvider`, and `AlphaVantageProvider`.
These providers handle fetching stock prices, dividends, exchange rates,
benchmark data, market caps, and Fama-French factors, incorporating caching,
retry mechanisms, and fallback strategies.
"""
# core/data_handling.py
# Classes DataProvider, YFinanceProvider, DataCleaner, DataValidator

import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from bcb import sgs
from backend_projeto.infrastructure.utils.retry import retry_with_backoff
import numpy as np
import time
import logging
import requests
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from abc import ABC, abstractmethod
from backend_projeto.infrastructure.utils.cache import CacheManager
from backend_projeto.infrastructure.utils.config import Settings, settings
from backend_projeto.domain.exceptions import (
    DataProviderError,
    InvalidTransactionFileError,
    DataValidationError,
)
import concurrent.futures
import functools
import pandas as pd
from backend_projeto.domain.trading_calendar import trading_calendar

from backend_projeto.infrastructure.utils.cache_cleaner import CacheCleaner

__all__ = ["DataProvider", "YFinanceProvider", "FinnhubProvider", "AlphaVantageProvider"]


def normalize_ticker_for_yahoo(ticker: str) -> str:
    """
    Normalize a ticker symbol for Yahoo Finance.
    
    Brazilian stocks need the .SA suffix to be recognized.
    If the ticker already has .SA or another suffix (contains a dot), leave it unchanged.
    
    Args:
        ticker: The ticker symbol (e.g., 'PETR4', 'VALE3', 'AAPL')
    
    Returns:
        The normalized ticker (e.g., 'PETR4.SA', 'VALE3.SA', 'AAPL')
    """
    if not ticker:
        return ticker
    
    # If it already has a suffix, leave it unchanged
    if '.' in ticker:
        return ticker
    
    # Brazilian ticker pattern: 4 letters + number(s) (e.g., PETR4, VALE3, ITUB4)
    # Some also have F at the end (e.g., PETR4F for fractional)
    import re
    brazilian_pattern = re.compile(r'^[A-Z]{4}\d{1,2}[FBW]?$', re.IGNORECASE)
    
    if brazilian_pattern.match(ticker.upper()):
        return f"{ticker.upper()}.SA"
    
    return ticker


def denormalize_ticker(ticker: str) -> str:
    """
    Remove the Yahoo Finance suffix from a ticker.
    
    Args:
        ticker: The ticker with suffix (e.g., 'PETR4.SA')
    
    Returns:
        The ticker without suffix (e.g., 'PETR4')
    """
    if ticker and '.SA' in ticker.upper():
        return ticker.replace('.SA', '').replace('.sa', '')
    return ticker


class DataProvider(ABC):
    """
    Abstract Base Class for all data providers.

    Defines the interface for fetching various types of financial data,
    ensuring consistency across different data sources.
    """
    _price_cache: Dict[str, pd.DataFrame] = {} # Shared cache for all DataProvider instances
    _cache_cleaner: Optional[CacheCleaner] = None # Cache cleaner instance

    def __init__(self):
        if DataProvider._cache_cleaner is None:
            DataProvider._cache_cleaner = CacheCleaner(DataProvider._price_cache)

    @abstractmethod
    def fetch_asset_info(self, assets: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Fetches basic information for a list of assets.

        Args:
            assets (List[str]): A list of asset tickers.

        Returns:
            Dict[str, Dict[str, str]]: A dictionary where keys are asset tickers
                                       and values are dictionaries containing asset information
                                       (e.g., currency, sector).
        """
        pass
    @abstractmethod
    def _get_cache_key(self, assets: List[str], start_date: str, end_date: str) -> str:
        """
        Generates a cache key for the given parameters.

        Args:
            assets (List[str]): A list of asset tickers.
            start_date (str): The start date for the data.
            end_date (str): The end date for the data.

        Returns:
            str: A unique string representing the cache key.
        """
        pass

    def _fetch_prices_direct_api(self, normalized_assets: List[str], start: pd.Timestamp, end: pd.Timestamp, 
                                  original_assets: List[str], ticker_map: Dict[str, str]) -> Optional[pd.DataFrame]:
        """
        Fetch prices directly from Yahoo Finance API with proper headers.
        This is more reliable than yfinance when dealing with rate limiting.
        """
        import time as time_module
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        all_data = {}
        
        for i, (norm_ticker, orig_ticker) in enumerate(zip(normalized_assets, original_assets)):
            try:
                # Add small delay between requests to avoid rate limiting
                if i > 0:
                    time_module.sleep(0.5)
                
                # Convert dates to Unix timestamps
                start_ts = int(start.timestamp())
                end_ts = int(end.timestamp())
                
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{norm_ticker}"
                params = {
                    'period1': start_ts,
                    'period2': end_ts,
                    'interval': '1d',
                    'includePrePost': 'false',
                    'events': 'div,splits'
                }
                
                logging.info(f"Fetching {norm_ticker} from Yahoo Finance API...")
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code == 429:
                    logging.warning(f"Rate limited by Yahoo Finance, waiting 5 seconds...")
                    time_module.sleep(5)
                    response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code != 200:
                    logging.error(f"Yahoo Finance API returned {response.status_code} for {norm_ticker}")
                    continue
                
                data = response.json()
                
                if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
                    logging.error(f"No data in Yahoo Finance response for {norm_ticker}")
                    continue
                
                result = data['chart']['result'][0]
                timestamps = result.get('timestamp', [])
                
                if not timestamps:
                    logging.warning(f"No timestamps in Yahoo Finance response for {norm_ticker}")
                    continue
                
                indicators = result.get('indicators', {}).get('quote', [{}])[0]
                closes = indicators.get('close', [])
                
                if not closes:
                    logging.warning(f"No close prices in Yahoo Finance response for {norm_ticker}")
                    continue
                
                # Create series with dates as index - normalize to date only (no time)
                dates = pd.to_datetime(timestamps, unit='s').tz_localize('UTC').tz_convert('America/Sao_Paulo').tz_localize(None)
                # Normalize to just date (remove time component) for proper alignment
                dates = dates.normalize()
                series = pd.Series(closes, index=dates, name=orig_ticker)
                series = series.dropna()
                # Remove duplicates (keep first) in case of multiple entries per day
                series = series[~series.index.duplicated(keep='first')]
                
                if not series.empty:
                    all_data[orig_ticker] = series
                    logging.info(f"Successfully fetched {len(series)} data points for {orig_ticker}")
                
            except Exception as e:
                logging.error(f"Error fetching {norm_ticker} from direct API: {str(e)}")
                continue
        
        if not all_data:
            return None
        
        df = pd.DataFrame(all_data)
        df.index = pd.to_datetime(df.index)
        return df

    @retry_with_backoff(max_retries=3, backoff_factor=2.0)
    def fetch_stock_prices(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches stock prices for given assets and date range with caching.

        This is a default implementation that can be overridden by concrete providers.
        It includes caching logic.

        Args:
            assets (List[str]): A list of asset tickers.
            start_date (str): The start date for fetching prices (YYYY-MM-DD).
            end_date (str): The end date for fetching prices (YYYY-MM-DD).

        Returns:
            pd.DataFrame: A DataFrame containing the adjusted closing prices of the assets.
        """
        cache_key = self._get_cache_key(assets, start_date, end_date)
        
        # Check cache first
        if self.cache.enabled and cache_key in self._price_cache:
            logging.info("Returning cached price data")
            return self._price_cache[cache_key]
        
        logging.info(f"Fetching prices for {assets} from {start_date} to {end_date}")
        try:
            # Normalize tickers for Yahoo Finance (add .SA for Brazilian stocks)
            original_assets = assets.copy() if isinstance(assets, list) else list(assets)
            normalized_assets = [normalize_ticker_for_yahoo(a) for a in original_assets]
            ticker_map = dict(zip(normalized_assets, original_assets))  # To restore original names
            
            logging.info(f"Normalized tickers: {normalized_assets}")
            
            # Add extra days to handle weekends/holidays
            start = pd.to_datetime(start_date) - pd.Timedelta(days=7)
            end = pd.to_datetime(end_date) + pd.Timedelta(days=7)
            
            # Try direct API call first (more reliable)
            data = self._fetch_prices_direct_api(normalized_assets, start, end, original_assets, ticker_map)
            
            # If direct API fails, try yfinance as fallback
            if data is None or data.empty:
                logging.info("Direct API failed, trying yfinance...")
                if len(normalized_assets) == 1:
                    ticker = yf.Ticker(normalized_assets[0])
                    data = ticker.history(start=start, end=end)
                    if not data.empty and 'Close' in data.columns:
                        # Use original asset name for column
                        data = data['Close'].to_frame(name=original_assets[0])
                    else:
                        data = pd.DataFrame()
                else:
                    data = yf.download(normalized_assets, start=start, end=end, progress=False)
                    if not data.empty:
                        if isinstance(data.columns, pd.MultiIndex):
                            data = data['Close']
                    else:
                        data = data[['Close']] if 'Close' in data.columns else data
                    # Rename columns back to original asset names
                    if hasattr(data, 'columns'):
                        data.columns = [ticker_map.get(c, c) for c in data.columns]
            
            if data is None or data.empty:
                logging.error(f"No data returned from Yahoo Finance for {assets}")
                raise DataProviderError(f"No data available for {assets} between {start_date} and {end_date}")
            
            # Filter to requested date range
            data = data.loc[start_date:end_date]
            
            if data.empty:
                logging.warning(f"No data in exact date range {start_date} to {end_date}, returning available data")
            
            # Cache the result
            if self.cache.enabled:
                self._price_cache[cache_key] = data
                
            return data
        except Exception as e:
            logging.error(f"Error fetching stock prices: {str(e)}")
            raise

    def fetch_dividends(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches dividend history for a list of assets via Yahoo Finance API directly.

        Args:
            assets (List[str]): A list of asset tickers.
            start_date (str): The start date for fetching dividends (YYYY-MM-DD).
            end_date (str): The end date for fetching dividends (YYYY-MM-DD).

        Returns:
            pd.DataFrame: A DataFrame containing dividend information for all assets.
                          Columns typically include 'ValorPorAcao' and 'Ativo'.
        """
        all_dividends = []
        # Normalize tickers for Yahoo Finance
        normalized_assets = [normalize_ticker_for_yahoo(a) for a in assets]
        
        # Convert dates to timestamps
        start_ts = int(pd.Timestamp(start_date).timestamp())
        end_ts = int(pd.Timestamp(end_date).timestamp())
        
        def fetch_single_dividend(norm_asset: str, orig_asset: str) -> pd.DataFrame:
            """Fetch dividends for a single asset directly from Yahoo Finance API."""
            try:
                url = f'https://query2.finance.yahoo.com/v8/finance/chart/{norm_asset}'
                params = {
                    'period1': start_ts,
                    'period2': end_ts,
                    'interval': '1d',
                    'events': 'div'
                }
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                
                resp = requests.get(url, params=params, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                
                result = data.get('chart', {}).get('result', [])
                if not result:
                    return pd.DataFrame()
                    
                events = result[0].get('events', {})
                dividends = events.get('dividends', {})
                
                if not dividends:
                    return pd.DataFrame()
                
                # Convert to DataFrame
                records = []
                for ts, div_data in dividends.items():
                    date = pd.Timestamp(int(ts), unit='s')
                    records.append({
                        'Date': date,
                        'ValorPorAcao': div_data.get('amount', 0),
                        'Ativo': orig_asset
                    })
                
                if not records:
                    return pd.DataFrame()
                    
                df = pd.DataFrame(records)
                df['Date'] = pd.to_datetime(df['Date']).dt.normalize()
                df = df.set_index('Date').sort_index()
                logging.info(f"Dividends for {orig_asset}: {len(df)} records")
                return df
                
            except Exception as e:
                logging.warning(f"Error fetching dividends for {orig_asset}: {e}")
                return pd.DataFrame()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(fetch_single_dividend, norm_asset, orig_asset): orig_asset 
                for norm_asset, orig_asset in zip(normalized_assets, assets)
            }
            
            for future in concurrent.futures.as_completed(futures):
                orig_asset = futures[future]
                try:
                    result_df = future.result()
                    if not result_df.empty:
                        all_dividends.append(result_df)
                except Exception as e:
                    logging.warning(f"Could not fetch dividends for {orig_asset}: {e}")
                    
        if not all_dividends:
            return pd.DataFrame(columns=['ValorPorAcao', 'Ativo'])
        return pd.concat(all_dividends)

    def fetch_exchange_rates(self, currencies: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches exchange rates via YFinance.

        Note: This implementation is a placeholder and currently returns an empty DataFrame.
        YFinance does have forex data, but a robust implementation would be more complex.

        Args:
            currencies (List[str]): A list of currency pairs (e.g., ["USDBRL=X"]).
            start_date (str): The start date for fetching rates (YYYY-MM-DD).
            end_date (str): The end date for fetching rates (YYYY-MM-DD).

        Returns:
            pd.DataFrame: An empty DataFrame, as the functionality is not fully implemented.
        """
        # YFinance can fetch forex data, e.g., "USDBRL=X"
        # This is a basic implementation. A more robust one would handle
        # different currency pairs and potential errors more gracefully.
        try:
            data = pdr.get_data_yahoo(currencies, start=start_date, end=end_date, timeout=self.timeout)
            if isinstance(data.index, pd.MultiIndex):
                data = data['Adj Close']
            return data
        except Exception as e:
            logging.error(f"Error fetching exchange rates for {currencies}: {e}")
            return pd.DataFrame()

    def fetch_benchmark_data(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.Series]:
        """
        Fetches historical data for a given benchmark ticker via YFinance.

        Args:
            ticker (str): The ticker symbol of the benchmark (e.g., "^BVSP", "^GSPC").
            start_date (str): The start date for fetching data (YYYY-MM-DD).
            end_date (str): The end date for fetching data (YYYY-MM-DD).

        Returns:
            Optional[pd.Series]: A Series containing the benchmark's historical data,
                                 or None if the data is empty or the ticker is not found.
        """
        try:
            data = pdr.get_data_yahoo(ticker, start=start_date, end=end_date, timeout=self.timeout)
            if not data.empty and 'Adj Close' in data.columns:
                return data['Adj Close']
            elif not data.empty and ticker in data.columns: # For single series like USDBRL=X
                return data[ticker]
            return None
        except Exception as e:
            logging.warning(f"Could not fetch benchmark data for {ticker} from YFinance: {e}")
            return None

    def fetch_market_caps(self, assets: List[str]) -> Dict[str, float]:
        """
        Fetches market capitalization for a list of assets via YFinance.

        Args:
            assets (List[str]): A list of asset tickers.

        Returns:
            Dict[str, float]: A dictionary where keys are asset tickers and values are their market caps.
                              Returns 0.0 for assets where market cap could not be fetched.
        """
        market_caps = {}
        for asset in assets:
            try:
                # Normalize ticker for Yahoo Finance
                normalized = normalize_ticker_for_yahoo(asset)
                ticker = yf.Ticker(normalized)
                data = ticker.info
                market_caps[asset] = float(data.get('marketCap', 0.0))  # Use original asset name
            except Exception as e:
                logging.warning(f"Could not fetch market cap for {asset} from YFinance: {e}")
                market_caps[asset] = 0.0
        return market_caps

class YFinanceProvider(DataProvider):
    """Provider for YFinance data with retry, circuit breaker, and flexible fallbacks."""
    
    _price_cache = {}
    _cache_cleaner = CacheCleaner(_price_cache)

    def __init__(self):
        """Initialize YFinanceProvider with default configuration."""
        super().__init__()
        self.cache = CacheManager(enabled=settings.ENABLE_CACHE)
        self.timeout = settings.DATA_PROVIDER_TIMEOUT

    def _get_cache_key(self, assets: List[str], start_date: str, end_date: str) -> str:
        """
        Generates a cache key specific to YFinanceProvider for the given parameters.

        Args:
            assets (List[str]): A list of asset tickers.
            start_date (str): The start date for the data.
            end_date (str): The end date for the data.

        Returns:
            str: A unique string representing the cache key for YFinance data.
        """
        return f"yfinance_prices_{'_'.join(sorted(assets))}_{start_date}_{end_date}"

    def fetch_asset_info(self, assets: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Fetches basic information for a list of assets via YFinance.

        Args:
            assets (List[str]): A list of asset tickers.

        Returns:
            Dict[str, Dict[str, str]]: A dictionary where keys are asset tickers
                                       and values are dictionaries containing asset information
                                       (e.g., currency, sector).
        """
        info = {}
        for asset in assets:
            try:
                ticker = yf.Ticker(asset)
                data = ticker.info
                info[asset] = {
                    'currency': data.get('currency', 'USD'),
                    'sector': data.get('sector', 'N/A'),
                    'longName': data.get('longName', asset)
                }
            except Exception as e:
                logging.warning(f"Could not fetch info for {asset} from YFinance: {e}")
                info[asset] = {'currency': 'USD', 'sector': 'N/A', 'longName': asset}
        return info

    def fetch_cdi_daily(self, start_date: str, end_date: str) -> pd.Series:
        """
        Fetches daily CDI (Certificado de Depósito Interbancário) rates from BCB (Banco Central do Brasil).
        
        Args:
            start_date (str): The start date for fetching CDI rates (YYYY-MM-DD).
            end_date (str): The end date for fetching CDI rates (YYYY-MM-DD).
            
        Returns:
            pd.Series: A Series containing daily CDI rates in decimal format (e.g., 0.00017 for 0.017%).
                       Index is DatetimeIndex (only business days with actual CDI data).
                       
        Raises:
            DataProviderError: If there's an error fetching data from BCB.
        """
        try:
            # CDI diário é a série 12 do SGS do BCB
            # A série 12 retorna a taxa DIÁRIA já em percentual (ex: 0.017% ao dia)
            # CDI só rende em dias úteis, não fazer forward fill para fins de semana
            cdi_data = sgs.get({'CDI': 12}, start=start_date, end=end_date)
            
            if cdi_data.empty:
                logging.warning(f"Nenhum dado CDI encontrado para o período {start_date} a {end_date}")
                # Retornar série vazia
                return pd.Series(dtype=float, name='CDI')
            
            # Converter de percentual para decimal (0.017% -> 0.00017)
            # Manter apenas os dias que têm dados reais (dias úteis)
            cdi_diario = cdi_data['CDI'] / 100.0
            cdi_diario.name = 'CDI'
            
            return cdi_diario
            
        except Exception as e:
            logging.error(f"Erro ao buscar dados do CDI: {e}")
            # Em caso de erro, retornar série vazia
            return pd.Series(dtype=float, name='CDI')
    
    def compute_monthly_rf_from_cdi(self, start_date: str, end_date: str) -> pd.Series:
        """
        Computes monthly risk-free rate from daily CDI data.
        
        Args:
            start_date (str): The start date (YYYY-MM-DD).
            end_date (str): The end date (YYYY-MM-DD).
            
        Returns:
            pd.Series: Monthly risk-free rate in decimal format, indexed by month-end dates.
                       
        Raises:
            DataProviderError: If there's an error computing the monthly rate.
        """
        try:
            # Buscar CDI diário
            cdi_daily = self.fetch_cdi_daily(start_date, end_date)
            
            if cdi_daily.empty:
                logging.warning("CDI diário vazio, retornando taxa mensal zero")
                dates = pd.date_range(start=start_date, end=end_date, freq='M')
                return pd.Series(0.0, index=dates, name='RF')
            
            # Converter para DataFrame para facilitar o resample
            cdi_df = pd.DataFrame({'CDI': cdi_daily})
            
            # Calcular retorno composto mensal: produto de (1 + r_diário) - 1
            # Resample para mensal e aplicar a fórmula de composição
            monthly_rf = cdi_df.resample('M').apply(lambda x: (1 + x).prod() - 1)['CDI']
            monthly_rf.name = 'RF'
            
            return monthly_rf
            
        except Exception as e:
            logging.error(f"Erro ao calcular taxa mensal do CDI: {e}")
            raise DataProviderError(f"Erro ao calcular taxa mensal do CDI: {e}")

    def fetch_ff3_us_monthly(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches Fama-French 3-Factor (US, monthly) data.

        Args:
            start_date (str): The start date for fetching factors (YYYY-MM-DD).
            end_date (str): The end date for fetching factors (YYYY-MM-DD).

        Returns:
            pd.DataFrame: A DataFrame containing the Fama-French 3 factors (MKT_RF, SMB, HML).
                          Factors are converted from percentage to decimal.

        Raises:
            DataProviderError: If there's an error fetching data from the Fama-French library.
        """
        try:
            # Fama-French factors are typically fetched from a specific source, e.g., Kenneth French's data library
            # For simplicity, let's assume a placeholder or a direct download if available.
            # In a real scenario, you'd use a library like `ffn` or `pandas_datareader` with a specific source.
            # For now, let's create a dummy dataframe
            dates = pd.date_range(start=start_date, end=end_date, freq='M')
            data = pd.DataFrame(np.random.rand(len(dates), 3) * 0.01, index=dates, columns=['MKT_RF', 'SMB', 'HML'])
            data['RF'] = np.random.rand(len(dates)) * 0.001 # Dummy risk-free rate
            return data
        except Exception as e:
            raise DataProviderError(f"Error fetching Fama-French 3 factors: {e}")


class FinnhubProvider(DataProvider):
    """
    Data provider for Finnhub API.

    This provider fetches financial data such as stock prices, asset information,
    dividends, and market caps from the Finnhub API. It includes retry mechanisms,
    circuit breaker patterns, and caching.
    """
    
    def __init__(self, config: Settings):
        """Initialize Finnhub provider with secure configuration.
        
        Args:
            config: Config instance with API keys and settings
            
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        if not config.FINNHUB_API_KEY:
            raise ValueError("FINNHUB_API_KEY is required for FinnhubProvider")
            
        self.api_key = config.FINNHUB_API_KEY
        self.cache = CacheManager(enabled=config.ENABLE_CACHE)
        self.max_retries = config.DATA_PROVIDER_MAX_RETRIES
        self.backoff_factor = config.DATA_PROVIDER_BACKOFF_FACTOR
        self.timeout = config.DATA_PROVIDER_TIMEOUT
        self.consecutive_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_open = False
        
        # Validate configuration
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.backoff_factor <= 0:
            raise ValueError("backoff_factor must be > 0")
        if self.timeout <= 0:
            raise ValueError("timeout must be > 0")

    def _make_request(self, endpoint: str, params: Dict):
        """Make a secure request to the Finnhub API.
        
        Args:
            endpoint: API endpoint (e.g., 'quote')
            params: Dictionary of request parameters
            
        Returns:
            JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If the response is not valid JSON or contains an error
        """
        # Input validation
        if not endpoint or not isinstance(endpoint, str):
            raise ValueError("endpoint must be a non-empty string")
            
        if not isinstance(params, dict):
            raise ValueError("params must be a dictionary")
            
        # Sanitize endpoint to prevent path traversal
        endpoint = endpoint.strip().lstrip('/')
        if not endpoint.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Invalid endpoint format")
        
        params['token'] = self.api_key
        url = f"https://finnhub.io/api/v1/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()  # Lança exceção para status HTTP 4xx/5xx
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"[Finnhub] Erro na requisição para {endpoint}: {e}")
            raise DataProviderError(f"Erro na API do Finnhub: {e}") from e

    def fetch_stock_prices(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches historical stock prices for given assets from Finnhub.

        Args:
            assets (List[str]): A list of asset tickers.
            start_date (str): The start date for fetching prices (YYYY-MM-DD).
            end_date (str): The end date for fetching prices (YYYY-MM-DD).

        Returns:
            pd.DataFrame: A DataFrame containing the closing prices of the assets.
        """

    def fetch_asset_info(self, assets: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Fetches basic information (e.g., currency, sector) for a list of assets from Finnhub.

        Args:
            assets (List[str]): A list of asset tickers.

        Returns:
            Dict[str, Dict[str, str]]: A dictionary where keys are asset tickers
                                       and values are dictionaries containing asset information.
        """

    def fetch_dividends(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches dividend data for a list of assets from Finnhub.

        Args:
            assets (List[str]): A list of asset tickers.
            start_date (str): The start date for fetching dividends (YYYY-MM-DD).
            end_date (str): The end date for fetching dividends (YYYY-MM-DD).

        Returns:
            pd.DataFrame: A DataFrame containing dividend information for all assets.
                          Columns typically include 'ValorPorAcao' and 'Ativo'.
        """

    def fetch_market_caps(self, assets: List[str]) -> Dict[str, float]:
        """
        Fetches market capitalization for a list of assets from Finnhub.

        Args:
            assets (List[str]): A list of asset tickers.

        Returns:
            Dict[str, float]: A dictionary where keys are asset tickers and values are their market caps.
                              Returns 0.0 for assets where market cap could not be fetched.
        """

    def fetch_benchmark_data(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.Series]:
        """
        Fetches historical data for a given benchmark ticker from Finnhub.

        Args:
            ticker (str): The ticker symbol of the benchmark.
            start_date (str): The start date for fetching data (YYYY-MM-DD).
            end_date (str): The end date for fetching data (YYYY-MM-DD).

        Returns:
            Optional[pd.Series]: A Series containing the benchmark's historical data, or None if not found.
        """

    def fetch_exchange_rates(self, currencies: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches exchange rates for a list of currency pairs from Finnhub.

        Note: This method is currently not implemented and will raise a NotImplementedError.

        Args:
            currencies (List[str]): A list of currency pairs.
            start_date (str): The start date for fetching rates (YYYY-MM-DD).
            end_date (str): The end date for fetching rates (YYYY-MM-DD).

        Returns:
            pd.DataFrame: (Not implemented)

        Raises:
            NotImplementedError: This method is not yet implemented for FinnhubProvider.
        """

class AlphaVantageProvider(DataProvider):
    """
    Data provider for Alpha Vantage API.

    This provider fetches financial data such as stock prices, asset information,
    dividends, and market caps from the Alpha Vantage API. It includes retry mechanisms
    and handles Alpha Vantage's specific rate limits.
    """
    
    def __init__(self, config: Settings):
        """Initialize Alpha Vantage provider with secure configuration.
        
        Args:
            config: Config instance with API keys and settings
            
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        if not config.ALPHA_VANTAGE_API_KEY:
            raise ValueError("ALPHA_VANTAGE_API_KEY is required for AlphaVantageProvider")
            
        self.api_key = config.ALPHA_VANTAGE_API_KEY
        self.cache = CacheManager(enabled=config.ENABLE_CACHE)
        self.base_url = 'https://www.alphavantage.co/query'
        self.timeout = config.DATA_PROVIDER_TIMEOUT
        self.max_retries = config.DATA_PROVIDER_MAX_RETRIES
        self.backoff_factor = config.DATA_PROVIDER_BACKOFF_FACTOR
        
        # Validate configuration
        if not self.api_key or not isinstance(self.api_key, str):
            raise ValueError("API key must be a non-empty string")
        if self.timeout <= 0:
            raise ValueError("timeout must be > 0")
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")

    def _make_request(self, params: Dict):
        """Make a secure request to the Alpha Vantage API with retries and rate limiting.
        
        Args:
            params: Dictionary of request parameters
            
        Returns:
            JSON response from the API
            
        Raises:
            requests.exceptions.RequestException: If the request fails after all retries
            ValueError: If the response is not valid JSON or contains an error
            DataProviderError: If the API returns an error response
        """
        if not isinstance(params, dict):
            raise ValueError("params must be a dictionary")
            
        # Add API key to params
        params = params.copy()
        params['apikey'] = self.api_key
        
        last_exception = None
        
        # Implement retry logic with exponential backoff
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(
                    self.base_url, 
                    params=params,
                    timeout=self.timeout
                )
                
                # Check for rate limiting (Alpha Vantage returns 429 for rate limits)
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))  # Default to 60 seconds
                    logging.warning(f"Rate limited by Alpha Vantage. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                    
                response.raise_for_status()  # Raise HTTPError for bad responses
                
                data = response.json()
                
                # Log information message if present
                if 'Information' in data:
                    logging.info(f"[AlphaVantage] Info: {data['Information']}")
                
                # Check for API errors in the response
                if 'Error Message' in data:
                    error_msg = data.get('Error Message', 'Unknown error')
                    if 'API call frequency' in error_msg:
                        # Handle rate limiting from Alpha Vantage
                        wait_time = 60  # Default wait time
                        logging.warning(f"Alpha Vantage rate limit reached. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    raise DataProviderError(f"Alpha Vantage API error: {error_msg}")
                    
                # Check for note about API call frequency in the response
                if 'Note' in data and 'API call frequency' in data['Note']:
                    logging.warning("Approaching Alpha Vantage rate limit")
                    time.sleep(1)  # Add a small delay to prevent hitting the limit
                    
                return data
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = self.backoff_factor * (2 ** attempt)
                    logging.warning(
                        f"Request failed (attempt {attempt + 1}/{self.max_retries}). "
                        f"Retrying in {wait_time} seconds... Error: {e}"
                    )
                    time.sleep(wait_time)
                
        # If we've exhausted all retries
        raise DataProviderError(
            f"Failed to complete request after {self.max_retries} attempts. Last error: {last_exception}"
        ) from last_exception
        
    def fetch_stock_prices(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches historical stock prices for given assets from Alpha Vantage.

        Args:
            assets (List[str]): A list of asset tickers.
            start_date (str): The start date for fetching prices (YYYY-MM-DD).
            end_date (str): The end date for fetching prices (YYYY-MM-DD).

        Returns:
            pd.DataFrame: A DataFrame containing the adjusted closing prices of the assets.
        """





    def fetch_asset_info(self, assets: List[str]) -> Dict[str, Dict[str, str]]:
        """
        Fetches basic information (e.g., currency, sector) for a list of assets from Alpha Vantage.

        Args:
            assets (List[str]): A list of asset tickers.

        Returns:
            Dict[str, Dict[str, str]]: A dictionary where keys are asset tickers
                                       and values are dictionaries containing asset information.
        """





    def fetch_dividends(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches dividend data for a list of assets from Alpha Vantage.

        Args:
            assets (List[str]): A list of asset tickers.
            start_date (str): The start date for fetching dividends (YYYY-MM-DD).
            end_date (str): The end date for fetching dividends (YYYY-MM-DD).

        Returns:
            pd.DataFrame: A DataFrame containing dividend information for all assets.
                          Columns typically include 'ValorPorAcao' and 'Ativo'.
        """





    def fetch_market_caps(self, assets: List[str]) -> Dict[str, float]:
        """
        Fetches market capitalization for a list of assets from Alpha Vantage.

        Args:
            assets (List[str]): A list of asset tickers.

        Returns:
            Dict[str, float]: A dictionary where keys are asset tickers and values are their market caps.
                              Returns 0.0 for assets where market cap could not be fetched.
        """





    def fetch_benchmark_data(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.Series]:
        """
        Fetches historical data for a given benchmark ticker from Alpha Vantage.

        Args:
            ticker (str): The ticker symbol of the benchmark.
            start_date (str): The start date for fetching data (YYYY-MM-DD).
            end_date (str): The end date for fetching data (YYYY-MM-DD).

        Returns:
            Optional[pd.Series]: A Series containing the benchmark's historical data, or None if not found.
        """





    def fetch_exchange_rates(self, currencies: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches exchange rates for a list of currency pairs from Alpha Vantage.

        Note: This method is currently not implemented and will raise a NotImplementedError.

        Args:
            currencies (List[str]): A list of currency pairs.
            start_date (str): The start date for fetching rates (YYYY-MM-DD).
            end_date (str): The end date for fetching rates (YYYY-MM-DD).

        Returns:
            pd.DataFrame: (Not implemented)

        Raises:
            NotImplementedError: This method is not yet implemented for AlphaVantageProvider.
        """
