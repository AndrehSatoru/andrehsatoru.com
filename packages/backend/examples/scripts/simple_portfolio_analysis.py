#!/usr/bin/env python3
"""
Script simplificado para análise de portfólio com os ativos especificados.
"""

import requests
import json
import os
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
OUTPUT_DIR = "portfolio_analysis_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Carregar ativos do arquivo JSON
ASSETS_FILE = os.path.join("portfolio_analysis_inputs", "ativos.json")
with open(ASSETS_FILE, 'r') as f:
    ASSETS = json.load(f)['assets']

# Período de análise
START_DATE = "2023-01-01"
END_DATE = "2024-12-31"

def make_request(endpoint, data, output_file=None):
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
    print("GERANDO GRAFICOS AVANCADOS")
    print("="*80)
    
    # Comparação de Preços
    print("\n1. Comparação de Preços Normalizados")
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
    print("\n2. Métricas de Risco Comparativas")
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
    print("\n3. Matriz de Correlação")
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
    print("\n4. Distribuição de Retornos")
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
    print("\n5. Métricas de Performance")
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
    print("\n6. Fronteira Eficiente Avançada")
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
    print("GERANDO GRAFICOS INTERATIVOS")
    print("="*80)
    
    # Análise de Portfólio Interativa
    print("\n1. Análise de Portfólio Interativa")
    make_request(
        "/plots/interactive/portfolio-analysis",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "benchmark": "^BVSP"
        },
        "interactive_portfolio_analysis.json"
    )
    
    # Fronteira Eficiente Interativa
    print("\n2. Fronteira Eficiente Interativa")
    make_request(
        "/plots/interactive/efficient-frontier",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE,
            "n_portfolios": 5000
        },
        "interactive_efficient_frontier.json"
    )
    
    # Métricas de Risco Interativas
    print("\n3. Métricas de Risco Interativas")
    make_request(
        "/plots/interactive/risk-metrics",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE
        },
        "interactive_risk_metrics.json"
    )
    
    # Matriz de Correlação Interativa
    print("\n4. Matriz de Correlação Interativa")
    make_request(
        "/plots/interactive/correlation-matrix",
        {
            "assets": ASSETS,
            "start_date": START_DATE,
            "end_date": END_DATE
        },
        "interactive_correlation_matrix.json"
    )

def main():
    """Função principal."""
    print("SIMULACAO DE ANALISE DE PORTFOLIO")
    print("="*80)
    print(f"Diretorio de saida: {OUTPUT_DIR}")
    print(f"URL base: {BASE_URL}")
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total de ativos: {len(ASSETS)}")
    
    # Verificar API
    if not check_api_status():
        print("\n[ERRO] API não está disponível. Certifique-se de que o servidor está rodando:")
        print("   uvicorn src.backend_projeto.main:app --reload --host 0.0.0.0 --port 8000")
        return
    
    try:
        # Executar todas as análises
        generate_portfolio_dashboard()
        generate_advanced_charts()
        generate_interactive_charts()
        
        print("\n" + "="*80)
        print("SIMULACAO CONCLUIDA!")
        print("="*80)
        print(f"Arquivos gerados em: {OUTPUT_DIR}")
        print(f"Total de ativos analisados: {len(ASSETS)}")
        print(f"Concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Listar arquivos gerados
        files = os.listdir(OUTPUT_DIR)
        print(f"\nArquivos gerados ({len(files)}):")
        for file in sorted(files):
            file_path = os.path.join(OUTPUT_DIR, file)
            size = os.path.getsize(file_path)
            print(f"   - {file} ({size:,} bytes)")
        
        # Resumo dos ativos
        print(f"\nAtivos analisados:")
        for i, asset in enumerate(ASSETS, 1):
            print(f"   {i:2d}. {asset}")
        
        print(f"\nTipos de análise gerados:")
        print(f"   - 3 Dashboards completos")
        print(f"   - 6 Gráficos avançados")
        print(f"   - 4 Gráficos interativos")
        
    except Exception as e:
        print(f"\n[ERRO] Erro durante a simulação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


