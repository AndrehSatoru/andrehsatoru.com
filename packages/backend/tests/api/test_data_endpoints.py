import pytest
from fastapi.testclient import TestClient
import pandas as pd
import numpy as np

from backend_projeto.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_prices(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01"
    }
    r = client.post("/api/v1/prices", json=payload)
    assert r.status_code == 200
    js = r.json()
    assert set(js.keys()) == {"columns", "index", "data"}
    assert js["columns"] == payload["assets"]
    assert len(js["index"]) > 0
    assert len(js["data"]) == len(js["index"])  # linhas
