import logging
import hashlib
import json
import redis
# pickle import removed for security
from datetime import timedelta
from typing import List, Optional, Any
import pandas as pd
from cachetools import TTLCache

class CacheManager:
    """
    Gerencia o armazenamento e a recuperação de dados em cache usando Redis 
    com fallback para memória (Hybrid Cache).
    """
    def __init__(self, enabled: bool = True, redis_host: str = 'localhost', redis_port: int = 6379):
        self.enabled = enabled
        self.redis_client = None
        # Cache em memória como fallback (LRU cache)
        # Maxsize 100 itens, TTL padrão 1 hora
        self.memory_cache = TTLCache(maxsize=100, ttl=3600)
        
        if not enabled:
            logging.info("Cache is disabled. CacheManager will not connect to Redis.")
            return

        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=0, 
                socket_connect_timeout=1,
                decode_responses=True # Alterado para True para suportar JSON/strings
            )
            self.redis_client.ping()
            logging.info(f"CacheManager connected to Redis at {redis_host}:{redis_port}")
        except redis.exceptions.ConnectionError as e:
            logging.warning(f"Could not connect to Redis at {redis_host}:{redis_port}. Using memory cache only. Error: {e}")
            self.redis_client = None

    def _generate_key(self, prefix: str, assets: List[str], start_date: str, end_date: str) -> str:
        """Gera uma chave única e determinística para os parâmetros."""
        asset_str = "_".join(sorted(assets))
        if len(asset_str) > 100:
            asset_str = hashlib.md5(asset_str.encode()).hexdigest()
        return f"cache:{prefix}:{asset_str}:{start_date}:{end_date}"

    def get_dataframe(self, prefix: str, assets: List[str], start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Tenta carregar um DataFrame do cache (Redis ou Memória)."""
        key = self._generate_key(prefix, assets, start_date, end_date)
        
        # 1. Tentar Redis
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    logging.info(f"[CACHE] HIT (Redis): Carregando '{key}'")
                    try:
                        # Tentar carregar como JSON (seguro)
                        data = json.loads(cached_data)
                        # Converter lista/dict de volta para DataFrame
                        # O formato esperado é 'split' do pandas: dict(index=[], columns=[], data=[])
                        return pd.DataFrame(data['data'], index=pd.to_datetime(data['index']), columns=data['columns'])
                    except (json.JSONDecodeError, KeyError, TypeError) as e:
                        logging.warning(f"[CACHE] Aviso: Falha ao decodificar JSON para '{key}': {e}")
                        # Dados antigos ou inválidos, ignorar
                        pass
            except Exception as e:
                logging.warning(f"[CACHE] ERRO (Redis): Falha ao ler '{key}': {e}")

        # 2. Tentar Memória (Fallback)
        if key in self.memory_cache:
            logging.info(f"[CACHE] HIT (Memory): Carregando '{key}'")
            return self.memory_cache[key]

        return None

    def set_dataframe(self, df: pd.DataFrame, prefix: str, assets: List[str], start_date: str, end_date: str, ttl_seconds: int = 86400):
        """Salva um DataFrame no cache (Redis e Memória)."""
        if df.empty:
            return
            
        key = self._generate_key(prefix, assets, start_date, end_date)
        
        # 1. Salvar em Memória
        try:
            self.memory_cache[key] = df.copy()
        except Exception as e:
            logging.warning(f"[CACHE] ERRO (Memory): Falha ao salvar '{key}': {e}")
        
        # 2. Salvar no Redis
        if self.redis_client:
            try:
                # Converter para JSON usando formato 'split' que preserva índice e colunas
                # default=str para converter datas/timestamps para string
                data = df.to_dict(orient='split')
                # Converter datas no índice para string ISO
                if isinstance(df.index, pd.DatetimeIndex):
                    data['index'] = [d.isoformat() for d in df.index]
                
                serialized = json.dumps(data, default=str)
                self.redis_client.setex(key, ttl_seconds, serialized)
                logging.info(f"[CACHE] WRITE (Redis): Salvando '{key}' com TTL {ttl_seconds}s")
            except Exception as e:
                logging.error(f"[CACHE] ERRO (Redis): Falha ao salvar '{key}': {e}")

    def get(self, key: str) -> Any:
        """Obtém um valor genérico do cache."""
        # Redis
        if self.redis_client:
            try:
                val = self.redis_client.get(key)
                if val:
                    try:
                        return json.loads(val)
                    except:
                        return val
            except Exception:
                pass
        
        # Memória
        return self.memory_cache.get(key)

    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Define um valor genérico no cache."""
        # Memória
        self.memory_cache[key] = value
        
        # Redis
        if self.redis_client:
            try:
                if isinstance(value, (dict, list)):
                    val_str = json.dumps(value)
                else:
                    val_str = str(value)
                self.redis_client.setex(key, ttl_seconds, val_str)
            except Exception as e:
                logging.error(f"Erro ao salvar no Redis: {e}")
