#!/usr/bin/env python3
"""
Script de diagnóstico simples para identificar problemas com geração de gráficos.
"""

import os
import sys
import traceback

# Adicionar o diretório raiz do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Testa se todas as importações necessárias funcionam."""
    print("🔍 Testando importações básicas...")

    try:
        import pandas as pd
        print("  ✅ pandas")
    except ImportError as e:
        print(f"  ❌ pandas: {e}")
        return False

    try:
        import numpy as np
        print("  ✅ numpy")
    except ImportError as e:
        print(f"  ❌ numpy: {e}")
        return False

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        print("  ✅ matplotlib")
    except ImportError as e:
        print(f"  ❌ matplotlib: {e}")
        return False

    return True

def test_project_imports():
    """Testa importações específicas do projeto."""
    print("\n🔍 Testando importações do projeto...")

    try:
        from src.backend_projeto.utils.config import Config
        config = Config()
        print("  ✅ Config")
    except Exception as e:
        print(f"  ❌ Config: {e}")
        return False

    try:
        from src.backend_projeto.core.data_handling import YFinanceProvider
        print("  ✅ YFinanceProvider")
    except Exception as e:
        print(f"  ❌ YFinanceProvider: {e}")
        return False

    try:
        from src.backend_projeto.core.visualizations.comprehensive_visualization import ComprehensiveVisualizer
        print("  ✅ ComprehensiveVisualizer")
    except Exception as e:
        print(f"  ❌ ComprehensiveVisualizer: {e}")
        traceback.print_exc()
        return False

    return True

def test_basic_functionality():
    """Testa funcionalidade básica de geração de gráficos."""
    print("\n🔍 Testando funcionalidade básica...")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Criar um gráfico simples
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
        ax.set_title("Teste Básico")

        # Salvar como bytes
        import io
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)

        # Salvar arquivo
        with open('teste_grafico.png', 'wb') as f:
            f.write(buf.read())

        print("  ✅ Gráfico básico criado com sucesso")
        return True

    except Exception as e:
        print(f"  ❌ Erro no gráfico básico: {e}")
        traceback.print_exc()
        return False

def main():
    """Função principal de diagnóstico."""
    print("🚀 Iniciando diagnóstico de geração de gráficos")
    print("=" * 50)

    # Teste 1: Importações básicas
    if not test_imports():
        print("\n❌ Problemas com importações básicas")
        return False

    # Teste 2: Importações do projeto
    if not test_project_imports():
        print("\n❌ Problemas com importações do projeto")
        return False

    # Teste 3: Funcionalidade básica
    if not test_basic_functionality():
        print("\n❌ Problemas com funcionalidade básica")
        return False

    print("\n✅ Todos os testes básicos passaram!")
    print("\n🔧 Possíveis problemas:")
    print("  - Dados financeiros indisponíveis (ativos inválidos)")
    print("  - Problemas de conectividade com APIs financeiras")
    print("  - Configurações de datas inválidas")
    print("  - Problemas específicos com funções de análise técnica")

    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)