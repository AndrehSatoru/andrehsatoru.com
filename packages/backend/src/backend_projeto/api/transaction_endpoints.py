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
        
        # OTIMIZAÇÃO: Batch de tickers (Fase 1.2)
        if body.operacoes:
            # 1. Coletar todos os tickers únicos e range de datas
            all_tickers = list(set(op.ticker for op in body.operacoes))
            dates = [pd.to_datetime(op.data) for op in body.operacoes]
            if dates:
                min_date = min(dates) - timedelta(days=7) # Margem de 7 dias antes
                max_date = max(dates) + timedelta(days=7) # Margem de 7 dias depois
                
                start_date_str = min_date.strftime('%Y-%m-%d')
                end_date_str = max_date.strftime('%Y-%m-%d')
                
                logger.info(f"Buscando preços em batch para {len(all_tickers)} ativos entre {start_date_str} e {end_date_str}")
                
                # 2. Fetch único de preços para todos os ativos no range total
                try:
                    all_prices = loader.fetch_stock_prices(all_tickers, start_date_str, end_date_str)
                except Exception as e:
                    logger.error(f"Erro no fetch batch: {e}")
                    all_prices = pd.DataFrame()
            else:
                 all_prices = pd.DataFrame()
        else:
            all_prices = pd.DataFrame()

        # 3. Processar operações usando dados em memória
        for op in body.operacoes:
            try:
                op_date = pd.to_datetime(op.data)
                
                # Preço padrão (fallback)
                preco = op.valor
                quantidade = 1.0
                price_found = False
                
                if not all_prices.empty:
                    # Verificar se temos coluna para este ticker
                    # all_prices pode ter colunas com nomes originais ou normalizados
                    # Tentar encontrar a coluna correta
                    ticker_col = None
                    if op.ticker in all_prices.columns:
                        ticker_col = op.ticker
                    else:
                        # Tentar encontrar com .SA ou sem
                        possible_cols = [c for c in all_prices.columns if op.ticker in c or c in op.ticker]
                        if possible_cols:
                            ticker_col = possible_cols[0]
                    
                    if ticker_col:
                        # Filtrar preços para este ativo
                        ticker_prices = all_prices[ticker_col].dropna()
                        
                        if not ticker_prices.empty:
                            # Encontrar preço na data mais próxima
                            try:
                                # Usar get_indexer para busca eficiente
                                idx_loc = ticker_prices.index.get_indexer([op_date], method='nearest')[0]
                                if idx_loc != -1: # -1 significa não encontrado
                                    closest_date = ticker_prices.index[idx_loc]
                                    # Verificar se a data próxima é razoável (ex: dentro de 5 dias)
                                    if abs((closest_date - op_date).days) <= 5:
                                        preco = float(ticker_prices.iloc[idx_loc])
                                        quantidade = op.valor / preco
                                        price_found = True
                                        logger.info(f"Preço encontrado para {op.ticker} em {closest_date.date()} (req: {op.data}): {preco:.2f}")
                                    else:
                                        logger.warning(f"Data mais próxima para {op.ticker} ({closest_date.date()}) muito distante de {op.data}")
                            except Exception as e:
                                logger.warning(f"Erro ao buscar data próxima para {op.ticker}: {e}")
                    
                if not price_found:
                     logger.warning(f"Usando valor como preço para {op.ticker} em {op.data} (não encontrado no batch)")
                
            except Exception as e:
                logger.warning(f"Erro ao processar {op.ticker} em {op.data}: {str(e)}. Usando valor como preço.")
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
