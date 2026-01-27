"""
API Routes

Defines REST API endpoints for the portfolio optimization service.
"""

import time
from typing import List
from fastapi import APIRouter, HTTPException

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import (
    StockListResponse, StockInfo,
    OptimizationRequest, OptimizationResponse,
    PortfolioResult, QAOAMetrics, ErrorResponse
)
from data.stock_data import StockDataManager, calculate_portfolio_metrics
from quantum.qaoa_optimizer import QAOAPortfolioOptimizer


router = APIRouter()

# Initialize stock data manager
stock_manager = StockDataManager()


@router.get("/stocks", response_model=StockListResponse)
async def get_stocks():
    stocks = stock_manager.get_stock_list()
    return StockListResponse(
        stocks=[StockInfo(**stock) for stock in stocks],
        count=len(stocks)
    )


@router.get("/stocks/search")
async def search_stocks(query: str = "", limit: int = 50):
    results = stock_manager.search_stocks(query, limit)
    return {
        "stocks": results,
        "count": len(results),
        "query": query
    }


@router.post(
    "/optimize",
    response_model=OptimizationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Optimization failed"}
    },
    summary="Optimize portfolio using QAOA",
    description="Runs quantum optimization to select optimal stocks"
)
async def optimize_portfolio(request: OptimizationRequest):
    """
    Run QAOA portfolio optimization.
    
    This endpoint:
    1. Fetches historical data for requested stocks
    2. Computes expected returns and covariance
    3. Builds QUBO formulation
    4. Runs QAOA optimization
    5. Returns optimal portfolio selection
    
    The optimization uses a penalty-based approach to enforce
    the cardinality constraint (selecting exactly k stocks).
    """
    start_time = time.time()
    
    try:
        # Validate stocks exist
        available_tickers = [s['ticker'] for s in stock_manager.get_stock_list()]
        invalid_stocks = [s for s in request.stocks if s not in available_tickers]
        
        if invalid_stocks:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid stock tickers: {invalid_stocks}"
            )
        
        # Validate k constraint
        if request.k > len(request.stocks):
            raise HTTPException(
                status_code=400,
                detail=f"k ({request.k}) cannot exceed number of stocks ({len(request.stocks)})"
            )
        
        # Prepare optimization inputs
        returns, covariance, tickers = stock_manager.prepare_optimization_inputs(
            request.stocks
        )
        
        # Create QAOA optimizer
        optimizer = QAOAPortfolioOptimizer(
            returns=returns,
            covariance=covariance,
            k=request.k,
            lambda_param=request.lambda_param,
            p=request.p
        )
        
        # Run optimization
        result = optimizer.optimize(
            maxiter=request.maxiter,
            shots=request.shots
        )
        
        # Get portfolio details
        portfolio = optimizer.get_optimal_portfolio()
        selected_indices = portfolio['selected_stocks']
        selected_tickers = [tickers[i] for i in selected_indices]
        
        # Calculate portfolio metrics with equal weights
        n_selected = len(selected_indices)
        weights = [1.0 / n_selected] * n_selected
        
        # Get individual stock metrics
        stock_metrics = {}
        for i, ticker in enumerate(tickers):
            stock_metrics[ticker] = {
                "expected_return": float(returns[i]),
                "volatility": float(covariance[i, i] ** 0.5),
                "selected": i in selected_indices
            }
        
        # Get circuit info
        circuit_info = optimizer.get_circuit_info()
        
        computation_time = time.time() - start_time
        
        return OptimizationResponse(
            success=True,
            portfolio=PortfolioResult(
                selected_stocks=selected_tickers,
                num_selected=n_selected,
                expected_return=portfolio['expected_return'],
                portfolio_risk=portfolio['portfolio_risk'],
                sharpe_ratio=portfolio['sharpe_ratio'],
                weights=weights
            ),
            qaoa_metrics=QAOAMetrics(
                num_qubits=circuit_info['num_qubits'],
                circuit_depth=circuit_info['depth'],
                qaoa_layers=request.p,
                iterations=result['iterations'],
                optimal_cost=result['optimal_cost']
            ),
            stock_metrics=stock_metrics,
            computation_time=computation_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )


@router.get(
    "/stocks/{ticker}/metrics",
    summary="Get metrics for a specific stock",
    description="Returns historical metrics for a specific stock"
)
async def get_stock_metrics(ticker: str):
    """Get metrics for a specific stock."""
    available_tickers = [s['ticker'] for s in stock_manager.get_stock_list()]
    
    if ticker not in available_tickers:
        raise HTTPException(
            status_code=404,
            detail=f"Stock {ticker} not found"
        )
    
    # Fetch data for this stock
    stock_manager.fetch_data([ticker], use_cache=True)
    metrics = stock_manager.get_stock_metrics()
    
    return {
        "ticker": ticker,
        "expected_return": float(metrics.loc[ticker, 'Expected Return']),
        "volatility": float(metrics.loc[ticker, 'Volatility']),
        "sharpe_ratio": float(metrics.loc[ticker, 'Sharpe Ratio'])
    }
