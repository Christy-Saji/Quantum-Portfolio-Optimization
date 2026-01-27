"""
API Data Models

Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class StockInfo(BaseModel):
    """Stock information model."""
    ticker: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Full company name")
    sector: str = Field(..., description="Market sector")
    symbol: str = Field(..., description="Yahoo Finance symbol")


class StockListResponse(BaseModel):
    """Response model for stock list endpoint."""
    stocks: List[StockInfo] = Field(..., description="List of available stocks")
    count: int = Field(..., description="Number of stocks")


class OptimizationRequest(BaseModel):
    """Request model for portfolio optimization."""
    stocks: List[str] = Field(
        ...,
        min_length=3,
        max_length=15,
        description="List of stock tickers to include"
    )
    k: int = Field(
        ...,
        ge=2,
        le=10,
        description="Number of stocks to select"
    )
    lambda_param: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Risk aversion parameter (0=max return, 1=min risk)"
    )
    p: int = Field(
        default=1,
        ge=1,
        le=3,
        description="QAOA circuit depth"
    )
    maxiter: int = Field(
        default=50,
        ge=10,
        le=200,
        description="Maximum optimization iterations"
    )
    shots: int = Field(
        default=1024,
        ge=256,
        le=4096,
        description="Number of measurement shots"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "stocks": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"],
                "k": 3,
                "lambda_param": 0.5,
                "p": 1,
                "maxiter": 50,
                "shots": 1024
            }
        }


class PortfolioResult(BaseModel):
    """Portfolio optimization result."""
    selected_stocks: List[str] = Field(..., description="Selected stock tickers")
    num_selected: int = Field(..., description="Number of stocks selected")
    expected_return: float = Field(..., description="Expected annual return")
    portfolio_risk: float = Field(..., description="Portfolio risk (std dev)")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    weights: List[float] = Field(..., description="Stock weights")


class QAOAMetrics(BaseModel):
    """QAOA circuit and optimization metrics."""
    num_qubits: int = Field(..., description="Number of qubits used")
    circuit_depth: int = Field(..., description="Circuit depth")
    qaoa_layers: int = Field(..., description="QAOA p parameter")
    iterations: int = Field(..., description="Optimization iterations")
    optimal_cost: float = Field(..., description="Final optimization cost")


class OptimizationResponse(BaseModel):
    """Response model for optimization endpoint."""
    success: bool = Field(..., description="Whether optimization succeeded")
    portfolio: PortfolioResult = Field(..., description="Optimized portfolio")
    qaoa_metrics: QAOAMetrics = Field(..., description="QAOA performance metrics")
    stock_metrics: Dict[str, Dict[str, float]] = Field(
        ..., 
        description="Individual stock metrics"
    )
    computation_time: float = Field(..., description="Computation time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "portfolio": {
                    "selected_stocks": ["RELIANCE", "TCS", "INFY"],
                    "num_selected": 3,
                    "expected_return": 0.18,
                    "portfolio_risk": 0.22,
                    "sharpe_ratio": 0.82,
                    "weights": [0.333, 0.333, 0.334]
                },
                "qaoa_metrics": {
                    "num_qubits": 5,
                    "circuit_depth": 15,
                    "qaoa_layers": 1,
                    "iterations": 50,
                    "optimal_cost": -0.45
                },
                "stock_metrics": {
                    "RELIANCE": {"return": 0.15, "risk": 0.25},
                    "TCS": {"return": 0.18, "risk": 0.22}
                },
                "computation_time": 2.5
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error info")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    quantum_ready: bool = Field(..., description="Quantum simulator available")
