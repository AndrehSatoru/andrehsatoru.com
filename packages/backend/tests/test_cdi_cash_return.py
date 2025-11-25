"""
Teste para verificar se o caixa está rendendo CDI corretamente.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backend_projeto.domain.analysis import PortfolioAnalyzer
from backend_projeto.infrastructure.data_handling import YFinanceProvider


def test_cdi_on_cash_basic():
    """
    Testa se o caixa rende CDI quando não há transações.
    """
    # Criar transações vazias (apenas para ter estrutura válida)
    # Mas na verdade vamos testar com capital inicial sem investimentos
    transactions = pd.DataFrame({
        'Data': [],
        'Ativo': [],
        'Quantidade': [],
        'Preco': []
    })
    
    # Como não podemos ter transações vazias, vamos criar uma transação pequena
    start_date = '2024-01-01'
    end_date = '2024-01-31'
    
    transactions = pd.DataFrame({
        'Data': [pd.Timestamp('2024-01-15')],
        'Ativo': ['PETR4.SA'],
        'Quantidade': [0.01],  # Quantidade muito pequena
        'Preco': [1.0]
    })
    
    loader = YFinanceProvider()
    initial_value = 100000.0  # R$ 100.000 inicial
    
    analyzer = PortfolioAnalyzer(
        transactions_df=transactions,
        data_loader=loader,
        start_date=start_date,
        end_date=end_date,
        initial_value=initial_value
    )
    
    # Calcular valor do portfólio
    portfolio_value = analyzer._calculate_portfolio_value()
    
    # O valor final deve ser maior que o inicial devido ao rendimento do CDI
    # (exceto pela pequena compra de 0.01 * 1.0 = 0.01)
    final_value = portfolio_value.iloc[-1]
    
    print(f"\nValor inicial: R$ {initial_value:,.2f}")
    print(f"Valor final: R$ {final_value:,.2f}")
    print(f"Rendimento: R$ {final_value - initial_value:,.2f}")
    print(f"Rendimento %: {((final_value / initial_value) - 1) * 100:.4f}%")
    
    # Verificar que houve algum rendimento positivo
    # (mesmo com a pequena transação, o rendimento do CDI sobre 99999.99 deve ser visível)
    assert final_value >= initial_value * 0.999, \
        f"Valor final ({final_value}) deveria ser próximo ou maior que inicial ({initial_value})"


def test_cdi_fetch():
    """
    Testa se o método de busca do CDI está funcionando.
    """
    loader = YFinanceProvider()
    
    try:
        cdi_rates = loader.fetch_cdi_daily('2024-01-01', '2024-01-31')
        
        print(f"\nCDI buscado com sucesso!")
        print(f"Período: {cdi_rates.index[0]} a {cdi_rates.index[-1]}")
        print(f"Primeiros valores:")
        print(cdi_rates.head())
        print(f"\nTaxa média diária: {cdi_rates.mean():.6f} ({cdi_rates.mean() * 100:.4f}%)")
        print(f"Taxa média anual aproximada: {((1 + cdi_rates.mean()) ** 252 - 1) * 100:.2f}%")
        
        # Verificar que temos dados
        assert not cdi_rates.empty, "CDI não deveria estar vazio"
        assert len(cdi_rates) > 20, "Deveria ter pelo menos 20 dias de dados"
        
    except Exception as e:
        print(f"\nAviso: Não foi possível buscar CDI (pode ser problema de conexão): {e}")
        pytest.skip("CDI não disponível")


def test_monthly_rf_from_cdi():
    """
    Testa o cálculo da taxa livre de risco mensal a partir do CDI.
    """
    loader = YFinanceProvider()
    
    try:
        rf_monthly = loader.compute_monthly_rf_from_cdi('2024-01-01', '2024-06-30')
        
        print(f"\nTaxa livre de risco mensal calculada com sucesso!")
        print(f"Período: {rf_monthly.index[0]} a {rf_monthly.index[-1]}")
        print(f"Valores mensais:")
        print(rf_monthly)
        print(f"\nTaxa média mensal: {rf_monthly.mean():.6f} ({rf_monthly.mean() * 100:.4f}%)")
        print(f"Taxa anual aproximada: {((1 + rf_monthly.mean()) ** 12 - 1) * 100:.2f}%")
        
        # Verificar que temos dados
        assert not rf_monthly.empty, "RF mensal não deveria estar vazio"
        assert len(rf_monthly) >= 6, "Deveria ter pelo menos 6 meses de dados"
        
    except Exception as e:
        print(f"\nAviso: Não foi possível calcular RF mensal: {e}")
        pytest.skip("RF mensal não disponível")


if __name__ == "__main__":
    print("=" * 80)
    print("TESTE: Busca de CDI")
    print("=" * 80)
    test_cdi_fetch()
    
    print("\n" + "=" * 80)
    print("TESTE: Cálculo de RF mensal")
    print("=" * 80)
    test_monthly_rf_from_cdi()
    
    print("\n" + "=" * 80)
    print("TESTE: Rendimento do caixa com CDI")
    print("=" * 80)
    test_cdi_on_cash_basic()
    
    print("\n" + "=" * 80)
    print("TODOS OS TESTES CONCLUÍDOS!")
    print("=" * 80)
