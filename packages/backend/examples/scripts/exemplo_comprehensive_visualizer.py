#!/usr/bin/env python3
"""
Exemplo de uso do utilitário abrangente de geração de gráficos.

Este script demonstra como usar o ComprehensiveVisualizer para gerar
todos os tipos de gráficos disponíveis e salvá-los como arquivos PNG.
"""

import os
import sys
from datetime import datetime, timedelta

# Adicionar o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend_projeto.core.visualizations.comprehensive_visualization import ComprehensiveVisualizer, generate_comprehensive_charts
from src.backend_projeto.core.data_handling import YFinanceProvider as DataLoader
from src.backend_projeto.utils.config import Config


def exemplo_basico():
    """Exemplo básico de geração de gráficos."""
    print("=== Exemplo Básico de Geração de Gráficos ===")

    # Configuração
    assets = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA']
    start_date = '2023-01-01'
    end_date = '2024-01-01'
    output_dir = 'exemplo_graficos'

    # Inicializar componentes
    config = Config()
    loader = DataLoader(config=config)

    # Opção 1: Usando a classe ComprehensiveVisualizer
    print(f"Gerando gráficos para {len(assets)} ativos...")
    visualizer = ComprehensiveVisualizer(config=config, output_dir=output_dir)

    try:
        generated_files = visualizer.generate_all_charts(
            assets=assets,
            start_date=start_date,
            end_date=end_date,
            loader=loader
        )

        print(f"✅ {len(generated_files)} gráficos gerados com sucesso!")
        print("\nArquivos gerados:")
        for chart_name, filepath in generated_files.items():
            print(f"  - {chart_name}: {filepath}")

        # Listar arquivos gerados
        print(f"\nArquivos no diretório {output_dir}:")
        for filename in visualizer.list_generated_files():
            print(f"  - {filename}")

    except Exception as e:
        print(f"❌ Erro ao gerar gráficos: {e}")


def exemplo_configuracoes_personalizadas():
    """Exemplo com configurações personalizadas."""
    print("\n=== Exemplo com Configurações Personalizadas ===")

    assets = ['PETR4.SA']
    start_date = '2023-06-01'
    end_date = '2023-12-31'
    output_dir = 'exemplo_configurado'

    # Configurações personalizadas
    plot_configs = {
        'technical_analysis': {
            'ma_windows': [5, 10, 21, 50],
            'ma_method': 'ema',
            'macd_fast': 8,
            'macd_slow': 21,
            'macd_signal': 5
        },
        'fama_french': {
            'model': 'ff5',
            'rf_source': 'selic'
        },
        'efficient_frontier': {
            'n_samples': 10000,
            'rf': 0.02
        }
    }

    config = Config()
    loader = DataLoader(config=config)
    visualizer = ComprehensiveVisualizer(config=config, output_dir=output_dir)

    try:
        generated_files = visualizer.generate_all_charts(
            assets=assets,
            start_date=start_date,
            end_date=end_date,
            loader=loader,
            plot_configs=plot_configs
        )

        print(f"✅ {len(generated_files)} gráficos gerados com configurações personalizadas!")
        for chart_name, filepath in generated_files.items():
            print(f"  - {chart_name}: {filepath}")

    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_apenas_tipos_especificos():
    """Exemplo gerando apenas tipos específicos de gráficos."""
    print("\n=== Exemplo com Tipos Específicos de Gráficos ===")

    assets = ['PETR4.SA', 'VALE3.SA']
    start_date = '2023-01-01'
    end_date = '2024-01-01'

    # Gerar apenas gráficos de análise técnica
    chart_requests = [
        {
            'type': 'technical_analysis',
            'assets': ['PETR4.SA'],
            'start_date': start_date,
            'end_date': end_date,
            'plot_configs': {
                'technical_analysis': {
                    'ma_windows': [5, 21],
                    'ma_method': 'sma'
                }
            }
        },
        {
            'type': 'efficient_frontier',
            'assets': assets,
            'start_date': start_date,
            'end_date': end_date,
            'plot_configs': {
                'efficient_frontier': {
                    'n_samples': 3000,
                    'rf': 0.015
                }
            }
        }
    ]

    config = Config()
    loader = DataLoader(config=config)
    visualizer = ComprehensiveVisualizer(output_dir='exemplo_seletivo')

    try:
        all_files = visualizer.generate_batch_charts(chart_requests, loader)
        print(f"✅ {len(all_files)} gráficos gerados seletivamente!")
        for chart_name, filepath in all_files.items():
            print(f"  - {chart_name}: {filepath}")

    except Exception as e:
        print(f"❌ Erro: {e}")


def exemplo_limpeza():
    """Exemplo de limpeza de arquivos antigos."""
    print("\n=== Exemplo de Limpeza de Arquivos ===")

    visualizer = ComprehensiveVisualizer(output_dir='exemplo_graficos')

    # Listar arquivos antes da limpeza
    files_before = visualizer.list_generated_files()
    print(f"Arquivos antes da limpeza: {len(files_before)}")

    # Limpar arquivos com mais de 1 dia
    removed = visualizer.cleanup_old_files(days_old=1)
    print(f"Arquivos removidos: {removed}")

    # Listar arquivos após a limpeza
    files_after = visualizer.list_generated_files()
    print(f"Arquivos após a limpeza: {len(files_after)}")


def exemplo_api_endpoint():
    """Exemplo de como usar via API endpoint."""
    print("\n=== Exemplo de Uso via API ===")

    # Exemplo de requisição para o endpoint /plots/comprehensive
    exemplo_request = {
        "assets": ["PETR4.SA", "VALE3.SA", "ITUB4.SA"],
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "chart_types": ["technical_analysis", "fama_french", "efficient_frontier"],
        "output_dir": "api_generated_plots",
        "plot_configs": {
            "technical_analysis": {
                "ma_windows": [5, 21, 50],
                "ma_method": "ema"
            },
            "fama_french": {
                "model": "ff3",
                "rf_source": "selic"
            }
        }
    }

    print("Requisição de exemplo para o endpoint /plots/comprehensive:")
    print(f"POST /plots/comprehensive")
    print(f"Body: {exemplo_request}")

    # Em uma aplicação real, você faria:
    # import requests
    # response = requests.post("http://localhost:8000/plots/comprehensive", json=exemplo_request)
    # result = response.json()
    # print(f"Arquivos gerados: {result['generated_files']}")


if __name__ == "__main__":
    print("🚀 Utilitário Abrangente de Geração de Gráficos - Exemplos de Uso")
    print("=" * 70)

    # Executar exemplos (comente os que não quiser executar)
    exemplo_basico()
    exemplo_configuracoes_personalizadas()
    exemplo_apenas_tipos_especificos()
    exemplo_limpeza()
    exemplo_api_endpoint()

    print("\n" + "=" * 70)
    print("✅ Exemplos concluídos! Verifique os diretórios criados para ver os gráficos gerados.")
    print("\nPara usar na API, faça uma requisição POST para /plots/comprehensive")
    print("com os parâmetros mostrados no exemplo acima.")