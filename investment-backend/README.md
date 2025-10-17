# Investment Backend API

API REST para análise de risco, otimização de portfólio e análise técnica de investimentos.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)

## 🚀 Quick Start

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env

# Iniciar servidor
cd src/backend_projeto
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Acesse: http://localhost:8000/docs

## 📚 Documentação

- **[API Quick Start](API_QUICKSTART.md)**: Exemplos práticos de uso
- **[Configuration Guide](CONFIGURATION.md)**: Guia de configuração e env vars
- **[Deployment Guide](DEPLOYMENT.md)**: Deploy em produção
- **[Improvements Summary](IMPROVEMENTS_SUMMARY.md)**: Detalhamento técnico
- **[Changelog](CHANGELOG.md)**: Histórico de versões

## ✨ Funcionalidades

### 📊 Análise Técnica
- Médias Móveis (SMA/EMA) com janelas customizáveis
- MACD (Moving Average Convergence Divergence)
- Gráficos PNG de preços + indicadores

### 📉 Métricas de Risco
- **VaR** (Value at Risk): historical, paramétrico (std/ewma/garch), EVT
- **ES/CVaR** (Expected Shortfall): perda média além do VaR
- **IVaR** (Incremental VaR): sensibilidade a mudanças nos pesos
- **MVaR** (Marginal VaR): impacto de remover ativos
- **VaR Relativo**: risco de underperformance vs benchmark
- **Drawdown**: máxima queda de pico a vale
- **Stress Testing**: cenários de choque
- **Backtest**: validação com Kupiec, Christoffersen, Basel zones

### 🎯 Otimização
- **Markowitz**: max Sharpe, min variância, max retorno
- **Black-Litterman**: incorporação de views subjetivas
- **Fronteira Eficiente**: visualização de trade-offs risco-retorno

### 📈 Modelos Fatoriais
- **CAPM**: beta, alpha, Sharpe ratio
- **APT**: regressão multifatorial

### 🎲 Simulação
- **Monte Carlo**: GBM (Geometric Brownian Motion)
- **Atribuição de Risco**: contribuição por ativo

## 🏗️ Arquitetura

```
investment-backend/
├── src/backend_projeto/
│   ├── api/              # Endpoints e modelos
│   │   ├── deps.py       # Dependency injection
│   │   ├── endpoints.py  # Rotas FastAPI
│   │   └── models.py     # Pydantic models
│   ├── core/             # Lógica de negócio
│   │   ├── analysis.py   # Métricas de risco
│   │   ├── optimization.py
│   │   ├── simulation.py
│   │   ├── technical_analysis.py
│   │   ├── ta_visualization.py
│   │   └── data_handling.py
│   ├── utils/            # Utilitários
│   │   ├── config.py
│   │   ├── logging_setup.py
│   │   ├── rate_limiter.py
│   │   └── sanitization.py
│   └── main.py           # Entry point
├── tests/                # Testes
│   ├── api/              # Testes de integração
│   └── unit/             # Testes unitários
├── .env.example          # Template de configuração
├── requirements.txt      # Dependências
├── Dockerfile            # Container Docker
└── docker-compose.yml    # Orquestração
```

## 🔧 Tecnologias

- **FastAPI**: Framework web moderno e rápido
- **Pydantic**: Validação de dados
- **Pandas/NumPy**: Manipulação de dados
- **SciPy**: Estatística e otimização
- **scikit-learn**: Machine learning (Ledoit-Wolf, etc.)
- **yfinance**: Dados de mercado
- **matplotlib**: Visualização
- **pytest**: Testes

## 📡 Endpoints (22 Total)

### System
- `GET /status` - Health check
- `GET /config` - Configurações públicas

### Data
- `POST /prices` - Preços históricos

### Technical Analysis
- `POST /ta/moving-averages` - Médias móveis
- `POST /ta/macd` - MACD

### Risk - Core
- `POST /risk/var` - Value at Risk
- `POST /risk/es` - Expected Shortfall
- `POST /risk/drawdown` - Maximum Drawdown

### Risk - Advanced
- `POST /risk/ivar` - Incremental VaR
- `POST /risk/mvar` - Marginal VaR
- `POST /risk/relvar` - VaR Relativo

### Risk - Scenario & Validation
- `POST /risk/stress` - Stress testing
- `POST /risk/backtest` - Backtest VaR
- `POST /risk/compare` - Comparar métodos

### Risk - Simulation & Analytics
- `POST /risk/montecarlo` - Monte Carlo
- `POST /risk/covariance` - Matriz de covariância
- `POST /risk/attribution` - Atribuição de risco

### Optimization
- `POST /opt/markowitz` - Otimização Markowitz
- `POST /opt/blacklitterman` - Black-Litterman

### Factor Models
- `POST /factors/capm` - CAPM
- `POST /factors/apt` - APT

### Visualization
- `POST /plots/efficient-frontier` - Fronteira eficiente
- `POST /plots/ta` - Gráficos de análise técnica

## 🧪 Testes

```bash
# Rodar todos os testes
pytest -v

# Com cobertura
pytest --cov=src/backend_projeto --cov-report=html

# Apenas testes rápidos
pytest -m "not slow"
```

**Cobertura atual**: ~90%

## 🐳 Docker

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Logs
docker-compose logs -f api

# Stop
docker-compose down
```

## 🔒 Segurança

- ✅ Validação de entrada via Pydantic
- ✅ Sanitização de tickers e datas
- ✅ Rate limiting (configurável)
- ✅ Circuit breaker para APIs externas
- ✅ Limite de 100 ativos por request
- ✅ Timeout configurável
- ✅ Logs estruturados (JSON)

## ⚡ Performance

- **Cache**: Dados históricos cacheados automaticamente
- **GZip**: Compressão automática (>1KB)
- **Filtros**: Redução de payload em até 80%
- **Retry**: Backoff exponencial para resiliência
- **Workers**: Suporte a múltiplos workers Uvicorn

## 📊 Exemplo de Uso

```python
import requests

# VaR de uma carteira
response = requests.post("http://localhost:8000/risk/var", json={
    "assets": ["PETR4.SA", "VALE3.SA"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "weights": [0.6, 0.4],
    "alpha": 0.99,
    "method": "historical"
})

var_result = response.json()
print(f"VaR 99%: {var_result['result']['var']:.2%}")
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 👥 Autores

- Andreh Satoru Yamagawa

## 🙏 Agradecimentos

- Saurão
- FastAPI community
- Pandas/NumPy/SciPy contributors
- Risk management literature (Dowd, Jorion, RiskMetrics)

---

**Versão**: 1.0.0  
**Última atualização**: 2025-10-09
