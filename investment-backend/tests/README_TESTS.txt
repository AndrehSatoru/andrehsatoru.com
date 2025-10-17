# Estrutura de Testes do Projeto PUC FINANCE

## Visão Geral
Este documento detalha a estrutura de testes e as implementações necessárias para o projeto PUC FINANCE.

## Estrutura de Diretórios
/tests
  /api            # Testes da API REST
    test_api.py   # Testes dos endpoints da API
  /unit           # Testes unitários
    test_cache_manager.py  # Testes do gerenciador de cache

## Implementação Necessária da API (endpoints.py)

1. Endpoint: POST /analysis/run
   - Função: Receber arquivo Excel com transações e executar análise
   - Parâmetros: 
     * transactions_file: UploadFile (arquivo Excel)
   - Retornos:
     * 200: Análise concluída com sucesso
     * 422: Arquivo não fornecido
     * 400: Formato de arquivo inválido

Código necessário em endpoints.py:
```python
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Optional
import pandas as pd
from io import BytesIO
from core.analysis import PortfolioAnalyzer  # (implementar esta classe)

router = APIRouter()

@router.post("/analysis/run")
async def run_analysis(transactions_file: Optional[UploadFile] = File(None)):
    if not transactions_file:
        raise HTTPException(status_code=422, detail="No file uploaded")
    
    try:
        # Ler o arquivo Excel
        contents = await transactions_file.read()
        df = pd.read_excel(BytesIO(contents))
        
        # Validar o formato do arquivo
        required_columns = ['Data', 'Ativo', 'Tipo']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file format. Required columns: Data, Ativo, Tipo"
            )
        
        # Executar análise
        analyzer = PortfolioAnalyzer(df)
        results = analyzer.run_analysis()
        
        return {
            "status": "success",
            "message": "Analysis completed",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Estrutura dos Testes (test_api.py)

Os testes atuais verificam dois cenários principais:

1. test_run_analysis_endpoint:
   - Objetivo: Testar o upload bem-sucedido e processamento do arquivo
   - Entrada: Arquivo Excel válido com transações
   - Resultado esperado: Status 200 e resposta de sucesso

2. test_run_analysis_no_file:
   - Objetivo: Testar o comportamento quando nenhum arquivo é enviado
   - Entrada: Nenhum arquivo
   - Resultado esperado: Status 422 (Unprocessable Entity)

Testes adicionais recomendados:

3. test_run_analysis_invalid_format:
   ```python
   def test_run_analysis_invalid_format(dummy_invalid_excel):
       """
       Testa se o endpoint retorna erro 400 quando o arquivo tem formato inválido.
       """
       files = {
           "transactions_file": ("invalid.xlsx", dummy_invalid_excel, 
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
       }
       response = client.post("/analysis/run", files=files)
       assert response.status_code == 400
   ```

4. test_run_analysis_large_file:
   - Testar o comportamento com arquivos grandes
   - Verificar timeout e limites de memória

## Configuração do Ambiente de Testes

1. Fixtures necessárias:
   - dummy_excel_file: Cria arquivo Excel válido para testes
   - dummy_invalid_excel: Cria arquivo Excel com formato inválido
   - client: TestClient do FastAPI

2. Dependências:
   - pytest
   - pytest-asyncio (para testes assíncronos)
   - httpx (usado pelo TestClient)
   - pandas (para manipulação dos arquivos Excel)

## Como Executar os Testes

1. Configurar PYTHONPATH:
   ```powershell
   $env:PYTHONPATH = "caminho/do/projeto/src;caminho/do/projeto/src/backend_projeto"
   ```

2. Executar testes:
   ```powershell
   pytest tests/api/test_api.py -v
   ```

## Depuração de Falhas Comuns

1. Erro 404 (Not Found):
   - Verificar se o router está corretamente registrado em main.py
   - Confirmar se o endpoint está definido com o caminho correto

2. Erro de importação:
   - Verificar PYTHONPATH
   - Confirmar estrutura de diretórios
   - Verificar __init__.py nos diretórios necessários

3. Falha nos testes:
   - Verificar formato do arquivo Excel de teste
   - Confirmar se todas as dependências estão instaladas
   - Verificar logs de erro detalhados com -vv

## Próximos Passos

1. Implementar o endpoint conforme especificado
2. Adicionar mais casos de teste
3. Implementar validações adicionais no processamento do arquivo
4. Adicionar documentação com Swagger/OpenAPI
5. Implementar tratamento de erros mais detalhado