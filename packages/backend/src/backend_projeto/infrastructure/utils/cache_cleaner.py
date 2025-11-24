# cache_cleaner.py

import threading
import time
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

class CacheCleaner:
    def __init__(self, cache_dict: Dict[str, Any], ttl_seconds: int = 3600):
        self.cache = cache_dict
        self.ttl = ttl_seconds
        self.last_clean = datetime.now()
        self._start_cleaner()

    def _start_cleaner(self):
        def clean_periodically():
            while True:
                time.sleep(300)  # Check every 5 minutes
                self._clean_old_entries()

        thread = threading.Thread(target=clean_periodically, daemon=True)
        thread.start()

    def _clean_old_entries(self):
        """Remove entries older than TTL."""
        now = datetime.now()
        if (now - self.last_clean).total_seconds() < self.ttl:
            return

        logging.info("Cleaning cache...")
        self.cache.clear()
        self.last_clean = now
        logging.info("Cache cleaned")