#!/usr/bin/env python3
"""
Script de teste específico para identificar problemas com gráficos financeiros.
"""

import os
import sys
import traceback
import logging
from datetime import datetime, timedelta

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Adicionar o diretório raiz do projeto ao path
# packages/backend/tests/.. -> packages/backend -> packages/backend/src
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

def test_data_loading():
    """Testa carregamento de dados financeiros."""
    logging.info("🔍 Testando carregamento de dados...")

    try:
        from backend_projeto.infrastructure.data_handling import YFinanceProvider
        from backend_projeto.infrastructure.utils.config import settings

        loader = YFinanceProvider()

        # Testar com ativo válido
        assets = ['PETR4.SA']
        start_date = '2023-01-01'
        end_date = '2024-01-01'

        logging.info(f"  Buscando dados para {assets} de {start_date} a {end_date}...")

        try:
            prices = loader.fetch_stock_prices(assets, start_date, end_date)
            logging.info(f"  ✅ Dados carregados: {prices.shape}")
            logging.info(f"  📊 Colunas: {list(prices.columns)}")
            logging.info(f"  📅 Período: {prices.index.min()} a {prices.index.max()}")

            if prices.empty or (len(prices) > 0 and prices.iloc[0, 0] <= 0):
                logging.warning("  ⚠️  Dados vazios ou inválidos")
                return None

            return prices

        except Exception as e:
            logging.error(f"  ❌ Erro ao buscar dados: {e}", exc_info=True)
            return None

    except Exception as e:
        logging.error(f"  ❌ Erro na configuração: {e}", exc_info=True)
        return None

def test_technical_analysis():
    """Testa análise técnica básica."""
    logging.info("\n🔍 Testando análise técnica...")

    prices = test_data_loading()
    if prices is None:
        logging.warning("  ⏭️  Pulando teste de análise técnica (sem dados)")
        return False

    try:
        # Imports ajustados para a estrutura observada
        from backend_projeto.domain.technical_analysis import calculate_moving_averages, calculate_macd

        asset = prices.columns[0]
        logging.info(f"  Calculando médias móveis para {asset}...")
        
        series = prices[asset]

        # Testar médias móveis
        ma_df = calculate_moving_averages(series, windows=[5, 21])
        logging.info(f"  ✅ Médias móveis calculadas: {ma_df.shape}")

        # Testar MACD
        macd_df = calculate_macd(series, fast=12, slow=26, signal=9)
        logging.info(f"  ✅ MACD calculado: {macd_df.shape}")

        return True

    except Exception as e:
        logging.error(f"  ❌ Erro na análise técnica: {e}", exc_info=True)
        return False

def test_chart_generation():
    """Testa geração de gráficos."""
    logging.info("\n🔍 Testando geração de gráficos...")

    prices = test_data_loading()
    if prices is None:
        logging.warning("  ⏭️  Pulando teste de gráficos (sem dados)")
        return False

    try:
        # Imports ajustados
        from backend_projeto.infrastructure.visualization.ta_visualization import generate_price_with_ma_chart, generate_macd_chart
        from backend_projeto.infrastructure.visualization.comprehensive_visualization import ComprehensiveVisualizer
        from backend_projeto.infrastructure.data_handling import YFinanceProvider

        asset = prices.columns[0]
        output_dir = "test_graficos"

        logging.info(f"  Gerando gráficos para {asset}...")

        # Testar gráfico de médias móveis
        ma_bytes = generate_price_with_ma_chart(prices, asset, windows=[5, 21])
        logging.info(f"  ✅ Gráfico de médias móveis gerado ({len(ma_bytes)} bytes)")

        # Testar gráfico MACD
        macd_bytes = generate_macd_chart(prices, asset, fast=12, slow=26, signal=9)
        logging.info(f"  ✅ Gráfico MACD gerado ({len(macd_bytes)} bytes)")

        # Testar visualizador completo
        visualizer = ComprehensiveVisualizer() # output_dir é passado no método ou config
        loader = YFinanceProvider()
        
        # Criando diretório se não existir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        generated_files = visualizer.generate_all_charts(
            assets=[asset],
            prices_df=prices, # Assumindo que aceita o DF direto, se não, teremos que ver a assinatura
            output_dir=output_dir
        )

        logging.info(f"  ✅ Visualizador executado: {len(generated_files)} arquivos")

        return True

    except Exception as e:
        logging.error(f"  ❌ Erro na geração de gráficos: {e}", exc_info=True)
        return False

def main():
    """Função principal."""
    logging.info("🚀 Teste específico de gráficos financeiros")
    logging.info("=" * 50)

    # Teste 1: Carregamento de dados
    if not test_data_loading():
        logging.error("\n❌ Problemas no carregamento de dados")
        return False

    # Teste 2: Análise técnica
    if not test_technical_analysis():
        logging.error("\n❌ Problemas na análise técnica")
        return False

    # Teste 3: Geração de gráficos
    if not test_chart_generation():
        logging.error("\n❌ Problemas na geração de gráficos")
        return False

    logging.info("\n✅ Todos os testes específicos passaram!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
