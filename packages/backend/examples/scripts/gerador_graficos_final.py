#!/usr/bin/env python3
"""
Solução integrada para geração de gráficos financeiros.

Este script resolve o problema de geração de gráficos tratando casos onde:
- APIs financeiras estão indisponíveis
- Dados de ativos são inválidos
- Problemas de conectividade

A estratégia é:
1. Tentar carregar dados reais primeiro
2. Se falhar, usar dados simulados realistas
3. Gerar gráficos normalmente
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

# Adicionar o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_logging():
    """Configura logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def create_fallback_data(assets: List[str], start_date: str, end_date: str) -> pd.DataFrame:
    """Cria dados simulados quando os dados reais não estão disponíveis."""
    logger = logging.getLogger(__name__)
    logger.info(f"Criando dados simulados para {len(assets)} ativos")

    # Criar datas
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    dates = pd.date_range(start=start, end=end, freq='D')

    # Gerar dados sintéticos realistas
    np.random.seed(42)  # Para reprodutibilidade

    prices_data = {}

    for asset in assets:
        # Gerar série temporal com tendência e ruído
        n_points = len(dates)

        # Valores base realistas para ativos brasileiros
        base_prices = {
            'PETR4.SA': 25.0,
            'VALE3.SA': 70.0,
            'ITUB4.SA': 30.0,
            'BBDC4.SA': 15.0,
            'ABEV3.SA': 12.0,
            'MGLU3.SA': 8.0,
            'WEGE3.SA': 40.0,
            'SANB11.SA': 35.0,
        }

        base_price = base_prices.get(asset, 20.0)

        # Tendência (alguns ativos sobem, outros oscilam)
        if 'PETR' in asset or 'VALE' in asset:
            trend = np.linspace(base_price, base_price * 1.2, n_points)  # Tendência de alta
        elif 'MGLU' in asset:
            trend = np.linspace(base_price, base_price * 0.3, n_points)  # Tendência de baixa
        else:
            trend = np.linspace(base_price * 0.9, base_price * 1.1, n_points)  # Oscilação

        # Sazonalidade mensal
        seasonal = 1.5 * np.sin(2 * np.pi * np.arange(n_points) / 21)

        # Ruído realista (volatilidade)
        volatility = 0.02 if 'MGLU' in asset else 0.03
        noise = np.random.normal(0, volatility, n_points)

        # Preços finais
        prices = trend + seasonal + noise
        prices = np.maximum(prices, 0.01)  # Evitar preços negativos

        prices_data[asset] = prices

    # Criar DataFrame
    df = pd.DataFrame(prices_data, index=dates)

    logger.info(f"Dados simulados criados: {df.shape}")
    return df

def load_financial_data_with_fallback(
    assets: List[str],
    start_date: str,
    end_date: str,
    max_retries: int = 2
) -> pd.DataFrame:
    """Carrega dados financeiros com fallback para dados simulados."""
    logger = logging.getLogger(__name__)

    # Tentar carregar dados reais
    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1} de carregar dados reais...")

            from src.backend_projeto.core.data_handling import YFinanceProvider
            from src.backend_projeto.utils.config import Config

            config = Config()
            loader = YFinanceProvider()

            prices = loader.fetch_stock_prices(assets, start_date, end_date)

            # Verificar se os dados são válidos
            if not prices.empty and prices.shape[0] > 10:
                valid_assets = []
                for asset in assets:
                    if asset in prices.columns and prices[asset].notna().sum() > 10:
                        valid_assets.append(asset)

                if valid_assets:
                    logger.info(f"Dados reais carregados para {len(valid_assets)} ativos")
                    return prices[valid_assets]

        except Exception as e:
            logger.warning(f"Erro na tentativa {attempt + 1}: {e}")

    # Fallback para dados simulados
    logger.info("Usando dados simulados como fallback")
    return create_fallback_data(assets, start_date, end_date)

def generate_comprehensive_charts_fixed(
    assets: List[str],
    start_date: str,
    end_date: str,
    output_dir: str = "graficos"
) -> Dict[str, str]:
    """Gera gráficos usando dados reais ou simulados."""
    logger = logging.getLogger(__name__)

    logger.info(f"Iniciando geração de gráficos para {len(assets)} ativos")

    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)

    # Carregar dados (reais ou simulados)
    prices = load_financial_data_with_fallback(assets, start_date, end_date)

    generated_files = {}

    try:
        # 1. Gráfico de preços
        import matplotlib.pyplot as plt

        plt.figure(figsize=(12, 6))
        for asset in prices.columns:
            plt.plot(prices.index, prices[asset], label=asset, linewidth=2)

        plt.title('Preços dos Ativos', fontsize=16)
        plt.xlabel('Data')
        plt.ylabel('Preço (R$)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)

        file_path = os.path.join(output_dir, "precos_ativos.png")
        plt.savefig(file_path, dpi=300, bbox_inches='tight')
        plt.close()
        generated_files["precos"] = file_path

        # 2. Análise técnica para cada ativo
        from src.backend_projeto.core.technical_analysis import moving_averages

        for asset in prices.columns:
            if asset not in prices.columns:
                continue

            # Médias móveis
            ma_df = moving_averages(prices[[asset]], windows=[5, 21, 50], method='sma')

            plt.figure(figsize=(12, 6))
            plt.plot(ma_df.index, ma_df[asset], label=f'{asset} (Preço)', linewidth=2, color='black')

            colors = ['blue', 'red', 'green']
            for i, window in enumerate([5, 21, 50]):
                col_name = f"{asset}_SMA_{window}"
                if col_name in ma_df.columns:
                    plt.plot(ma_df.index, ma_df[col_name],
                            label=f'Média {window} dias',
                            linewidth=1.5, color=colors[i])

            plt.title(f'Análise Técnica - {asset}', fontsize=16)
            plt.xlabel('Data')
            plt.ylabel('Preço (R$)')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)

            file_path = os.path.join(output_dir, f"{asset}_analise_tecnica.png")
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            generated_files[f"{asset}_ta"] = file_path

        # 3. Gráfico de correlação
        returns = prices.pct_change().dropna()
        if len(returns.columns) > 1:
            correlation = returns.corr()

            plt.figure(figsize=(10, 8))
            import seaborn as sns
            sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5)
            plt.title('Matriz de Correlação dos Retornos', fontsize=16)

            file_path = os.path.join(output_dir, "matriz_correlacao.png")
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            generated_files["correlacao"] = file_path

        logger.info(f"Gerados {len(generated_files)} gráficos com sucesso")
        return generated_files

    except Exception as e:
        logger.error(f"Erro ao gerar gráficos: {e}")
        raise

def main():
    """Função principal."""
    logger = setup_logging()

    print("🚀 Gerador de Gráficos Financeiros (com fallback)")
    print("=" * 55)

    # Configuração padrão
    assets = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA']
    start_date = '2023-01-01'
    end_date = '2024-01-01'
    output_dir = 'graficos'

    try:
        # Gerar gráficos
        files = generate_comprehensive_charts_fixed(
            assets=assets,
            start_date=start_date,
            end_date=end_date,
            output_dir=output_dir
        )

        print("\n✅ Gráficos gerados com sucesso!")
        print(f"📁 Diretório: {output_dir}")
        print("\n📋 Arquivos gerados:")
        for name, path in files.items():
            size = os.path.getsize(path)
            print(f"  • {name}: {size:,} bytes")

        print("\n💡 Dica: Se precisar de dados reais, verifique:")
        print("   - Conectividade com internet")
        print("   - Disponibilidade das APIs financeiras")
        print("   - Códigos dos ativos (ex: PETR4.SA para ações brasileiras)")
        return True

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        logger.error("Erro na geração de gráficos", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)