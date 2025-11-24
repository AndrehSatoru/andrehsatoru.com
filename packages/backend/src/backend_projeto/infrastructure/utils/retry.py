import time
import logging
from functools import wraps
from typing import Callable, TypeVar, Any

T = TypeVar('T')

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 2.0) -> Callable:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        logging.error(f"Max retries ({max_retries}) exceeded for {func.__name__}")
                        raise e
                    wait_time = (backoff_factor ** retries) + 0.1
                    logging.warning(f"Retry {retries}/{max_retries} for {func.__name__} after {wait_time:.2f}s. Error: {str(e)}")
                    time.sleep(wait_time)
        return wrapper
    return decorator