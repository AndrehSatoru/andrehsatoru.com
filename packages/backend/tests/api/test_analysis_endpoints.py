import pytest
from fastapi.testclient import TestClient
import pandas as pd
from io import BytesIO

from backend_projeto.main import app 

client = TestClient(app)

@pytest.fixture
def dummy_excel_file():
    """
    Cria um arquivo Excel em memória para ser usado nos testes de upload.
    """
    df = pd.DataFrame({
        'Data': ['2024-01-05'],
        'Ativo': ['PETR4.SA'],
        'Quantidade': [100],
        'Preco': [100.00]
    })
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transacoes')
    output.seek(0)
    return output

def test_run_analysis_endpoint(dummy_excel_file):
    """
    Testa o endpoint de análise, enviando um arquivo de transações.
    """
    # Arrange
    files = {
        "transactions_file": ("Carteira_Teste.xlsx", dummy_excel_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    }

    # Act
    response = client.post("/api/v1/analysis/run", files=files)

    # Assert
    assert response.status_code == 200 # ou 202 se for uma task assíncrona
    
    response_json = response.json()
    assert "status" in response_json
    assert "message" in response_json
    assert response_json["status"] == "success"
    assert "Análise iniciada com sucesso" in response_json["message"]

def test_run_analysis_no_file():
    """
    Testa se o endpoint retorna um erro 422 se nenhum arquivo for enviado.
    """
    # Act
    response = client.post("/api/v1/analysis/run")

    # Assert
    assert response.status_code == 422 # Unprocessable Entity
