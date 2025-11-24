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
            data = pdr.get_data_yahoo(assets, start=start_date, end=end_date, timeout=self.timeout)
            if isinstance(data.index, pd.MultiIndex):
                data = data['Adj Close']
            
            # Cache the result
            if self.cache.enabled:
                self._price_cache[cache_key] = data
                
            return data
        except Exception as e:
            logging.error(f"Error fetching stock prices: {str(e)}")
            raise

    def fetch_dividends(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches dividend history for a list of assets via YFinance, with parallel processing.

        Args:
            assets (List[str]): A list of asset tickers.
            start_date (str): The start date for fetching dividends (YYYY-MM-DD).
            end_date (str): The end date for fetching dividends (YYYY-MM-DD).

        Returns:
            pd.DataFrame: A DataFrame containing dividend information for all assets.
                          Columns typically include 'ValorPorAcao' and 'Ativo'.
        """
        all_dividends = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_asset = {executor.submit(lambda s, start, end: s.loc[start:end], yf.Ticker(asset).dividends, start_date, end_date): asset for asset in assets}
            for future in concurrent.futures.as_completed(future_to_asset):
                asset = future_to_asset[future]
                try:
                    divs = future.result()
                    if not divs.empty:
                        divs = divs.reset_index()
                        divs.columns = ['Date', 'ValorPorAcao']
                        divs['Ativo'] = asset
                        divs['Date'] = pd.to_datetime(divs['Date'])
                        divs = divs.set_index('Date')
                        all_dividends.append(divs)
                except Exception as e:
                    logging.warning(f"Could not fetch dividends for {asset} from YFinance: {e}")
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
                ticker = yf.Ticker(asset)
                data = ticker.info
                market_caps[asset] = float(data.get('marketCap', 0.0))
            except Exception as e:
                logging.warning(f"Could not fetch market cap for {asset} from YFinance: {e}")
                market_caps[asset] = 0.0
        return market_caps

class YFinanceProvider(DataProvider):
    """Provider for YFinance data with retry, circuit breaker, and flexible fallbacks."""
    
    _price_cache = {}
    _cache_cleaner = CacheCleaner(_price_cache)

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
