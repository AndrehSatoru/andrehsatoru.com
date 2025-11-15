# Plataforma de Análise de Investimentos

Uma plataforma full-stack para análise de risco, otimização de portfólio e análise técnica de investimentos, com um backend em FastAPI e um frontend em React.

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)


## 🚀 Início Rápido (Recomendado)

A maneira mais fácil de executar a plataforma completa (backend + frontend) é com o Docker Compose.

**Pré-requisitos:**
- Docker e Docker Compose instalados.
- Git instalado.

```bash
# 1. Clone o repositório
git clone https://github.com/your-username/investment-backend.git
cd investment-backend

# 2. Crie e configure o arquivo de ambiente
cp .env.example .env
# Abra o .env e adicione suas chaves de API (FINNHUB_API_KEY, ALPHA_VANTAGE_API_KEY)
# Você pode obter as chaves em:
# - Finnhub: https://finnhub.io/
# - Alpha Vantage: https://www.alphavantage.co/

# 3. Construa e execute os serviços
docker-compose up --build -d
```

Você pode acessar:
- **Frontend (React App):** [http://localhost:3000](http://localhost:3000)
- **Documentação da API (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

## 📚 Documentação

- **[Início Rápido da API](API_QUICKSTART.md)**: Exemplos práticos de uso da API.
- **[Guia de Configuração](CONFIGURATION.md)**: Guia para variáveis de ambiente.
- **[Guia de Implantação](DEPLOYMENT.md)**: Implantação em produção.
- **[Changelog](CHANGELOG.md)**: Histórico de versões.

## ✨ Funcionalidades

### 📊 Análise Técnica
- Médias móveis SMA/EMA com janelas personalizáveis.
- MACD (Convergência e Divergência de Médias Móveis).
- Gráficos PNG de preços + indicadores.

### 📉 Métricas de Risco
- **VaR** (Value at Risk): histórico, paramétrico (std/ewma/garch), EVT.
- **ES/CVaR** (Expected Shortfall): perda média além do VaR.
- **IVaR** (Incremental VaR): sensibilidade a mudanças de peso.
- **MVaR** (Marginal VaR): impacto da remoção de ativos.
- **VaR Relativo**: risco de desempenho inferior a um benchmark.
- **Drawdown**: queda máxima do pico ao vale.
- **Testes de Estresse**: cenários de choque.
- **Backtesting**: validação com Kupiec, Christoffersen, zonas de Basileia.

### 🎯 Otimização
- **Markowitz**: max Sharpe, variância mínima, retorno máximo.
- **Black-Litterman**: incorporação de visões subjetivas.
- **Fronteira Eficiente**: visualização do trade-off risco-retorno.

### 📈 Modelos de Fatores
- **CAPM**: beta, alfa, índice de Sharpe.
- **APT**: regressão multifatorial.

### 🎲 Simulação
- **Monte Carlo**: GBM (Movimento Browniano Geométrico).
- **Atribuição de Risco**: contribuição por ativo.

## 🏗️ Arquitetura

Este projeto segue uma arquitetura desacoplada com um backend Python/FastAPI servindo um frontend React.

```
investment-backend/
├── investment-frontend/      # Frontend React (SPA)
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── services/         # Comunicação com a API
│   │   └── App.tsx           # Componente principal
│   └── package.json
├── src/backend_projeto/      # Backend FastAPI
│   ├── api/                  # Endpoints da API (Modulares)
│   │   ├── risk_endpoints.py
│   │   ├── optimization_endpoints.py
│   │   └── ... (11 módulos no total)
│   ├── core/                 # Lógica de Negócio
│   │   ├── analysis.py
│   │   ├── optimization.py
│   │   └── ...
│   ├── utils/                # Utilitários
│   └── main.py               # Ponto de entrada do FastAPI
├── tests/                    # Testes Pytest
├── .github/                  # Workflows de CI/CD
├── .env.example              # Template de ambiente
├── requirements.txt          # Dependências Python
├── docker-compose.yml        # Orquestração Docker
└── Dockerfile                # Imagem Docker do Backend
```

## 🔧 Tecnologias

- **Backend:** FastAPI, Pydantic, Pandas, NumPy, SciPy, scikit-learn, yfinance
- **Frontend:** React, TypeScript, Material-UI (MUI)
- **Banco de Dados/Cache:** Redis (opcional, para cache)
- **Testes:** Pytest, pytest-mock, httpx
- **DevOps:** Docker, Docker Compose, GitHub Actions

## 📡 Endpoints da API

A API é organizada em módulos lógicos e fornece uma ampla gama de endpoints para análise financeira. Para uma lista completa e interativa de todos os endpoints disponíveis, execute a aplicação e visite a documentação Swagger gerada automaticamente em **[http://localhost:8000/docs](http://localhost:8000/docs)**.

## 🧪 Testes

O projeto possui uma suíte de testes abrangente usando `pytest`.

```bash
# Navegue para o diretório do backend se você estiver na raiz
# cd investment-backend

# Execute todos os testes com relatório de cobertura
pytest -v --tb=short --cov=src/backend_projeto --cov-report=xml --cov-report=term
```

**Cobertura Atual:** ~90%

## 🐳 Desenvolvimento com Docker

O arquivo `docker-compose.yml` é configurado para produção e desenvolvimento.

```bash
# Construa e inicie todos os serviços em modo detached
docker-compose up --build -d

# Visualize os logs de um serviço específico (ex: a API)
docker-compose logs -f api

# Pare e remova todos os serviços
docker-compose down
```

## 💻 Desenvolvimento Manual (Sem Docker)

Se você prefere executar os serviços manualmente:

### Backend

**Pré-requisitos:**
- Python 3.9+
- Pip

```bash
# 1. Navegue para o diretório raiz
# cd investment-backend

# 2. Instale as dependências Python
pip install -r requirements.txt

# 3. Configure o ambiente
cp .env.example .env
# Edite o .env com suas chaves de API

# 4. Inicie o servidor
cd src/backend_projeto
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

**Pré-requisitos:**
- Node.js 18+
- npm

```bash
# 1. Navegue para o diretório do frontend
cd investment-frontend

# 2. Instale as dependências Node.js
npm install

# 3. Inicie o servidor de desenvolvimento
npm start
```
O aplicativo React estará disponível em `http://localhost:3000`.

## 🤝 Contribuição

1.  Faça um fork do projeto.
2.  Crie uma branch de feature (`git checkout -b feature/new-feature`).
3.  Faça commit de suas mudanças (`git commit -am 'Add new feature'`).
4.  Faça push para a branch (`git push origin feature/new-feature`).
5.  Abra um Pull Request.

## 📝 Licença

Este projeto ainda não está licenciado sob a Licença MIT.

## 👥 Autores

- Andreh Satoru Yamagawa

## 🙏 Agradecimentos

- Saurão
- Comunidade FastAPI
- Contribuidores do Pandas/NumPy/SciPy
- Literatura de gestão de risco (Dowd, Jorion, RiskMetrics)
