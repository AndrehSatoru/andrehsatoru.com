"""
Domain constants and configuration values.
"""

from typing import List, Dict

# Proxies used to estimate CDI/Risk-Free Rate when direct data is unavailable
# ^IRX is the 13-week Treasury Bill rate, often used as a proxy for short-term risk-free rate
CDI_PROXIES: List[str] = ['^IRX']

# Mapping for month numbers to string representations (used in response formatting)
# Note: Keys are integers 1-12. 'set_' is used to avoid conflicts or specific formatting needs in frontend
MONTH_MAP: Dict[int, str] = {
    1: 'jan', 2: 'fev', 3: 'mar', 4: 'abr', 5: 'mai', 6: 'jun',
    7: 'jul', 8: 'ago', 9: 'set', 10: 'out', 11: 'nov', 12: 'dez'
}
