# packages/backend/src/backend_projeto/api/__init__.py

from . import advanced_endpoints
from . import analysis_endpoints
from . import dashboard_endpoints
from . import data_endpoints
from . import deps
from . import endpoints
from . import factor_endpoints
from . import helpers
from . import models
from . import optimization_endpoints
from . import portfolio_endpoints
from . import portfolio_simulation
from . import risk_endpoints
from . import system_endpoints
from . import technical_analysis_endpoints
from . import transaction_endpoints
from . import visualization_endpoints
from . import auth_endpoints # New import

# Alias portfolio_simulation to portfolio_simulation_endpoints to fix ImportError in main.py
portfolio_simulation_endpoints = portfolio_simulation