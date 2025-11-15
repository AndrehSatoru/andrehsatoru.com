#!/usr/bin/env python3
"""
Script de teste específico para identificar problemas com gráficos financeiros.
"""

import os
import sys
import traceback
from datetime import datetime, timedelta

# Adicionar o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_data_loading():
    """Testa carregamento de dados financeiros."""
    print("🔍 Testando carregamento de dados...")

    try:
        from src.backend_projeto.core.data_handling import YFinanceProvider
        from src.backend_projeto.utils.config import Config

        config = Config()
        loader = YFinanceProvider()

        # Testar com ativo válido
        assets = ['PETR4.SA']
        start_date = '2023-01-01'
        end_date = '2024-01-01'

        print(f"  Buscando dados para {assets} de {start_date} a {end_date}...")

        try:
            prices = loader.fetch_stock_prices(assets, start_date, end_date)
            print(f"  ✅ Dados carregados: {prices.shape}")
            print(f"  📊 Colunas: {list(prices.columns)}")
            print(f"  📅 Período: {prices.index.min()} a {prices.index.max()}")

            if prices.empty or prices.iloc[0, 0] <= 0:
                print("  ⚠️  Dados vazios ou inválidos")
                return None

            return prices

        except Exception as e:
            print(f"  ❌ Erro ao buscar dados: {e}")
            traceback.print_exc()
            return None

    except Exception as e:
        print(f"  ❌ Erro na configuração: {e}")
        traceback.print_exc()
        return None

def test_technical_analysis():
    """Testa análise técnica básica."""
    print("\n🔍 Testando análise técnica...")

    prices = test_data_loading()
    if prices is None:
        print("  ⏭️  Pulando teste de análise técnica (sem dados)")
        return False

    try:
        from src.backend_projeto.core.technical_analysis import moving_averages, macd_series

        asset = prices.columns[0]
        print(f"  Calculando médias móveis para {asset}...")

        # Testar médias móveis
        ma_df = moving_averages(prices[[asset]], windows=[5, 21], method='sma')
        print(f"  ✅ Médias móveis calculadas: {ma_df.shape}")

        # Testar MACD
        macd_df = macd_series(prices[[asset]], fast=12, slow=26, signal=9)
        print(f"  ✅ MACD calculado: {macd_df.shape}")

        return True

    except Exception as e:
        print(f"  ❌ Erro na análise técnica: {e}")
        traceback.print_exc()
        return False

def test_chart_generation():
    """Testa geração de gráficos."""
    print("\n🔍 Testando geração de gráficos...")

    prices = test_data_loading()
    if prices is None:
        print("  ⏭️  Pulando teste de gráficos (sem dados)")
        return False

    try:
        from src.backend_projeto.core.visualizations.ta_visualization import plot_price_with_ma, plot_macd
        from src.backend_projeto.core.visualizations.comprehensive_visualization import ComprehensiveVisualizer
        from src.backend_projeto.core.data_handling import YFinanceProvider

        asset = prices.columns[0]
        output_dir = "test_graficos"

        print(f"  Gerando gráficos para {asset}...")

        # Testar gráfico de médias móveis
        ma_bytes = plot_price_with_ma(prices, asset, windows=[5, 21], method='sma')
        print(f"  ✅ Gráfico de médias móveis gerado ({len(ma_bytes)} bytes)")

        # Testar gráfico MACD
        macd_bytes = plot_macd(prices, asset, fast=12, slow=26, signal=9)
        print(f"  ✅ Gráfico MACD gerado ({len(macd_bytes)} bytes)")

        # Testar visualizador completo
        visualizer = ComprehensiveVisualizer(output_dir=output_dir)
        loader = YFinanceProvider()
        generated_files = visualizer.generate_all_charts(
            assets=[asset],
            start_date='2023-01-01',
            end_date='2024-01-01',
            loader=loader
        )

        print(f"  ✅ Visualizador executado: {len(generated_files)} arquivos")

        return True

    except Exception as e:
        print(f"  ❌ Erro na geração de gráficos: {e}")
        traceback.print_exc()
        return False

def main():
    """Função principal."""
    print("🚀 Teste específico de gráficos financeiros")
    print("=" * 50)

    # Teste 1: Carregamento de dados
    if not test_data_loading():
        print("\n❌ Problemas no carregamento de dados")
        return False

    # Teste 2: Análise técnica
    if not test_technical_analysis():
        print("\n❌ Problemas na análise técnica")
        return False

    # Teste 3: Geração de gráficos
    if not test_chart_generation():
        print("\n❌ Problemas na geração de gráficos")
        return False

    print("\n✅ Todos os testes específicos passaram!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)