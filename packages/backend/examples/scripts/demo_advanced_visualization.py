#!/usr/bin/env python3
"""
Script de demonstração das novas funcionalidades de visualização avançada.
"""

import requests
import json
import os
from datetime import datetime, timedelta
import time

# Configurações
BASE_URL = "http://localhost:8000"
OUTPUT_DIR = "demo_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def make_request(endpoint, data, output_file=None, content_type="image/png"):
    """Faz requisição para endpoint e salva resultado."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        print(f"🔄 Fazendo requisição para: {endpoint}")
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        
        if output_file:
            file_path = os.path.join(OUTPUT_DIR, output_file)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Salvo em: {file_path}")
        else:
            print(f"✅ Resposta recebida: {len(response.content)} bytes")
        
        return response
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def demo_advanced_charts():
    """Demonstra gráficos avançados."""
    print("\n" + "="*60)
    print("🎨 DEMONSTRAÇÃO - GRÁFICOS AVANÇADOS")
    print("="*60)
    
    # Dados de exemplo
    assets = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
    start_date = "2023-01-01"
    end_date = "2024-12-31"
    
    # 1. Candlestick Avançado
    print("\n📊 1. Candlestick Avançado")
    make_request(
        "/plots/advanced/candlestick",
        {"assets": [assets[0]], "start_date": start_date, "end_date": end_date},
        "candlestick_advanced.png"
    )
    
    # 2. Comparação de Preços
    print("\n📈 2. Comparação de Preços")
    make_request(
        "/plots/advanced/price-comparison",
        {"assets": assets, "start_date": start_date, "end_date": end_date, "normalize": True},
        "price_comparison.png"
    )
    
    # 3. Métricas de Risco
    print("\n⚠️ 3. Métricas de Risco")
    make_request(
        "/plots/advanced/risk-metrics",
        {"assets": assets, "start_date": start_date, "end_date": end_date},
        "risk_metrics.png"
    )
    
    # 4. Heatmap de Correlação
    print("\n🔥 4. Heatmap de Correlação")
    make_request(
        "/plots/advanced/correlation-heatmap",
        {"assets": assets, "start_date": start_date, "end_date": end_date},
        "correlation_heatmap.png"
    )
    
    # 5. Distribuição de Retornos
    print("\n📊 5. Distribuição de Retornos")
    make_request(
        "/plots/advanced/return-distribution",
        {"assets": assets, "start_date": start_date, "end_date": end_date},
        "return_distribution.png"
    )
    
    # 6. Q-Q Plot
    print("\n📈 6. Q-Q Plot")
    make_request(
        "/plots/advanced/qq-plot",
        {"assets": assets, "start_date": start_date, "end_date": end_date, "asset": assets[0]},
        "qq_plot.png"
    )
    
    # 7. Métricas de Performance
    print("\n🎯 7. Métricas de Performance")
    make_request(
        "/plots/advanced/performance-metrics",
        {"assets": assets, "start_date": start_date, "end_date": end_date, "benchmark": "^BVSP"},
        "performance_metrics.png"
    )
    
    # 8. Fronteira Eficiente Avançada
    print("\n🎯 8. Fronteira Eficiente Avançada")
    make_request(
        "/plots/advanced/efficient-frontier-advanced",
        {"assets": assets, "start_date": start_date, "end_date": end_date, "n_portfolios": 2000},
        "efficient_frontier_advanced.png"
    )

def demo_dashboards():
    """Demonstra dashboards."""
    print("\n" + "="*60)
    print("🎛️ DEMONSTRAÇÃO - DASHBOARDS")
    print("="*60)
    
    assets = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA"]
    start_date = "2023-01-01"
    end_date = "2024-12-31"
    
    # 1. Dashboard de Portfólio
    print("\n📊 1. Dashboard de Portfólio")
    make_request(
        "/plots/dashboard/portfolio",
        {
            "assets": assets,
            "start_date": start_date,
            "end_date": end_date,
            "title": "Portfolio Analysis Dashboard",
            "benchmark": "^BVSP"
        },
        "portfolio_dashboard.png"
    )
    
    # 2. Dashboard de Risco
    print("\n⚠️ 2. Dashboard de Risco")
    make_request(
        "/plots/dashboard/risk",
        {
            "assets": assets,
            "start_date": start_date,
            "end_date": end_date,
            "var_alpha": 0.95
        },
        "risk_dashboard.png"
    )
    
    # 3. Dashboard de Performance
    print("\n🎯 3. Dashboard de Performance")
    make_request(
        "/plots/dashboard/performance",
        {
            "assets": assets,
            "start_date": start_date,
            "end_date": end_date,
            "benchmark": "^BVSP"
        },
        "performance_dashboard.png"
    )

def demo_interactive_charts():
    """Demonstra gráficos interativos."""
    print("\n" + "="*60)
    print("🎮 DEMONSTRAÇÃO - GRÁFICOS INTERATIVOS")
    print("="*60)
    
    assets = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
    start_date = "2023-01-01"
    end_date = "2024-12-31"
    
    # 1. Candlestick Interativo
    print("\n📊 1. Candlestick Interativo")
    make_request(
        "/plots/interactive/candlestick",
        {"assets": [assets[0]], "start_date": start_date, "end_date": end_date},
        "interactive_candlestick.json",
        "application/json"
    )
    
    # 2. Análise de Portfólio Interativa
    print("\n📈 2. Análise de Portfólio Interativa")
    make_request(
        "/plots/interactive/portfolio-analysis",
        {
            "assets": assets,
            "start_date": start_date,
            "end_date": end_date,
            "benchmark": "^BVSP"
        },
        "interactive_portfolio_analysis.json",
        "application/json"
    )
    
    # 3. Fronteira Eficiente Interativa
    print("\n🎯 3. Fronteira Eficiente Interativa")
    make_request(
        "/plots/interactive/efficient-frontier",
        {
            "assets": assets,
            "start_date": start_date,
            "end_date": end_date,
            "n_portfolios": 3000
        },
        "interactive_efficient_frontier.json",
        "application/json"
    )
    
    # 4. Métricas de Risco Interativas
    print("\n⚠️ 4. Métricas de Risco Interativas")
    make_request(
        "/plots/interactive/risk-metrics",
        {"assets": assets, "start_date": start_date, "end_date": end_date},
        "interactive_risk_metrics.json",
        "application/json"
    )
    
    # 5. Matriz de Correlação Interativa
    print("\n🔥 5. Matriz de Correlação Interativa")
    make_request(
        "/plots/interactive/correlation-matrix",
        {"assets": assets, "start_date": start_date, "end_date": end_date},
        "interactive_correlation_matrix.json",
        "application/json"
    )
    
    # 6. Simulação Monte Carlo Interativa
    print("\n🎲 6. Simulação Monte Carlo Interativa")
    make_request(
        "/plots/interactive/monte-carlo",
        {
            "assets": assets,
            "start_date": start_date,
            "end_date": end_date,
            "asset": assets[0],
            "n_simulations": 2000,
            "n_days": 252
        },
        "interactive_monte_carlo.json",
        "application/json"
    )

def demo_comprehensive_analysis():
    """Demonstra análise abrangente."""
    print("\n" + "="*60)
    print("🔍 DEMONSTRAÇÃO - ANÁLISE ABRANGENTE")
    print("="*60)
    
    # Análise completa com múltiplos ativos
    assets = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA"]
    start_date = "2023-01-01"
    end_date = "2024-12-31"
    
    print(f"\n📊 Analisando {len(assets)} ativos:")
    for asset in assets:
        print(f"   - {asset}")
    
    # Dashboard completo
    print("\n🎛️ Gerando Dashboard Completo...")
    make_request(
        "/plots/dashboard/portfolio",
        {
            "assets": assets,
            "start_date": start_date,
            "end_date": end_date,
            "title": f"Análise Completa - {len(assets)} Ativos",
            "benchmark": "^BVSP"
        },
        "comprehensive_analysis_dashboard.png"
    )
    
    # Análise interativa completa
    print("\n🎮 Gerando Análise Interativa Completa...")
    make_request(
        "/plots/interactive/portfolio-analysis",
        {
            "assets": assets,
            "start_date": start_date,
            "end_date": end_date,
            "benchmark": "^BVSP"
        },
        "comprehensive_interactive_analysis.json",
        "application/json"
    )

def main():
    """Função principal."""
    print("🚀 DEMONSTRAÇÃO DAS NOVAS FUNCIONALIDADES DE VISUALIZAÇÃO")
    print("="*80)
    print(f"📁 Diretório de saída: {OUTPUT_DIR}")
    print(f"🌐 URL base: {BASE_URL}")
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Verificar se a API está rodando
        print("\n🔍 Verificando API...")
        response = requests.get(f"{BASE_URL}/status", timeout=5)
        if response.status_code == 200:
            print("✅ API está rodando!")
        else:
            print("❌ API não está respondendo corretamente")
            return
        
        # Executar demonstrações
        demo_advanced_charts()
        demo_dashboards()
        demo_interactive_charts()
        demo_comprehensive_analysis()
        
        print("\n" + "="*80)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        print("="*80)
        print(f"📁 Arquivos gerados em: {OUTPUT_DIR}")
        print(f"📊 Total de gráficos: ~20")
        print(f"🎛️ Dashboards: 3")
        print(f"🎮 Gráficos interativos: 6")
        print(f"⏰ Concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Listar arquivos gerados
        files = os.listdir(OUTPUT_DIR)
        print(f"\n📋 Arquivos gerados ({len(files)}):")
        for file in sorted(files):
            file_path = os.path.join(OUTPUT_DIR, file)
            size = os.path.getsize(file_path)
            print(f"   - {file} ({size:,} bytes)")
        
    except Exception as e:
        print(f"\n❌ Erro durante a demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


