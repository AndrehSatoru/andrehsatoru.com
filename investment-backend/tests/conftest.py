import pandas as pd
import numpy as np
import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from src.backend_projeto.main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)


def _make_prices(assets, start_date, end_date):
    dates = pd.bdate_range(start=start_date, end=end_date)
    data = {}
    for i, a in enumerate(assets):
        # série determinística e crescente
        data[a] = np.linspace(100 + i, 110 + i, num=len(dates))
    return pd.DataFrame(data, index=dates)


@pytest.fixture(autouse=True)
def stub_fetch_prices(monkeypatch):
    # Stub global para evitar chamadas externas em testes
    def fake_fetch(self, assets, start_date, end_date):
        return _make_prices(assets, start_date, end_date)
    monkeypatch.setattr(
        "src.backend_projeto.core.data_handling.DataLoader.fetch_stock_prices",
        fake_fetch,
        raising=True,
    )
    yield
