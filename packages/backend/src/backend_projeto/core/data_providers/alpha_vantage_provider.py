import pandas as pd
import logging
import requests
import time
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

class AlphaVantageProvider(DataProvider):
    """Provider para dados do Alpha Vantage."""
    
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
        """Busca preços históricos via Alpha Vantage.
        
        Args:
            assets: Lista de códigos dos ativos
            start_date: Data inicial no formato 'YYYY-MM-DD'
            end_date: Data final no formato 'YYYY-MM-DD'
            
        Returns:
            DataFrame com os preços de fechamento ajustados
        """
        logging.info(f"[AlphaVantage] Buscando cotações para {len(assets)} ativos...")
        
        all_data = []
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)





        for asset in assets:


            cache_key = f"alphavantage_prices_{asset}_{start_date}_{end_date}"


            cached_df = self.cache.get_dataframe(cache_key)


            if cached_df is not None:


                all_data.append(cached_df)


                continue





            try:


                params = {


                    'function': 'TIME_SERIES_DAILY_ADJUSTED',


                    'symbol': asset,


                    'outputsize': 'full'


                }


                data = self._make_request(params)





                if 'Time Series (Daily)' in data:


                    ts_data = data['Time Series (Daily)']


                    df = pd.DataFrame.from_dict(ts_data, orient='index')


                    df.index = pd.to_datetime(df.index)


                    df = df[(df.index >= start_date_obj) & (df.index <= end_date_obj)]


                    df = df[['4. close']].rename(columns={'4. close': asset}).astype(float)


                    self.cache.set_dataframe(df, cache_key)


                    all_data.append(df)


                else:


                    logging.warning(f"[AlphaVantage] Nenhum dado de preço para {asset}")


                time.sleep(12) # Respeitar o rate limit da API gratuita (5 req/min)


            except DataProviderError as e:


                logging.error(f"[AlphaVantage] Erro ao buscar preços para {asset}: {e}")





        if not all_data:


            return pd.DataFrame()


        return pd.concat(all_data, axis=1)





    def fetch_asset_info(self, assets: List[str]) -> Dict[str, Dict[str, str]]:


        """Busca informações básicas via Alpha Vantage (OVERVIEW)."""


        asset_info = {}


        for asset in assets:


            try:


                params = {'function': 'OVERVIEW', 'symbol': asset}


                overview = self._make_request(params)


                if overview and 'Symbol' in overview:


                    asset_info[asset] = {


                        'currency': overview.get('Currency', 'USD'),


                        'sector': overview.get('Sector', 'N/A')


                    }


                else:


                    asset_info[asset] = {'currency': 'USD', 'sector': 'N/A'}


                time.sleep(12)


            except DataProviderError:


                asset_info[asset] = {'currency': 'USD', 'sector': 'N/A'}


        return asset_info


    def fetch_dividends(self, assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:


        """Busca dividendos via Alpha Vantage (usando TIME_SERIES_DAILY_ADJUSTED)."""


        all_dividends = []


        start_date_obj = pd.to_datetime(start_date)


        end_date_obj = pd.to_datetime(end_date)


        for asset in assets:


            try:


                params = {


                    'function': 'TIME_SERIES_DAILY_ADJUSTED',


                    'symbol': asset,


                    'outputsize': 'full'


                }


                data = self._make_request(params)


                if 'Time Series (Daily)' in data:


                    df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')


                    df.index = pd.to_datetime(df.index)


                    df = df[(df.index >= start_date_obj) & (df.index <= end_date_obj)]


                    div_df = df[df['7. dividend amount'].astype(float) > 0]


                    if not div_df.empty:


                        div_df = div_df[['7. dividend amount']].rename(columns={'7. dividend amount': 'ValorPorAcao', 'index': 'Date'})


                        div_df['Ativo'] = asset


                        all_dividends.append(div_df)


                time.sleep(12)


            except DataProviderError as e:


                logging.error(f"[AlphaVantage] Erro ao buscar dividendos para {asset}: {e}")


        if not all_dividends:


            return pd.DataFrame()


        return pd.concat(all_dividends)


    def fetch_market_caps(self, assets: List[str]) -> Dict[str, float]:


        """Busca market caps via Alpha Vantage (OVERVIEW)."""


        market_caps = {}


        for asset in assets:


            try:


                params = {'function': 'OVERVIEW', 'symbol': asset}


                overview = self._make_request(params)


                if overview and overview.get('MarketCapitalization') and overview['MarketCapitalization'] != 'None':


                    market_caps[asset] = float(overview['MarketCapitalization'])


                else:


                    market_caps[asset] = 0.0


                time.sleep(12)


            except (DataProviderError, ValueError):


                market_caps[asset] = 0.0


        return market_caps


    def fetch_benchmark_data(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.Series]:


        """Busca benchmark via Alpha Vantage."""


        df = self.fetch_stock_prices([ticker], start_date, end_date)


        if df.empty or ticker not in df.columns:


            return None


        return df[ticker]


    def fetch_exchange_rates(self, currencies: List[str], start_date: str, end_date: str) -> pd.DataFrame:


        raise NotImplementedError("AlphaVantageProvider.fetch_exchange_rates is not implemented")
