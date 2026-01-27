# Quantum Portfolio Optimization using QAOA

A simplified quantum computing project that optimizes stock portfolios from the Nifty 50 using the Quantum Approximate Optimization Algorithm (QAOA).

## What It Does

This application selects the optimal combination of stocks to maximize returns while minimizing risk. It formulates the problem as a Quadratic Unconstrained Binary Optimization (QUBO) problem and solves it using a simulated quantum circuit (QAOA).

## Project Structure

The project is designed to be simple and easy to explain, consisting of a lightweight backend and a clean frontend.

```
Quantum-Portfolio-Optimization/
├── backend/
│   ├── api.py          # Main Backend Server (FastAPI)
│   ├── stocks.py       # Stock Data Management (Real-time + Mock Fallback)
│   ├── qaoa.py         # Quantum Logic (QUBO setup, Ising formulation, QAOA circuit)
│   └── requirements.txt
├── frontend/
│   ├── index.html      # User Interface
│   ├── app.js          # Client-side Logic
│   └── styles.css      # Styling (Dark Theme)
└── run.py              # Startup Script
```

## How To Run

### 1. Install Dependencies
Open a terminal in the project folder and run:
```bash
pip install -r backend/requirements.txt
```

### 2. Start the App
Run the following command to start the backend server:
```bash
python run.py
```

### 3. Open the Frontend
Once the server is running, open the `frontend/index.html` file in your web browser.
(Or start a simple server `cd frontend && python -m http.server 3000` and go to `localhost:3000`).

## How It Works

1. **Stock Selection**: The user picks a set of stocks (e.g., RELIANCE, TCS).
2. **Data Fetching**: The app fetches live 2-year data from Yahoo Finance.
   - *Note: If the API is blocked or fails, the app automatically falls back to generating realistic synthetic data so the demo always works.*
3. **Mathematics**:
   - Calculates **Expected Returns** and **Covariance Matrix** (Risk).
   - Formulates a **QUBO Matrix** that balances high returns against high risk.
4. **Quantum Processing**:
   - Converts the QUBO into an **Ising Hamiltonian**.
   - Creates a **QAOA Quantum Circuit** using `qiskit`.
   - Simulates the circuit to find the bitstring (portfolio) with the lowest energy (best cost).
5. **Result**: Displays the selected stocks, optimal weights, and risk/return metrics.

## File Details for Presentation

- **run.py**: The entry point. It sets up the path and launches the Uvicorn server.
- **backend/api.py**: Defines the API endpoints (`/stocks`, `/optimize`). It receives requests from the frontend and coordinates the math and quantum solver.
- **backend/stocks.py**: Handles data. It attempts to download real stock prices. If that fails (e.g., due to network restrictions), it generates random walk data to ensure the project is demonstratable.
- **backend/qaoa.py**: The core "intelligent" part.
  - `build_qubo_matrix`: Converts finance data to a matrix.
  - `qubo_to_ising`: Prepares the matrix for the quantum solver.
  - `optimize_qaoa`: Runs the quantum simulation.

## Technologies Used

- **Python (FastAPI)**: Backend Logic.
- **Qiskit**: Quantum Computing Framework (IBM).
- **Pandas/NumPy**: Financial calculations.
- **HTML/JS**: Frontend UI.
- **Yahoo Finance (yfinance)**: Market data source.
