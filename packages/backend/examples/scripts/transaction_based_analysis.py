#!/usr/bin/env python3
"""
Script para análise de portfólio baseada em transações, com busca de dados otimizada.
"""

import json
import pandas as pd
import yfinance as yf
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# --- Configurações ---
PORTFOLIO_FILE = os.path.join("portfolio_analysis_inputs", "ativos.json")
OUTPUT_DIR = "portfolio_analysis_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Funções Principais ---

def load_portfolio_definition(file_path):
    """Carrega a definição do portfólio do arquivo JSON."""
    print(f"[INFO] Carregando portfólio de: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        portfolio_data = data.get("portfolio")
        if not portfolio_data:
            raise ValueError("Estrutura do JSON inválida. Chave 'portfolio' não encontrada.")
        required_keys = ["start_date", "end_date", "transactions", "initial_cash"] # Added initial_cash
        for key in required_keys:
            if key not in portfolio_data:
                raise ValueError(f"Chave obrigatória '{key}' não encontrada no JSON.")
        print("[INFO] Definição do portfólio carregada com sucesso.")
        return portfolio_data
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"[ERRO] Falha ao carregar o portfólio: {e}")
        raise

def fetch_all_data(tickers, start_date, end_date):
    """Busca todos os preços e dividendos de uma vez para os tickers fornecidos."""
    print(f"[INFO] Buscando dados de preços e dividendos para {len(tickers)} ativos de {start_date} a {end_date}...")
    try:
        data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker')
        
        if data.empty:
            raise ValueError("yf.download não retornou dados. Verifique os tickers e o período.")

        prices_df = pd.DataFrame()
        dividends_df = pd.DataFrame()
        
        failed_tickers = []
        for ticker in tickers:
            if ticker in data.columns:
                # Extrair preços de fechamento
                prices_df[ticker] = data[ticker]['Close']
                # Extrair dividendos, verificando se a coluna existe
                if 'Dividends' in data[ticker].columns:
                    dividends_df[ticker] = data[ticker]['Dividends']
                else:
                    # Se não houver coluna de dividendos, criar uma série de zeros com o mesmo índice dos preços
                    dividends_df[ticker] = pd.Series(0.0, index=prices_df.index)
            else:
                failed_tickers.append(ticker)

        if failed_tickers:
            print(f"[AVISO] Falha ao buscar dados para os seguintes tickers: {', '.join(failed_tickers)}")
            valid_tickers = [ticker for ticker in tickers if ticker not in failed_tickers]
            if not valid_tickers:
                raise ValueError("Nenhum dado de preço pôde ser obtido para nenhum dos tickers.")
            prices_df = prices_df[valid_tickers]
            dividends_df = dividends_df[valid_tickers] # Ensure dividends_df also only has valid tickers

        prices_df = prices_df.ffill().bfill() # Preencher quaisquer lacunas nos dados
        dividends_df = dividends_df.fillna(0) # Dividendos ausentes são 0

        print("[INFO] Busca de dados de preços e dividendos concluída.")
        return prices_df, dividends_df

    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha na busca de dados de preços e dividendos: {e}")
        raise

def fetch_cdi_rates(start_date, end_date):
    """
    Busca as taxas diárias do CDI.
    Para simplificar, usaremos uma taxa anual constante e a converteremos para diária.
    Em um cenário real, buscaríamos dados históricos do CDI.
    """
    print("[INFO] Buscando taxas CDI (usando taxa anual constante para simplificar)...")
    # Taxa CDI anual de exemplo (e.g., 13.65% em 2023)
    annual_cdi_rate = 0.1365 
    daily_cdi_rate = (1 + annual_cdi_rate)**(1/252) - 1 # Assumindo 252 dias úteis
    
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    cdi_series = pd.Series(daily_cdi_rate, index=date_range)
    
    print("[INFO] Taxas CDI geradas.")
    return cdi_series

def get_price_on_date(ticker, date_str, prices_df):
    """Busca o preço de um ativo em uma data específica a partir de um DataFrame pré-buscado."""
    target_date = pd.to_datetime(date_str)
    
    if ticker not in prices_df.columns:
        return None

    if target_date in prices_df.index:
        price = prices_df.loc[target_date, ticker]
        if not pd.isna(price):
            return price
    
    future_dates = prices_df.index[prices_df.index > target_date]
    if not future_dates.empty:
        for next_trading_day in future_dates:
            price = prices_df.loc[next_trading_day, ticker]
            if not pd.isna(price):
                print(f"[INFO] Preço para {ticker} em {date_str} obtido no próximo dia útil: {next_trading_day.strftime('%Y-%m-%d')}")
                return price
        
    print(f"[AVISO] Não foi possível encontrar preço para {ticker} em ou após {date_str}.")
    return None

def process_transactions(transactions, start_date, end_date, prices_df, dividends_df, cdi_rates, initial_cash): # Added initial_cash
    """Processa transações, gerencia caixa e dividendos usando DataFrames pré-buscados."""
    print("[INFO] Processando transações, dividendos e rendimento de caixa...")
    transactions.sort(key=lambda x: x['date'])
    
    holdings = {'cash': initial_cash} # Initialize cash with initial_cash
    holdings_over_time = []
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    valid_tickers = prices_df.columns
    
    transaction_idx = 0
    for current_date in date_range:
        # 1. Aplicar rendimento do CDI ao caixa
        if current_date in cdi_rates.index:
            daily_cdi = cdi_rates.loc[current_date]
            holdings['cash'] *= (1 + daily_cdi)

        # 2. Processar dividendos
        if current_date in dividends_df.index:
            for ticker in valid_tickers:
                if ticker in holdings and holdings[ticker] > 0:
                    dividend_per_share = dividends_df.loc[current_date, ticker]
                    if dividend_per_share > 0:
                        total_dividend = dividend_per_share * holdings[ticker]
                        holdings['cash'] += total_dividend
                        print(f"  - DIVIDENDO: R$ {total_dividend:.2f} de {ticker} em {current_date.strftime('%Y-%m-%d')}")

        # 3. Processar transações
        while transaction_idx < len(transactions) and pd.to_datetime(transactions[transaction_idx]['date']) <= current_date:
            tx = transactions[transaction_idx]
            ticker = tx['ticker']
            
            if ticker not in valid_tickers:
                print(f"[AVISO] Pulando transação para o ticker '{ticker}' pois os dados de preço não foram encontrados.")
                transaction_idx += 1
                continue

            price = get_price_on_date(ticker, tx['date'], prices_df)
            if price is None or pd.isna(price):
                print(f"[ERRO] Pulando transação de {ticker} em {tx['date']} por falta de preço no DataFrame.")
                transaction_idx += 1
                continue

            quantity = tx['amount'] / price
            
            if tx['type'] == 'buy':
                if holdings['cash'] >= tx['amount']:
                    holdings[ticker] = holdings.get(ticker, 0) + quantity
                    holdings['cash'] -= tx['amount']
                    print(f"  - COMPRA: {quantity:.4f} de {ticker} em {tx['date']} ao preço de {price:.2f} (R$ {tx['amount']:.2f})")
                else:
                    print(f"[AVISO] Saldo insuficiente para COMPRA de {ticker} em {tx['date']}. Transação ignorada.")
            elif tx['type'] == 'sell':
                if holdings.get(ticker, 0) >= quantity:
                    holdings[ticker] = holdings.get(ticker, 0) - quantity
                    holdings['cash'] += tx['amount']
                    print(f"  - VENDA: {quantity:.4f} de {ticker} em {tx['date']} ao preço de {price:.2f} (R$ {tx['amount']:.2f})")
                else:
                    print(f"[AVISO] Quantidade insuficiente de {ticker} para VENDA em {tx['date']}. Transação ignorada.")

            transaction_idx += 1

        daily_holdings = holdings.copy()
        daily_holdings['date'] = current_date
        holdings_over_time.append(daily_holdings)

    print("[INFO] Processamento de transações, dividendos e caixa concluído.")
    return pd.DataFrame(holdings_over_time).set_index('date').fillna(0)

def calculate_portfolio_value(holdings_df, prices_df):
    """Calcula o valor diário do portfólio (ações + caixa) usando preços pré-buscados."""
    print("[INFO] Calculando o valor diário do portfólio (ações + caixa)...")
    
    portfolio_value_series = pd.Series(index=holdings_df.index, dtype=float)
    
    for date in holdings_df.index:
        current_value = holdings_df.loc[date, 'cash'] if 'cash' in holdings_df.columns else 0.0
        
        for ticker in prices_df.columns:
            if ticker in holdings_df.columns and holdings_df.loc[date, ticker] > 0:
                if date in prices_df.index and not pd.isna(prices_df.loc[date, ticker]):
                    current_value += holdings_df.loc[date, ticker] * prices_df.loc[date, ticker]
        portfolio_value_series.loc[date] = current_value
    
    print("[INFO] Cálculo do valor do portfólio (ações + caixa) concluído.")
    return pd.DataFrame(portfolio_value_series, columns=['Portfolio_Value'])

def plot_portfolio_performance(portfolio_value_df, output_file):
    """Plota a performance do valor do portfólio."""
    print(f"[INFO] Gerando gráfico de performance do portfólio...")
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(portfolio_value_df.index, portfolio_value_df['Portfolio_Value'], label='Valor da Carteira', color='blue', linewidth=2)
    ax.set_title('Performance da Carteira Baseada em Transações', fontsize=18, fontweight='bold')
    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel('Valor da Carteira (R$)', fontsize=12)
    ax.legend(loc='upper left')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    from matplotlib.ticker import FuncFormatter
    formatter = FuncFormatter(lambda x, p: f'R$ {x:,.0f}')
    ax.yaxis.set_major_formatter(formatter)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    plt.close()
    print(f"[OK] Gráfico salvo em: {output_file}")

def calculate_portfolio_kpis(portfolio_value_df, portfolio_returns):
    """Calcula os principais KPIs do portfólio."""
    print("[INFO] Calculando KPIs do portfólio...")
    
    initial_value = portfolio_value_df['Portfolio_Value'].iloc[0]
    final_value = portfolio_value_df['Portfolio_Value'].iloc[-1]
    
    total_return = (final_value / initial_value) - 1 if initial_value != 0 else 0
    
    # Anualização
    trading_days_in_period = len(portfolio_returns)
    years_in_period = trading_days_in_period / 252.0 # Assumindo 252 dias úteis por ano
    
    annualized_return = (1 + total_return)**(1/years_in_period) - 1 if years_in_period > 0 else 0
    annualized_volatility = portfolio_returns.std() * (252**0.5)
    
    # Sharpe Ratio (assumindo risk-free rate = 0 para simplicidade)
    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else 0
    
    # Max Drawdown
    cumulative_returns = (1 + portfolio_returns).cumprod()
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns / running_max) - 1
    max_drawdown = drawdown.min()
    
    # Calmar Ratio
    calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
    
    # Sortino Ratio (assumindo MAR = 0 para simplicidade)
    downside_returns = portfolio_returns[portfolio_returns < 0]
    downside_std = downside_returns.std() * (252**0.5) if not downside_returns.empty else 0
    sortino_ratio = annualized_return / downside_std if downside_std != 0 else 0

    kpis = {
        "Initial Value": initial_value,
        "Final Value": final_value,
        "Total Return": total_return,
        "Annualized Return": annualized_return,
        "Annualized Volatility": annualized_volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown": max_drawdown,
        "Calmar Ratio": calmar_ratio,
        "Sortino Ratio": sortino_ratio,
        "Trading Days": trading_days_in_period,
        "Years in Period": years_in_period
    }
    print("[INFO] KPIs calculados.")
    return kpis

def print_and_save_kpis(kpis, output_file):
    """Imprime os KPIs no console e salva em um arquivo."""
    print("\n" + "="*80)
    print("RESUMO DE PERFORMANCE DO PORTFÓLIO")
    print("="*80)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("RESUMO DE PERFORMANCE DO PORTFÓLIO\n")
        f.write("="*80 + "\n")
        for key, value in kpis.items():
            if isinstance(value, (float, pd.Series)):
                line = f"{key:<25}: {value:.2%}" if "Return" in key or "Drawdown" in key else f"{key:<25}: {value:,.2f}"
            else:
                line = f"{key:<25}: {value}"
            print(line)
            f.write(line + "\n")
        f.write("="*80 + "\n")
    print(f"[OK] KPIs salvos em: {output_file}")

def main():
    """Função principal para orquestrar a análise."""
    print("="*80)
    print("INICIANDO ANÁLISE DE PORTFÓLIO (VERSÃO OTIMIZADA COM CAIXA E DIVIDENDOS)")
    print("="*80)
    
    try:
        portfolio_def = load_portfolio_definition(PORTFOLIO_FILE)
        start_date = portfolio_def['start_date']
        end_date = portfolio_def['end_date']
        transactions = portfolio_def['transactions']
        initial_cash = portfolio_def.get('initial_cash', 0.0) # Get initial_cash, default to 0 if not present
        
        unique_tickers = list(set(tx['ticker'] for tx in transactions))
        
        prices_df, dividends_df = fetch_all_data(unique_tickers, start_date, end_date)
        cdi_rates = fetch_cdi_rates(start_date, end_date)
        
        holdings_df = process_transactions(transactions, start_date, end_date, prices_df, dividends_df, cdi_rates, initial_cash) # Pass initial_cash
        
        portfolio_value_df = calculate_portfolio_value(holdings_df, prices_df)
        
        if portfolio_value_df.empty or portfolio_value_df['Portfolio_Value'].sum() == 0:
            print("\n[AVISO] O valor do portfólio é zero. Nenhuma análise adicional será gerada.")
            return # Exit main if no portfolio value

        # Calculate portfolio returns
        portfolio_returns = portfolio_value_df['Portfolio_Value'].pct_change().dropna()

        # 5. Calcular e exibir KPIs
        kpis = calculate_portfolio_kpis(portfolio_value_df, portfolio_returns)
        print_and_save_kpis(kpis, os.path.join(OUTPUT_DIR, "portfolio_summary.txt"))

        # 6. Gerar gráfico de performance (já existente)
        output_path_perf = os.path.join(OUTPUT_DIR, "transaction_based_portfolio_performance.png")
        plot_portfolio_performance(portfolio_value_df, output_path_perf)
        
        print("\n" + "="*80)
        print("ANÁLISE CONCLUÍDA!")
        print("="*80)
        
    except (FileNotFoundError, json.JSONDecodeError, ValueError, Exception) as e:
        print(f"\n[FALHA CRÍTICA] A análise não pôde ser concluída. Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()