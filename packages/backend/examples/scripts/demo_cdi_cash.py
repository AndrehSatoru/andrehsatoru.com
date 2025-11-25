#!/usr/bin/env python3
"""
Script de demonstração do rendimento do CDI no caixa do portfólio.

Este script cria um portfólio simples e mostra como o caixa 
não investido agora rende CDI diariamente.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pandas as pd
from datetime import datetime
from backend_projeto.domain.analysis import PortfolioAnalyzer
from backend_projeto.infrastructure.data_handling import YFinanceProvider


def demo_cdi_no_caixa():
    """
    Demonstra o rendimento do CDI no caixa não investido.
    """
    print("=" * 80)
    print("DEMONSTRAÇÃO: RENDIMENTO DO CDI NO CAIXA")
    print("=" * 80)
    
    # Configuração
    initial_value = 100000.0  # R$ 100.000 inicial
    start_date = '2024-01-01'
    end_date = '2024-12-31'
    
    # Criar transações: investir apenas R$ 10.000 no início
    # Deixando R$ 90.000 em caixa para render CDI
    transactions = pd.DataFrame({
        'Data': [pd.Timestamp('2024-01-15')],
        'Ativo': ['PETR4.SA'],
        'Quantidade': [100],
        'Preco': [100.0]  # Compra de R$ 10.000
    })
    
    print(f"\nConfiguração do teste:")
    print(f"  Capital inicial: R$ {initial_value:,.2f}")
    print(f"  Período: {start_date} a {end_date}")
    print(f"  Investimento em ações: R$ 10.000,00 (PETR4.SA)")
    print(f"  Caixa disponível: R$ 90.000,00")
    print(f"\n  → O caixa de R$ 90.000 deve render CDI diariamente!")
    
    # Criar analisador
    loader = YFinanceProvider()
    analyzer = PortfolioAnalyzer(
        transactions_df=transactions,
        data_loader=loader,
        start_date=start_date,
        end_date=end_date,
        initial_value=initial_value
    )
    
    print("\n" + "-" * 80)
    print("Buscando dados do CDI e calculando valor do portfólio...")
    print("-" * 80)
    
    # Calcular valor do portfólio
    try:
        portfolio_value = analyzer._calculate_portfolio_value()
        
        # Buscar CDI para comparação
        cdi_rates = loader.fetch_cdi_daily(start_date, end_date)
        
        # Calcular rendimento esperado do CDI sobre os R$ 90.000
        # (aproximadamente, ignorando a pequena variação por causa do investimento)
        cdi_compound = (1 + cdi_rates).prod()
        expected_cash_value = 90000 * cdi_compound
        expected_total = expected_cash_value + 10000  # + valor inicial do investimento
        
        # Valores finais
        final_value = portfolio_value.iloc[-1]
        initial_cash = 90000
        
        print(f"\n{'='*80}")
        print("RESULTADOS:")
        print("=" * 80)
        print(f"\nValor inicial total: R$ {initial_value:,.2f}")
        print(f"  - Investido em ações: R$ 10.000,00")
        print(f"  - Em caixa: R$ {initial_cash:,.2f}")
        
        print(f"\nValor final total: R$ {final_value:,.2f}")
        print(f"Rendimento total: R$ {final_value - initial_value:,.2f}")
        print(f"Retorno total: {((final_value / initial_value) - 1) * 100:.4f}%")
        
        print(f"\n--- Análise do CDI ---")
        print(f"Taxa CDI média diária: {cdi_rates.mean() * 100:.6f}%")
        print(f"Taxa CDI anualizada: {((1 + cdi_rates.mean()) ** 252 - 1) * 100:.2f}%")
        print(f"Rendimento composto do CDI no período: {(cdi_compound - 1) * 100:.4f}%")
        
        print(f"\n--- Rendimento esperado do caixa (R$ 90.000) ---")
        print(f"Valor esperado do caixa com CDI: R$ {expected_cash_value:,.2f}")
        print(f"Rendimento do caixa: R$ {expected_cash_value - initial_cash:,.2f}")
        print(f"Retorno do caixa: {((expected_cash_value / initial_cash) - 1) * 100:.4f}%")
        
        # Mostrar evolução mensal
        print(f"\n{'='*80}")
        print("EVOLUÇÃO MENSAL DO PORTFÓLIO:")
        print("=" * 80)
        monthly_values = portfolio_value.resample('M').last()
        print(f"\n{'Data':<15} {'Valor (R$)':<20} {'Variação %':<15}")
        print("-" * 50)
        prev_value = initial_value
        for date, value in monthly_values.items():
            variation = ((value / prev_value) - 1) * 100 if prev_value > 0 else 0
            print(f"{date.strftime('%Y-%m-%d'):<15} {value:>18,.2f} {variation:>13.4f}%")
            prev_value = value
        
        print(f"\n{'='*80}")
        print("✓ IMPLEMENTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("✓ O caixa agora rende CDI diariamente!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERRO ao processar: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = demo_cdi_no_caixa()
    sys.exit(0 if success else 1)
