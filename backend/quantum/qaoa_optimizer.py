import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from scipy.optimize import minimize

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import SparsePauliOp
from qiskit_algorithms.minimum_eigensolvers import QAOA
from qiskit_algorithms.optimizers import COBYLA, SPSA

from .qubo import QUBOFormulator
from .ising import IsingTransformer


class QAOAPortfolioOptimizer:
    def __init__(self, returns: np.ndarray, covariance: np.ndarray, k: int,
                 lambda_param: float = 0.5, p: int = 1, penalty: Optional[float] = None):
        self.returns = np.array(returns)
        self.covariance = np.array(covariance)
        self.k = k
        self.n_stocks = len(returns)
        self.p = p
        self.lambda_param = lambda_param
        
        self.qubo = QUBOFormulator(returns, covariance, k, lambda_param, penalty)
        self.ising = IsingTransformer(self.qubo.build_qubo_matrix())
        
        self._optimal_params = None
        self._optimal_bitstring = None
        self._optimization_result = None
        
    def build_cost_hamiltonian(self) -> SparsePauliOp:
        n = self.n_stocks
        h, J = self.ising.h, self.ising.J
        pauli_list, coeffs = [], []
        
        if self.ising.offset != 0:
            pauli_list.append('I' * n)
            coeffs.append(self.ising.offset)
        
        for i in range(n):
            if h[i] != 0:
                pauli = ['I'] * n
                pauli[n - 1 - i] = 'Z'
                pauli_list.append(''.join(pauli))
                coeffs.append(h[i])
        
        for i in range(n):
            for j in range(i + 1, n):
                if J[i, j] != 0:
                    pauli = ['I'] * n
                    pauli[n - 1 - i] = 'Z'
                    pauli[n - 1 - j] = 'Z'
                    pauli_list.append(''.join(pauli))
                    coeffs.append(J[i, j])
        
        return SparsePauliOp(pauli_list, coeffs) if pauli_list else SparsePauliOp(['I' * n], [0.0])
    
    def create_qaoa_circuit(self, gamma: List[float], beta: List[float]) -> QuantumCircuit:
        n = self.n_stocks
        qc = QuantumCircuit(n)
        qc.h(range(n))
        
        for layer in range(self.p):
            self._apply_cost_unitary(qc, gamma[layer])
            self._apply_mixer_unitary(qc, beta[layer])
        
        qc.measure_all()
        return qc
    
    def _apply_cost_unitary(self, qc: QuantumCircuit, gamma: float) -> None:
        h, J, n = self.ising.h, self.ising.J, self.n_stocks
        
        for i in range(n):
            if h[i] != 0:
                qc.rz(2 * gamma * h[i], i)
        
        for i in range(n):
            for j in range(i + 1, n):
                if J[i, j] != 0:
                    qc.cx(i, j)
                    qc.rz(2 * gamma * J[i, j], j)
                    qc.cx(i, j)
    
    def _apply_mixer_unitary(self, qc: QuantumCircuit, beta: float) -> None:
        for i in range(self.n_stocks):
            qc.rx(2 * beta, i)
    
    def _evaluate_expectation(self, params: np.ndarray, shots: int = 1024) -> float:
        gamma, beta = params[:self.p], params[self.p:]
        qc = self.create_qaoa_circuit(list(gamma), list(beta))
        
        sampler = StatevectorSampler()
        result = sampler.run([qc], shots=shots).result()
        counts = result[0].data.meas.get_counts()
        
        total_cost, total_counts = 0.0, 0
        for bitstring, count in counts.items():
            x = np.array([int(b) for b in bitstring[::-1]])
            total_cost += self.qubo.evaluate(x) * count
            total_counts += count
        
        return total_cost / total_counts
    
    def optimize(self, method: str = 'COBYLA', maxiter: int = 100, 
                 shots: int = 1024, initial_params: Optional[np.ndarray] = None) -> Dict[str, Any]:
        if initial_params is None:
            np.random.seed(42)
            initial_params = np.random.uniform(0, np.pi, 2 * self.p)
        
        self._iteration_costs = []
        
        if method.upper() == 'COBYLA':
            result = minimize(
                lambda p: self._evaluate_expectation(p, shots),
                initial_params, method='COBYLA',
                options={'maxiter': maxiter, 'rhobeg': 0.5}
            )
        elif method.upper() == 'SPSA':
            optimizer = SPSA(maxiter=maxiter)
            result_params, result_value, _ = optimizer.minimize(
                lambda p: self._evaluate_expectation(p, shots), initial_params
            )
            result = type('Result', (), {
                'x': result_params, 'fun': result_value,
                'success': True, 'nit': maxiter
            })()
        else:
            raise ValueError(f"Unknown optimizer: {method}")
        
        self._optimal_params = result.x
        gamma_opt, beta_opt = result.x[:self.p], result.x[self.p:]
        
        final_qc = self.create_qaoa_circuit(list(gamma_opt), list(beta_opt))
        final_result = StatevectorSampler().run([final_qc], shots=shots * 4).result()
        final_counts = final_result[0].data.meas.get_counts()
        
        best_bitstring, best_cost = None, float('inf')
        for bitstring, count in final_counts.items():
            x = np.array([int(b) for b in bitstring[::-1]])
            cost = self.qubo.evaluate(x)
            if cost < best_cost:
                best_cost = cost
                best_bitstring = bitstring[::-1]
        
        self._optimal_bitstring = best_bitstring
        self._optimization_result = {
            'optimal_params': {'gamma': list(gamma_opt), 'beta': list(beta_opt)},
            'optimal_cost': best_cost,
            'optimal_bitstring': best_bitstring,
            'selected_indices': [i for i, b in enumerate(best_bitstring) if b == '1'],
            'convergence': result.success if hasattr(result, 'success') else True,
            'iterations': result.nit if hasattr(result, 'nit') else maxiter,
            'final_distribution': dict(final_counts),
            'iteration_costs': self._iteration_costs
        }
        return self._optimization_result
    
    def get_optimal_portfolio(self) -> Dict[str, Any]:
        if self._optimization_result is None:
            raise RuntimeError("Must run optimize() first")
        
        selected = self._optimization_result['selected_indices']
        x = np.zeros(self.n_stocks)
        x[selected] = 1
        
        portfolio_return = np.mean(self.returns[selected])
        weights = np.zeros(self.n_stocks)
        weights[selected] = 1.0 / len(selected)
        portfolio_variance = weights @ self.covariance @ weights
        portfolio_risk = np.sqrt(portfolio_variance)
        
        return {
            'selected_stocks': selected,
            'num_selected': len(selected),
            'expected_return': float(portfolio_return),
            'portfolio_risk': float(portfolio_risk),
            'sharpe_ratio': float(portfolio_return / portfolio_risk) if portfolio_risk > 0 else 0,
            'bitstring': self._optimal_bitstring
        }
    
    def get_circuit_info(self) -> Dict[str, Any]:
        qc = self.create_qaoa_circuit([0.5] * self.p, [0.5] * self.p)
        qc_no_meas = qc.remove_final_measurements(inplace=False)
        
        return {
            'num_qubits': qc.num_qubits,
            'depth': qc.depth(),
            'num_parameters': 2 * self.p,
            'gate_counts': dict(qc_no_meas.count_ops()),
            'circuit_layers': self.p
        }
    
    def __repr__(self) -> str:
        return f"QAOAPortfolioOptimizer(n_stocks={self.n_stocks}, k={self.k}, p={self.p}, λ={self.lambda_param})"


def run_qaoa_optimization(returns: np.ndarray, covariance: np.ndarray, k: int,
                          stock_names: Optional[List[str]] = None, lambda_param: float = 0.5,
                          p: int = 1, maxiter: int = 50, shots: int = 1024) -> Dict[str, Any]:
    optimizer = QAOAPortfolioOptimizer(returns, covariance, k, lambda_param, p)
    print(f"Running QAOA optimization (p={p}, k={k})...")
    result = optimizer.optimize(maxiter=maxiter, shots=shots)
    portfolio = optimizer.get_optimal_portfolio()
    
    if stock_names is not None:
        portfolio['selected_stock_names'] = [stock_names[i] for i in portfolio['selected_stocks']]
    
    circuit_info = optimizer.get_circuit_info()
    return {'optimization': result, 'portfolio': portfolio, 'circuit': circuit_info}


if __name__ == "__main__":
    from .qubo import create_sample_problem
    
    print("=== QAOA Portfolio Optimization Example ===\n")
    returns, covariance = create_sample_problem(n=4, k=2)
    stock_names = ['STOCK_A', 'STOCK_B', 'STOCK_C', 'STOCK_D']
    
    print("Stock Data:")
    print(f"  Expected Returns: {returns}")
    print(f"  Selecting k=2 stocks from n=4\n")
    
    result = run_qaoa_optimization(returns, covariance, k=2, stock_names=stock_names,
                                   lambda_param=0.5, p=1, maxiter=30, shots=512)
    
    print("\nResults:")
    print(f"  Selected Stocks: {result['portfolio']['selected_stock_names']}")
    print(f"  Expected Return: {result['portfolio']['expected_return']:.4f}")
    print(f"  Portfolio Risk: {result['portfolio']['portfolio_risk']:.4f}")
    print(f"  Sharpe Ratio: {result['portfolio']['sharpe_ratio']:.4f}")
    print(f"\nCircuit Info:")
    print(f"  Qubits: {result['circuit']['num_qubits']}")
    print(f"  Depth: {result['circuit']['depth']}")
    print(f"  Gates: {result['circuit']['gate_counts']}")
