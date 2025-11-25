"""
This module defines FastAPI endpoints for processing financial transaction operations.

It provides a route to receive transaction data and execute portfolio analysis.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import pandas as pd
import logging
import traceback
from datetime import datetime, timedelta
from backend_projeto.domain.analysis import PortfolioAnalyzer
from backend_projeto.infrastructure.data_handling import YFinanceProvider
from backend_projeto.api.deps import get_loader

logger = logging.getLogger(__name__)

class Operacao(BaseModel):
    data: str
    ticker: str
    tipo: str
    valor: float

class Body(BaseModel):
    valorInicial: float
    dataInicial: str
    operacoes: List[Operacao]

router = APIRouter()

@router.post("/processar_operacoes")
async def processar_operacoes(
    body: Body,
    loader: YFinanceProvider = Depends(get_loader)
) -> dict:
    """
    Processes a list of financial operations and runs portfolio analysis.
    
    Fetches historical prices for each operation to calculate the correct quantity of shares.

    Args:
        body (Body): Request body containing initial investment, start date, and a list of operations.
        loader (YFinanceProvider): Data provider for fetching historical prices.

    Returns:
        dict: A dictionary with status, message, and complete analysis results.
    
    Raises:
        HTTPException: 400 if data format is invalid, 500 for processing errors.
    """
    try:
        # Converter operações para DataFrame no formato esperado pelo PortfolioAnalyzer
        # PortfolioAnalyzer espera colunas: Data, Ativo, Quantidade, Preco
        operations_data = []
        
        # Buscar preços históricos para cada operação
        for op in body.operacoes:
            try:
                # Buscar preço do ativo na data da operação
                # Adicionar 1 dia antes e depois para garantir que temos dados
                op_date = pd.to_datetime(op.data)
                start_date = (op_date - timedelta(days=5)).strftime('%Y-%m-%d')
                end_date = (op_date + timedelta(days=1)).strftime('%Y-%m-%d')
                
                # Buscar preços históricos
                prices_df = loader.fetch_stock_prices([op.ticker], start_date, end_date)
                
                # Pegar o preço mais próximo da data da operação
                if not prices_df.empty:
                    # Se prices_df for Series, converter para DataFrame
                    if isinstance(prices_df, pd.Series):
                        prices_df = prices_df.to_frame(name=op.ticker)
                    
                    # Encontrar o preço na data ou mais próximo
                    closest_date = prices_df.index[prices_df.index.get_indexer([op_date], method='nearest')[0]]
                    preco = prices_df.loc[closest_date, op.ticker] if op.ticker in prices_df.columns else prices_df.iloc[0, 0]
                    
                    # Calcular quantidade = valor / preço
                    quantidade = op.valor / preco
                    
                    logger.info(f"Operação {op.ticker} em {op.data}: valor={op.valor}, preço={preco:.2f}, quantidade={quantidade:.4f}")
                else:
                    # Se não encontrou preço, usar valor diretamente (quantidade = 1)
                    logger.warning(f"Não foi possível buscar preço para {op.ticker} em {op.data}. Usando valor como preço.")
                    preco = op.valor
                    quantidade = 1.0
                
            except Exception as e:
                # Se houver erro ao buscar preço, usar valor como preço (quantidade = 1)
                logger.warning(f"Erro ao buscar preço para {op.ticker} em {op.data}: {str(e)}. Usando valor como preço.")
                preco = op.valor
                quantidade = 1.0
            
            operations_data.append({
                'Data': op.data,
                'Ativo': op.ticker,
                'Quantidade': quantidade,
                'Preco': preco
            })
        
        df = pd.DataFrame(operations_data)
        
        # Executar análise completa com valor inicial e data inicial
        analyzer = PortfolioAnalyzer(
            df, 
            start_date=body.dataInicial,
            initial_value=body.valorInicial
        )
        results = analyzer.run_analysis()
        
        return {
            "status": "success",
            "message": "Análise executada com sucesso!",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar operações: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error(f"Data recebida - valorInicial: {body.valorInicial}, dataInicial: {body.dataInicial}, operacoes: {len(body.operacoes)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar operações: {str(e)}"
        )
