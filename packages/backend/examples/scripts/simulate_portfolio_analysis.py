#!/usr/bin/env python3
"""
Script para simular análise de portfólio com os ativos especificados.
"""

import requests
import json
import os
from datetime import datetime, timedelta
import time

# Configurações
BASE_URL = "http://localhost:8000"
OUTPUT_DIR = "portfolio_analysis_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Ativos especificados
ASSETS = [
    "EQTL3.SA", "CPFE3.SA", "EMBR3.SA", "DIRR3.SA", "LAVV3.SA", 
    "AZZA3.SA", "PRIO3.SA", "TFCO4.SA", "VAL", "SBSP3.SA", 
    "EQIX", "GE", "BA", "MC.PA", "ITX.MC", "NEE", "VALE3.SA", "AURA33.SA"
]

# Período de análise
START_DATE = "2022-01-01"
END_DATE = "2024-12-31"

def make_request(endpoint, data, output_file=None, content_type="image/png"):
    """Faz requisição para endpoint e salva resultado."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        print(f"[INFO] Fazendo requisição para: {endpoint}")
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        
        if output_file:
            file_path = os.path.join(OUTPUT_DIR, output_file)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"[OK] Salvo em: {file_path}")
        else:
            print(f"[OK] Resposta recebida: {len(response.content)} bytes")
        
        return response
    
    except requests.exceptions.RequestException as e:
        print(f"[ERRO] Erro na requisição: {e}")
        return None

def check_api_status():
    """Verifica se a API está rodando."""
    try:
        print("[INFO] Verificando API...")
        response = requests.get(f"{BASE_URL}/status", timeout=10)
        if response.status_code == 200:
            print("[OK] API está rodando!")
            return True
        else:
            print("[ERRO] API não está respondendo corretamente")
            return False
    except Exception as e:
        print(f"[ERRO] Erro ao conectar com API: {e}")
        return False

def generate_portfolio_dashboard():
    """Gera dashboard completo do portfólio."""
    print("\n" + "="*80)
    print("GERANDO DASHBOARD COMPLETO DO PORTFOLIO")
    print("="*80)
    
    print(f"Analisando {len(ASSETS)} ativos:")
    for i, asset in enumerate(ASSETS, 1):
        print(f"   {i:2d}. {asset}")
    
    # Dashboard de Portfólio Completo
    print("\n1. Dashboard de Portfólio Completo")
    make_request(
        "/plots/dashboard/portfolio",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "title": f"Análise Completa - {len(ASSETS)} Ativos",
            "benchmark": "^BVSP"
        },
        "portfolio_complete_dashboard.png"
    )
    
    # Dashboard de Risco
    print("\n2. Dashboard de Análise de Risco")
    make_request(
        "/plots/dashboard/risk",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "var_alpha": 0.95
        },
        "risk_analysis_dashboard.png"
    )
    
    # Dashboard de Performance
    print("\n3. Dashboard de Performance")
    make_request(
        "/plots/dashboard/performance",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "benchmark": "^BVSP"
        },
        "performance_dashboard.png"
    )

def generate_advanced_charts():
    """Gera gráficos avançados."""
    print("\n" + "="*80)
    print("📊 GERANDO GRÁFICOS AVANÇADOS")
    print("="*80)
    
    # Comparação de Preços
    print("\n📈 1. Comparação de Preços Normalizados")
    make_request(
        "/plots/advanced/price-comparison",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "normalize": True
        },
        "price_comparison_normalized.png"
    )
    
    # Métricas de Risco
    print("\n⚠️ 2. Métricas de Risco Comparativas")
    make_request(
        "/plots/advanced/risk-metrics",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE
        },
        "risk_metrics_comparison.png"
    )
    
    # Heatmap de Correlação
    print("\n🔥 3. Matriz de Correlação")
    make_request(
        "/plots/advanced/correlation-heatmap",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE
        },
        "correlation_heatmap.png"
    )
    
    # Distribuição de Retornos
    print("\n📊 4. Distribuição de Retornos")
    make_request(
        "/plots/advanced/return-distribution",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE
        },
        "return_distribution.png"
    )
    
    # Métricas de Performance
    print("\n🎯 5. Métricas de Performance")
    make_request(
        "/plots/advanced/performance-metrics",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "benchmark": "^BVSP"
        },
        "performance_metrics.png"
    )
    
    # Fronteira Eficiente Avançada
    print("\n🎯 6. Fronteira Eficiente Avançada")
    make_request(
        "/plots/advanced/efficient-frontier-advanced",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "n_portfolios": 5000
        },
        "efficient_frontier_advanced.png"
    )

def generate_interactive_charts():
    """Gera gráficos interativos."""
    print("\n" + "="*80)
    print("🎮 GERANDO GRÁFICOS INTERATIVOS")
    print("="*80)
    
    # Análise de Portfólio Interativa
    print("\n📈 1. Análise de Portfólio Interativa")
    make_request(
        "/plots/interactive/portfolio-analysis",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "benchmark": "^BVSP"
        },
        "interactive_portfolio_analysis.json",
        "application/json"
    )
    
    # Fronteira Eficiente Interativa
    print("\n🎯 2. Fronteira Eficiente Interativa")
    make_request(
        "/plots/interactive/efficient-frontier",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "n_portfolios": 5000
        },
        "interactive_efficient_frontier.json",
        "application/json"
    )
    
    # Métricas de Risco Interativas
    print("\n⚠️ 3. Métricas de Risco Interativas")
    make_request(
        "/plots/interactive/risk-metrics",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE
        },
        "interactive_risk_metrics.json",
        "application/json"
    )
    
    # Matriz de Correlação Interativa
    print("\n🔥 4. Matriz de Correlação Interativa")
    make_request(
        "/plots/interactive/correlation-matrix",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE
        },
        "interactive_correlation_matrix.json",
        "application/json"
    )

def generate_individual_analysis():
    """Gera análise individual para alguns ativos principais."""
    print("\n" + "="*80)
    print("🔍 ANÁLISE INDIVIDUAL DE ATIVOS PRINCIPAIS")
    print("="*80)
    
    # Selecionar alguns ativos principais para análise individual
    main_assets = ["VALE3.SA", "GE", "BA", "NEE", "EQIX"]
    
    for asset in main_assets:
        if asset in ASSETS:
            print(f"\n📊 Analisando {asset} individualmente...")
            
            # Candlestick Avançado
            make_request(
                "/plots/advanced/candlestick",
                {
                    "assets": [asset],
                    "start_date": START_DATE,
                    "end_date": END_DATE
                },
                f"candlestick_{asset.replace('.', '_')}.png"
            )
            
            # Q-Q Plot
            make_request(
                "/plots/advanced/qq-plot",
                {
                    "assets": [asset],
                    "start_date": START_DATE,
                    "end_date": END_DATE,
                    "asset": asset
                },
                f"qq_plot_{asset.replace('.', '_')}.png"
            )

def generate_monte_carlo_simulations():
    """Gera simulações Monte Carlo para ativos principais."""
    print("\n" + "="*80)
    print("🎲 SIMULAÇÕES MONTE CARLO")
    print("="*80)
    
    # Simulações para ativos principais
    main_assets = ["VALE3.SA", "GE", "BA", "NEE"]
    
    for asset in main_assets:
        if asset in ASSETS:
            print(f"\n🎲 Simulação Monte Carlo para {asset}...")
            make_request(
                "/plots/interactive/monte-carlo",
                {
                    "assets": [asset],
                    "start_date": START_DATE,
                    "end_date": END_DATE,
                    "asset": asset,
                    "n_simulations": 2000,
                    "n_days": 252
                },
                f"monte_carlo_{asset.replace('.', '_')}.json",
                "application/json"
            )

def main():
    """Função principal."""
    print("🚀 SIMULAÇÃO DE ANÁLISE DE PORTFÓLIO")
    print("="*80)
    print(f"📁 Diretório de saída: {OUTPUT_DIR}")
    print(f"🌐 URL base: {BASE_URL}")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total de ativos: {len(ASSETS)}")
    
    # Verificar API
    if not check_api_status():
        print("\n❌ API não está disponível. Certifique-se de que o servidor está rodando:")
        print("   uvicorn src.backend_projeto.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    try:
        # Executar todas as análises
        generate_portfolio_dashboard()
        generate_advanced_charts()
        generate_interactive_charts()
        generate_individual_analysis()
        generate_monte_carlo_simulations()
        
        print("\n" + "="*80)
        print("🎉 SIMULAÇÃO CONCLUÍDA!")
        print("="*80)
        print(f"📁 Arquivos gerados em: {OUTPUT_DIR}")
        print(f"📊 Total de ativos analisados: {len(ASSETS)}")
        print(f"⏰ Concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Listar arquivos gerados
        files = os.listdir(OUTPUT_DIR)
        print(f"\n📋 Arquivos gerados ({len(files)}):")
        for file in sorted(files):
            file_path = os.path.join(OUTPUT_DIR, file)
            size = os.path.getsize(file_path)
            print(f"   - {file} ({size:,} bytes)")
        
        # Resumo dos ativos
        print(f"\n📊 Ativos analisados:")
        for i, asset in enumerate(ASSETS, 1):
            print(f"   {i:2d}. {asset}")
        
        print(f"\n🎯 Tipos de análise gerados:")
        print(f"   - 3 Dashboards completos")
        print(f"   - 6 Gráficos avançados")
        print(f"   - 4 Gráficos interativos")
        print(f"   - Análise individual de ativos principais")
        print(f"   - Simulações Monte Carlo")
        
    except Exception as e:
        print(f"\n❌ Erro durante a simulação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
