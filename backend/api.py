import time
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np

<<<<<<< Updated upstream
from stocks import get_stock_list, fetch_stock_data, calculate_returns_and_cov, NIFTY_50
from qaoa import optimize_qaoa, classical_brute_force
=======
from stocks import get_stock_list, fetch_stock_data, calculate_returns_and_cov
from qaoa import optimize_qaoa, classical_brute_force

>>>>>>> Stashed changes

app = FastAPI(title="Quantum Portfolio Optimizer")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class OptimizeRequest(BaseModel):
    stocks: List[str]
    k: int
    lambda_param: float = 0.5
    p: int = 1
    maxiter: int = 50
    shots: int = 1024
    sector_diversify: bool = False
    max_per_sector: int = 1


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0", "quantum_ready": True}


@app.get("/api/stocks")
def get_stocks():
    stocks = get_stock_list()
    return {"stocks": stocks, "count": len(stocks)}


def compute_portfolio_metrics(returns, covariance, selected_indices):
    """Compute return, risk, sharpe for a set of selected stock indices."""
    n_sel = len(selected_indices)
    sel_returns = returns[selected_indices]
    port_return = np.mean(sel_returns)
    w = np.zeros(len(returns))
    w[selected_indices] = 1.0 / n_sel
    port_risk = np.sqrt(w @ covariance @ w)
    sharpe = port_return / port_risk if port_risk > 0 else 0
    return float(port_return), float(port_risk), float(sharpe)


@app.post("/api/optimize")
def optimize_portfolio(request: OptimizeRequest):
    start_time = time.time()
    try:
        MAX_STOCKS = 20
        if len(request.stocks) > MAX_STOCKS:
            raise HTTPException(400, f"Too many stocks ({len(request.stocks)}). Max {MAX_STOCKS} for quantum simulation.")
        if request.k > len(request.stocks):
            raise HTTPException(400, f"k ({request.k}) cannot exceed number of stocks ({len(request.stocks)})")

        prices, stock_status = fetch_stock_data(request.stocks)
        n_available = len(prices.columns)
        if n_available == 0:
            raise HTTPException(500, "No stock data could be fetched. Please try different stocks.")
        if request.k > n_available:
            failed = [s for s in request.stocks if s not in prices.columns]
            raise HTTPException(400, f"k ({request.k}) exceeds available stocks ({n_available}). Failed: {', '.join(failed)}")

        returns, covariance = calculate_returns_and_cov(prices)
<<<<<<< Updated upstream
=======
        
        # --- Run Classical Brute-Force ---
        print("Running classical brute-force solver...")
        classical_start = time.time()
        classical_result = classical_brute_force(
            returns, covariance, request.k,
            lambda_param=request.lambda_param
        )
        classical_time = time.time() - classical_start
        
        # --- Run QAOA (Quantum) ---
        print("Running QAOA quantum solver...")
        qaoa_start = time.time()
        result = optimize_qaoa(
            returns, covariance, request.k,
            lambda_param=request.lambda_param,
            p=request.p,
            maxiter=request.maxiter,
            shots=request.shots
        )
        qaoa_time = time.time() - qaoa_start
        
        # Map selected indices to actual stock tickers (prices.columns, not request.stocks)
>>>>>>> Stashed changes
        actual_tickers = list(prices.columns)

        # Build sector index mapping if enabled
        sector_indices = None
        if request.sector_diversify:
            sector_map = {}
            for i, ticker in enumerate(actual_tickers):
                sector = NIFTY_50.get(ticker, {}).get('sector', 'Unknown')
                sector_map.setdefault(sector, []).append(i)
            sector_indices = sector_map

        # Run Classical Brute-Force
        classical_result = classical_brute_force(returns, covariance, request.k,
            lambda_param=request.lambda_param, sector_indices=sector_indices, max_per_sector=request.max_per_sector)

        # Run QAOA
        qaoa_start = time.time()
        result = optimize_qaoa(returns, covariance, request.k,
            lambda_param=request.lambda_param, p=request.p, maxiter=request.maxiter,
            shots=request.shots, sector_indices=sector_indices, max_per_sector=request.max_per_sector)
        qaoa_time = time.time() - qaoa_start

        selected_tickers = [actual_tickers[i] for i in result['selected_indices']]
        classical_tickers = [actual_tickers[i] for i in classical_result['selected_indices']]
<<<<<<< Updated upstream

        port_return, port_risk, sharpe = compute_portfolio_metrics(returns, covariance, result['selected_indices'])
        c_return, c_risk, c_sharpe = compute_portfolio_metrics(returns, covariance, classical_result['selected_indices'])

        results_match = set(result['selected_indices']) == set(classical_result['selected_indices'])

=======
        n_selected = len(selected_tickers)
        weights = [1.0 / n_selected] * n_selected
        
        selected_returns = returns[result['selected_indices']]
        portfolio_return = np.mean(selected_returns)
        
        w = np.zeros(len(returns))
        w[result['selected_indices']] = 1.0 / n_selected
        portfolio_variance = w @ covariance @ w
        portfolio_risk = np.sqrt(portfolio_variance)
        sharpe = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
        
        # Classical portfolio metrics
        classical_selected_returns = returns[classical_result['selected_indices']]
        classical_portfolio_return = np.mean(classical_selected_returns)
        w_classical = np.zeros(len(returns))
        n_classical = len(classical_result['selected_indices'])
        w_classical[classical_result['selected_indices']] = 1.0 / n_classical
        classical_portfolio_variance = w_classical @ covariance @ w_classical
        classical_portfolio_risk = np.sqrt(classical_portfolio_variance)
        classical_sharpe = classical_portfolio_return / classical_portfolio_risk if classical_portfolio_risk > 0 else 0
        
        # Check if both methods found the same solution
        results_match = set(result['selected_indices']) == set(classical_result['selected_indices'])
        
>>>>>>> Stashed changes
        stock_metrics = {}
        for i, ticker in enumerate(actual_tickers):
            stock_metrics[ticker] = {
                "expected_return": float(returns[i]),
                "volatility": float(np.sqrt(covariance[i, i])),
                "selected": ticker in selected_tickers,
                "sector": NIFTY_50.get(ticker, {}).get('sector', 'Unknown'),
                "status": stock_status.get(ticker, 'unknown')
            }
        for ticker in request.stocks:
            if ticker not in stock_metrics:
                stock_metrics[ticker] = {
                    "expected_return": None, "volatility": None, "selected": False,
                    "sector": NIFTY_50.get(ticker, {}).get('sector', 'Unknown'),
                    "status": stock_status.get(ticker, 'data_unavailable')
                }

        return {
            "success": True,
            "portfolio": {
                "selected_stocks": selected_tickers, "num_selected": len(selected_tickers),
                "expected_return": port_return, "portfolio_risk": port_risk, "sharpe_ratio": sharpe,
            },
            "qaoa_metrics": {
                "num_qubits": result['num_qubits'], "circuit_depth": result['qaoa_layers'] * 4,
                "qaoa_layers": result['qaoa_layers'], "iterations": result['iterations'],
                "optimal_cost": result['optimal_cost']
            },
            "comparison": {
                "classical": {
<<<<<<< Updated upstream
                    "selected_stocks": classical_tickers, "optimal_cost": classical_result['optimal_cost'],
                    "expected_return": c_return, "portfolio_risk": c_risk, "sharpe_ratio": c_sharpe,
                    "computation_time": round(classical_result['computation_time'], 4),
                    "combinations_evaluated": classical_result['total_combinations']
                },
                "qaoa": {
                    "selected_stocks": selected_tickers, "optimal_cost": result['optimal_cost'],
                    "expected_return": port_return, "portfolio_risk": port_risk, "sharpe_ratio": sharpe,
                    "computation_time": round(qaoa_time, 4), "qaoa_iterations": result['iterations']
                },
                "results_match": results_match
            },
            "sector_diversification": {
                "enabled": request.sector_diversify,
                "max_per_sector": request.max_per_sector if request.sector_diversify else None
=======
                    "selected_stocks": classical_tickers,
                    "optimal_cost": classical_result['optimal_cost'],
                    "expected_return": float(classical_portfolio_return),
                    "portfolio_risk": float(classical_portfolio_risk),
                    "sharpe_ratio": float(classical_sharpe),
                    "computation_time": round(classical_time, 4),
                    "combinations_evaluated": classical_result['total_combinations']
                },
                "qaoa": {
                    "selected_stocks": selected_tickers,
                    "optimal_cost": result['optimal_cost'],
                    "expected_return": float(portfolio_return),
                    "portfolio_risk": float(portfolio_risk),
                    "sharpe_ratio": float(sharpe),
                    "computation_time": round(qaoa_time, 4),
                    "qaoa_iterations": result['iterations']
                },
                "results_match": results_match,
                "speedup_factor": round(qaoa_time / classical_time, 2) if classical_time > 0 else None
>>>>>>> Stashed changes
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
