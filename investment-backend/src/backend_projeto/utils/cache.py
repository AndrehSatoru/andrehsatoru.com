import logging
import hashlib
import redis
import pickle
from pathlib import Path
from typing import List, Optional
import pandas as pd

class CacheManager:
    """Gerencia o armazenamento e a recuperação de dados em cache usando Redis."""
    def __init__(self, cache_dir: str = 'cache', redis_host: str = 'localhost', redis_port: int = 6379):
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)
            self.redis_client.ping()
            logging.info(f"CacheManager conectado ao Redis em {redis_host}:{redis_port}")
        except redis.exceptions.ConnectionError as e:
            logging.error(f"Não foi possível conectar ao Redis em {redis_host}:{redis_port}. O cache não funcionará. Erro: {e}")
            self.redis_client = None

    def _generate_key(self, prefix: str, assets: List[str], start_date: str, end_date: str) -> str:
        """Gera uma chave única e determinística para os parâmetros."""
        asset_str = "_".join(sorted(assets))
        if len(asset_str) > 100:
            asset_str = hashlib.md5(asset_str.encode()).hexdigest()
        return f"cache:{prefix}:{asset_str}:{start_date}:{end_date}"

    def get_dataframe(self, prefix: str, assets: List[str], start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Tenta carregar um DataFrame do cache Redis."""
        if not self.redis_client:
            return None
            
        key = self._generate_key(prefix, assets, start_date, end_date)
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                logging.info(f"[CACHE] HIT: Carregando '{key}' do Redis.")
                return pickle.loads(cached_data)
            return None
        except Exception as e:
            logging.warning(f"[CACHE] ERRO: Falha ao ler a chave '{key}' do Redis: {e}. Buscando dados frescos.")
            return None

    def set_dataframe(self, df: pd.DataFrame, prefix: str, assets: List[str], start_date: str, end_date: str, ttl_seconds: int = 86400):
        """Salva um DataFrame no cache Redis com um TTL (Time To Live)."""
        if df.empty or not self.redis_client:
            return
            
        key = self._generate_key(prefix, assets, start_date, end_date)
        try:
            serialized_df = pickle.dumps(df)
            self.redis_client.setex(key, ttl_seconds, serialized_df)
            logging.info(f"[CACHE] WRITE: Salvando '{key}' no Redis com TTL de {ttl_seconds} segundos.")
        except Exception as e:
            logging.error(f"[CACHE] ERRO: Falha ao salvar a chave '{key}' no Redis: {e}")
