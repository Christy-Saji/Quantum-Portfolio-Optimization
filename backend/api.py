import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import numpy as np

from stocks import get_stock_list, fetch_stock_data, calculate_returns_and_cov
from qaoa import optimize_qaoa


app = FastAPI(title="Quantum Portfolio Optimizer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OptimizeRequest(BaseModel):
    stocks: List[str]
    k: int
    lambda_param: float = 0.5
    p: int = 1
    maxiter: int = 50
    shots: int = 1024


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0", "quantum_ready": True}


@app.get("/api/stocks")
def get_stocks():
    stocks = get_stock_list()
    return {"stocks": stocks, "count": len(stocks)}


@app.post("/api/optimize")
def optimize_portfolio(request: OptimizeRequest):
    start_time = time.time()
    
    try:
        # Practical limit for classical quantum simulators
        MAX_STOCKS = 20  # 2^20 = ~1 million states (manageable)
        
        if len(request.stocks) > MAX_STOCKS:
            raise HTTPException(
                400, 
                f"Too many stocks selected ({len(request.stocks)}). "
                f"Classical quantum simulators can only handle up to {MAX_STOCKS} stocks. "
                f"For larger portfolios, please use classical optimization methods or real quantum hardware."
            )
        
        if request.k > len(request.stocks):
            raise HTTPException(400, f"k ({request.k}) cannot exceed number of stocks ({len(request.stocks)})")
        
        prices, stock_status = fetch_stock_data(request.stocks)
        
        # Validate k against actual fetched stocks (not requested stocks)
        n_available = len(prices.columns)
        if n_available == 0:
            raise HTTPException(500, "No stock data could be fetched. Please try different stocks.")
        
        if request.k > n_available:
            failed_stocks = [s for s in request.stocks if s not in prices.columns]
            raise HTTPException(
                400, 
                f"k ({request.k}) exceeds available stocks ({n_available}). "
                f"Failed to fetch: {', '.join(failed_stocks)}. "
                f"Please reduce k to {n_available} or less, or select different stocks."
            )
        
        returns, covariance = calculate_returns_and_cov(prices)
        
        result = optimize_qaoa(
            returns, covariance, request.k,
            lambda_param=request.lambda_param,
            p=request.p,
            maxiter=request.maxiter,
            shots=request.shots
        )
        
        # Map selected indices to actual stock tickers (prices.columns, not request.stocks)
        actual_tickers = list(prices.columns)
        selected_tickers = [actual_tickers[i] for i in result['selected_indices']]
        n_selected = len(selected_tickers)
        weights = [1.0 / n_selected] * n_selected
        
        selected_returns = returns[result['selected_indices']]
        portfolio_return = np.mean(selected_returns)
        
        w = np.zeros(len(returns))
        w[result['selected_indices']] = 1.0 / n_selected
        portfolio_variance = w @ covariance @ w
        portfolio_risk = np.sqrt(portfolio_variance)
        sharpe = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
        
        stock_metrics = {}
        
        # Add metrics for successfully fetched stocks
        for i, ticker in enumerate(actual_tickers):
            stock_metrics[ticker] = {
                "expected_return": float(returns[i]),
                "volatility": float(np.sqrt(covariance[i, i])),
                "selected": ticker in selected_tickers,
                "status": stock_status.get(ticker, 'unknown')
            }
        
        # Add entries for failed stocks
        for ticker in request.stocks:
            if ticker not in stock_metrics:
                stock_metrics[ticker] = {
                    "expected_return": None,
                    "volatility": None,
                    "selected": False,
                    "status": stock_status.get(ticker, 'data_unavailable')
                }
        
        return {
            "success": True,
            "portfolio": {
                "selected_stocks": selected_tickers,
                "num_selected": n_selected,
                "expected_return": float(portfolio_return),
                "portfolio_risk": float(portfolio_risk),
                "sharpe_ratio": float(sharpe),
                "weights": weights
            },
            "qaoa_metrics": {
                "num_qubits": result['num_qubits'],
                "circuit_depth": result['qaoa_layers'] * 4,
                "qaoa_layers": result['qaoa_layers'],
                "iterations": result['iterations'],
                "optimal_cost": result['optimal_cost']
            },
            "stock_metrics": stock_metrics,
            "data_source": "mock_data" if all(s == 'mock_data' for s in stock_status.values()) else "yahoo_finance",
            "computation_time": time.time() - start_time
        }
    
    except Exception as e:
        raise HTTPException(500, f"Optimization failed: {str(e)}")


if __name__ == "__main__":
    print("Starting Quantum Portfolio Optimizer API...")
    print("API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
