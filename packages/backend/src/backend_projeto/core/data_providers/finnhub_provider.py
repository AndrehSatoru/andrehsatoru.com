import pandas as pd
import logging
import requests
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from backend_projeto.utils.cache import CacheManager
from backend_projeto.utils.config import Settings
from backend_projeto.core.exceptions import DataProviderError

class DataProvider(ABC):
    @abstractmethod
    def fetch_asset_info(self, assets: List[str]) -> Dict[str, Dict[str, str]]: pass
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

class FinnhubProvider(DataProvider):
    """Provider para dados do Finnhub como backup do YFinance."""
    
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
        """Busca preços históricos via Finnhub."""
        all_data = []
        start_unix = int(pd.to_datetime(start_date).timestamp())
        end_unix = int(pd.to_datetime(end_date).timestamp())

        for asset in assets:
            cache_key = f"finnhub_prices_{asset}_{start_date}_{end_date}"
            cached_df = self.cache.get_dataframe(cache_key)
            if cached_df is not None:
                all_data.append(cached_df)
                continue

            try:
                params = {
                    'symbol': asset,
                    'resolution': 'D', # Diário
                    'from': start_unix,
                    'to': end_unix
                }
                data = self._make_request('stock/candle', params)
                if data.get('s') == 'ok':
                    df = pd.DataFrame(data)
                    df['t'] = pd.to_datetime(df['t'], unit='s')
                    df = df.rename(columns={'c': asset, 't': 'Date'}).set_index('Date')
                    df = df[[asset]]
                    self.cache.set_dataframe(df, cache_key)
                    all_data.append(df)
                else:
                    logging.warning(f"[Finnhub] Nenhum dado de preço para {asset}")
            except DataProviderError as e:
                logging.error(f"[Finnhub] Falha ao buscar preços para {asset}: {e}")

        if not all_data:
            return pd.DataFrame()
        return pd.concat(all_data, axis=1)

    def fetch_asset_info(self, assets: List[str]) -> Dict[str, Dict[str, str]]:
        """Busca informações básicas (perfil) do ativo."""
        asset_info = {}
        for asset in assets:
            try:
                params = {'symbol': asset}
                profile = self._make_request('stock/profile2', params)
                if profile:
                    asset_info[asset] = {
                        'currency': profile.get('currency', 'USD'),
                        'sector': profile.get('finnhubIndustry', 'N/A')
                    }
                else:
                    asset_info[asset] = {'currency': 'USD', 'sector': 'N/A'}
            except DataProviderError:
                asset_info[asset] = {'currency': 'USD', 'sector': 'N/A'}
        return asset_info

    def fetch_dividends(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        """Busca dividendos via Finnhub."""
        all_dividends = []
        for asset in assets:
            try:
                params = {
                    'symbol': asset,
                    'from': start_date,
                    'to': end_date
                }
                dividends = self._make_request('stock/dividend', params)
                if dividends:
                    df = pd.DataFrame(dividends)
                    df = df.rename(columns={'amount': 'ValorPorAcao', 'payDate': 'Date'})
                    df['Ativo'] = asset
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.set_index('Date')
                    all_dividends.append(df)
            except DataProviderError as e:
                logging.error(f"[Finnhub] Falha ao buscar dividendos para {asset}: {e}")

        if not all_dividends:
            return pd.DataFrame()
        return pd.concat(all_dividends)

    def fetch_market_caps(self, assets: List[str]) -> Dict[str, float]:
        """Busca market cap via Finnhub (usando stock/profile2)."""
        market_caps = {}
        for asset in assets:
            try:
                params = {'symbol': asset}
                profile = self._make_request('stock/profile2', params)
                # Market cap vem em milhões, então multiplicamos
                market_caps[asset] = float(profile.get('marketCapitalization', 0.0)) * 1_000_000
            except (DataProviderError, ValueError):
                market_caps[asset] = 0.0
        return market_caps

    def fetch_benchmark_data(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.Series]:
        """Busca dados de benchmark (índices) via Finnhub."""
        df = self.fetch_stock_prices([ticker], start_date, end_date)
        if not df.empty and ticker in df.columns:
            return df[ticker]
        return None

    def fetch_exchange_rates(self, currencies: List[str], start_date: str, end_date: str) -> pd.DataFrame:
        raise NotImplementedError("FinnhubProvider.fetch_exchange_rates is not implemented")
