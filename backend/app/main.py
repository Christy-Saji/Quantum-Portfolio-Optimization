"""
FastAPI Main Application

Entry point for the Quantum Portfolio Optimization API.

This API provides endpoints for:
- Listing available stocks
- Running QAOA portfolio optimization
- Retrieving stock metrics

The optimization uses Quantum Approximate Optimization Algorithm (QAOA)
running on a quantum simulator to select optimal portfolio stocks.
"""

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.routes import router
from app.models import HealthResponse


# Check quantum dependencies
def check_quantum_ready() -> bool:
    """Check if quantum computing dependencies are available."""
    try:
        from qiskit import QuantumCircuit
        from qiskit.primitives import StatevectorSampler
        return True
    except ImportError:
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("[START] Starting Quantum Portfolio Optimization API...")
    print(f"   Quantum ready: {check_quantum_ready()}")
    yield
    # Shutdown
    print("[STOP] Shutting down API...")



# Create FastAPI app
app = FastAPI(
    title="Quantum Portfolio Optimization API",
    description="""
    ## Overview
    
    This API provides quantum-powered portfolio optimization using the 
    **Quantum Approximate Optimization Algorithm (QAOA)**.
    
    ## Features
    
    - 📈 Select optimal stocks from NSE/BSE market
    - ⚛️ QAOA-based optimization on quantum simulator
    - 📊 Risk-return trade-off customization
    - 🔧 Configurable optimization parameters
    
    ## How It Works
    
    1. **Stock Selection**: Choose stocks to include in optimization
    2. **QUBO Formulation**: Problem is converted to QUBO format
    3. **Ising Mapping**: QUBO is mapped to Ising Hamiltonian
    4. **QAOA Optimization**: Quantum circuit finds optimal selection
    5. **Results**: Optimal portfolio with metrics is returned
    
    ## Technical Details
    
    - Runs on Qiskit AerSimulator (no quantum hardware required)
    - Supports circuit depth p = 1-3
    - Uses COBYLA classical optimizer
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get(
    "/",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns API health status"
)
async def health_check():
    """
    Health check endpoint.
    
    Returns the API status and version information.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        quantum_ready=check_quantum_ready()
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns API health status"
)
async def health():
    """Alternative health check endpoint."""
    return await health_check()


# Include API routes
app.include_router(router, prefix="/api", tags=["Portfolio Optimization"])


# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
