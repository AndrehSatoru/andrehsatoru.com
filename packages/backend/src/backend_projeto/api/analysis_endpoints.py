"""
This module defines FastAPI endpoints for portfolio analysis.

It provides an endpoint to run a comprehensive portfolio analysis based on
an uploaded transaction file, returning the analysis results.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Optional
import pandas as pd
from io import BytesIO
from backend_projeto.domain.analysis import PortfolioAnalyzer

router = APIRouter()

@router.post("/analysis/run")
async def run_analysis(transactions_file: Optional[UploadFile] = File(None)) -> dict:
    """
    Runs a portfolio analysis based on an uploaded transactions file.

    The uploaded file is expected to be an Excel file containing transaction data
    with required columns: 'Data', 'Ativo', 'Tipo'.

    Args:
        transactions_file (Optional[UploadFile]): The uploaded Excel file containing transaction data.

    Returns:
        dict: A dictionary containing the status, a success message, and the analysis results.

    Raises:
        HTTPException: 422 if no file is uploaded,
                       400 if the file format is invalid (missing required columns),
                       500 for internal server errors during processing.
    """
    if not transactions_file:
        raise HTTPException(status_code=422, detail="No file uploaded")
    
    try:
        # Ler o arquivo Excel
        contents = await transactions_file.read()
        df = pd.read_excel(BytesIO(contents))
        
        # Validar o formato do arquivo
        required_columns = ['Data', 'Ativo', 'Quantidade', 'Preco']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file format. Required columns: {', '.join(required_columns)}"
            )
        
        # Executar análise
        analyzer = PortfolioAnalyzer(df)
        results = analyzer.run_analysis()
        
        return {
            "status": "success",
            "message": "Análise iniciada com sucesso",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
