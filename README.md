# Quantum Portfolio Optimization using QAOA

A simplified quantum computing project that optimizes stock portfolios using the Quantum Approximate Optimization Algorithm (QAOA).

## What It Does

Selects the best combination of stocks from Nifty 50 that maximizes returns while minimizing risk using quantum optimization.

## Project Structure

```
Quantum-Portfolio-Optimization/
├── backend/
│   ├── api.py          # FastAPI server with all endpoints
│   ├── stocks.py       # Nifty 50 stocks + Yahoo Finance data
│   ├── qaoa.py         # Quantum optimization (QUBO + Ising + QAOA)
│   └── requirements.txt
├── frontend/
│   ├── index.html      # UI
│   ├── app.js          # Frontend logic
│   └── styles.css      # Styling
└── run.py              # Main launcher script
```

## How To Run

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Start Backend Server
```bash
python run.py
```

### 3. Open Frontend
- Open `frontend/index.html` in your browser
- Or run: `python -m http.server 3000` from `frontend/` folder

### 4. Use The App
1. Select stocks from Nifty 50 (checkboxes)
2. Choose how many stocks to select (k slider)
3. Adjust risk preference (λ slider)
4. Click "Optimize Portfolio"
5. View results showing optimal stock selection

## How It Works

1. **QUBO Formulation**: Converts portfolio optimization into a Quadratic Unconstrained Binary Optimization problem
2. **Ising Transformation**: Transforms QUBO to Ising Hamiltonian for quantum computer
3. **QAOA**: Uses quantum circuits to find optimal solution
4. **Results**: Shows selected stocks, expected return, risk, and Sharpe ratio

## Technologies

- **Backend**: FastAPI (Python)
- **Quantum**: Qiskit (IBM Quantum SDK)
- **Data**: Yahoo Finance (live 2-year daily prices)
- **Frontend**: Vanilla HTML/CSS/JavaScript

## File Details

### Backend Files

- **api.py** (120 lines): FastAPI server with `/stocks` and `/optimize` endpoints
- **stocks.py** (80 lines): Nifty 50 list, yfinance data fetching, return/covariance calculation
- **qaoa.py** (145 lines): QUBO matrix, Ising transformation, QAOA quantum circuits

### Frontend Files

- **index.html**: Stock selection grid, configuration sliders, results display
- **app.js**: Stock loading, optimization API calls, UI updates
- **styles.css**: Modern dark theme with animations

## API Endpoints

- `GET /health` - Server health check
- `GET /api/stocks` - List all Nifty 50 stocks
- `POST /api/optimize` - Run QAOA portfolio optimization

## Requirements

```txt
fastapi==0.104.1
uvicorn==0.24.0
numpy==1.26.0
pandas==2.1.3
yfinance==0.2.32
qiskit==0.45.0
scipy==1.11.3
```

## Notes For Presentation

- **Simplified for teaching**: Only 3 backend files, easy to explain
- **Live data**: Uses real Yahoo Finance stock prices
- **Quantum concepts**: Demonstrates QUBO, Ising, QAOA circuit construction
- **Visual results**: Clear UI showing optimization output

---

**Created as college project demonstrating quantum computing for portfolio optimization**
