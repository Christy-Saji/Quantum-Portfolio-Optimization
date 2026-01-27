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
        if request.k > len(request.stocks):
            raise HTTPException(400, f"k ({request.k}) cannot exceed number of stocks ({len(request.stocks)})")
        
        prices = fetch_stock_data(request.stocks)
        returns, covariance = calculate_returns_and_cov(prices)
        
        result = optimize_qaoa(
            returns, covariance, request.k,
            lambda_param=request.lambda_param,
            p=request.p,
            maxiter=request.maxiter,
            shots=request.shots
        )
        
        selected_tickers = [request.stocks[i] for i in result['selected_indices']]
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
        for i, ticker in enumerate(request.stocks):
            stock_metrics[ticker] = {
                "expected_return": float(returns[i]),
                "volatility": float(np.sqrt(covariance[i, i])),
                "selected": i in result['selected_indices']
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
            "computation_time": time.time() - start_time
        }
    
    except Exception as e:
        raise HTTPException(500, f"Optimization failed: {str(e)}")


if __name__ == "__main__":
    print("Starting Quantum Portfolio Optimizer API...")
    print("API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
