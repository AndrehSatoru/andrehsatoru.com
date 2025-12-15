import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from backend_projeto.main import app
    return TestClient(app)

def test_plot_efficient_frontier(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "n_samples": 100,
        "long_only": True,
        "rf": 0.01
    }
    r = client.post("/api/v1/plots/efficient-frontier", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"

def test_plot_ff_factors_endpoint(client: TestClient):
    payload = {
        "model": "ff3",
        "start_date": "2020-01-01",
        "end_date": "2020-12-31"
    }
    r = client.post("/api/v1/plots/ff-factors", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"

def test_plot_ff_betas_endpoint(client: TestClient):
    payload = {
        "asset": "AAA.SA",
        "model": "ff3",
        "start_date": "2020-01-01",
        "end_date": "2020-12-31",
        "rf_source": "ff"
    }
    r = client.post("/api/v1/plots/ff-betas", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"

def test_plot_technical_analysis(client: TestClient):
    payload = {
        "asset": "AAA.SA",
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "plot_type": "combined",
        "ma_windows": [5, 21],
        "ma_method": "sma",
        "macd_fast": 12,
        "macd_slow": 26,
        "macd_signal": 9
    }
    r = client.post("/api/v1/plots/ta", json=payload)
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"

def test_generate_comprehensive_charts(client: TestClient):
    payload = {
        "assets": ["AAA.SA", "BBB.SA"],
        "start_date": "2024-01-01",
        "end_date": "2024-03-01",
        "output_dir": "generated_plots",
        "chart_types": ["technical_analysis", "efficient_frontier"]
    }
    r = client.post("/api/v1/plots/comprehensive", json=payload)
    assert r.status_code == 200
    js = r.json()
    assert "generated_files" in js and len(js["generated_files"]) > 0
