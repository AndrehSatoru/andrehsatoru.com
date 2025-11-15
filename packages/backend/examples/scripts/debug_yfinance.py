import yfinance as yf
import pandas as pd

# Silenciar alguns avisos do yfinance
pd.options.mode.chained_assignment = None

print(f"yfinance version: {yf.__version__}")

print("\n--- Testando um ticker conhecido (MSFT) ---")
try:
    msft = yf.Ticker("MSFT")
    hist = msft.history(period="1mo")
    if not hist.empty:
        print("Dados de MSFT obtidos com sucesso:")
        print(hist.head(2))
    else:
        print("Falha ao obter dados para MSFT.")
except Exception as e:
    print(f"Erro ao buscar MSFT: {e}")

print("\n--- Testando um dos tickers do usuário (EQTL3.SA) ---")
try:
    eqtl = yf.Ticker("EQTL3.SA")
    hist = eqtl.history(period="1mo")
    if not hist.empty:
        print("Dados de EQTL3.SA obtidos com sucesso:")
        print(hist.head(2))
    else:
        print("Falha ao obter dados para EQTL3.SA.")
except Exception as e:
    print(f"Erro ao buscar EQTL3.SA: {e}")

print("\n--- Testando o ticker 'VAL' ---")
try:
    val = yf.Ticker("VAL")
    hist = val.history(period="1mo")
    if not hist.empty:
        print("Dados de VAL obtidos com sucesso:")
        print(hist.head(2))
    else:
        print("Falha ao obter dados para VAL.")
except Exception as e:
    print(f"Erro ao buscar VAL: {e}")

print("\n--- Testando o ticker 'VALE' para comparação ---")
try:
    vale = yf.Ticker("VALE")
    hist = vale.history(period="1mo")
    if not hist.empty:
        print("Dados de VALE obtidos com sucesso:")
        print(hist.head(2))
    else:
        print("Falha ao obter dados para VALE.")
except Exception as e:
    print(f"Erro ao buscar VALE: {e}")
