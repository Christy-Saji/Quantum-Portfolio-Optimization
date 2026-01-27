import numpy as np
from typing import Tuple, Optional


class QUBOFormulator:
    def __init__(self, returns: np.ndarray, covariance: np.ndarray, k: int,
                 lambda_param: float = 0.5, penalty: Optional[float] = None):
        self.returns = np.array(returns)
        self.covariance = np.array(covariance)
        self.n_stocks = len(returns)
        self.k = k
        self.lambda_param = lambda_param
        
        self._validate_inputs()
        self.penalty = penalty if penalty is not None else self._compute_optimal_penalty()
            
    def _validate_inputs(self) -> None:
        if self.n_stocks != self.covariance.shape[0]:
            raise ValueError(f"Returns length ({self.n_stocks}) must match covariance dimension ({self.covariance.shape[0]})")
        if self.covariance.shape[0] != self.covariance.shape[1]:
            raise ValueError("Covariance matrix must be square")
        if not 0 <= self.lambda_param <= 1:
            raise ValueError("lambda_param must be in [0, 1]")
        if self.k < 1 or self.k > self.n_stocks:
            raise ValueError(f"k must be in [1, {self.n_stocks}]")
            
    def _compute_optimal_penalty(self) -> float:
        risk_scale = np.max(np.abs(self.covariance))
        return_scale = np.max(np.abs(self.returns))
        max_scale = max(risk_scale, return_scale)
        return max(10.0, 2.0 * max_scale * self.n_stocks)
    
    def build_qubo_matrix(self) -> np.ndarray:
        n, λ, P, k = self.n_stocks, self.lambda_param, self.penalty, self.k
        Q = np.zeros((n, n))
        
        for i in range(n):
            Q[i, i] = λ * self.covariance[i, i] - (1 - λ) * self.returns[i] + P * (1 - 2 * k)
        
        for i in range(n):
            for j in range(i + 1, n):
                Q[i, j] = 2.0 * (λ * self.covariance[i, j] + P)
        
        return Q
    
    def build_symmetric_qubo(self) -> np.ndarray:
        Q = self.build_qubo_matrix()
        return (Q + Q.T) / 2
    
    def evaluate(self, x: np.ndarray) -> float:
        Q = self.build_qubo_matrix()
        x = np.array(x)
        return float(x @ Q @ x)
    
    def evaluate_components(self, x: np.ndarray) -> dict:
        x = np.array(x)
        risk = float(x @ self.covariance @ x)
        expected_return = float(self.returns @ x)
        selected = int(np.sum(x))
        constraint_violation = (selected - self.k) ** 2
        penalty_term = self.penalty * constraint_violation
        total = self.lambda_param * risk - (1 - self.lambda_param) * expected_return + penalty_term
        
        return {
            'risk': risk,
            'expected_return': expected_return,
            'selected_count': selected,
            'constraint_violation': constraint_violation,
            'penalty_term': penalty_term,
            'total_objective': total
        }
    
    def get_qubo_dict(self) -> dict:
        Q = self.build_qubo_matrix()
        return {(i, j): Q[i, j] for i in range(self.n_stocks) 
                for j in range(i, self.n_stocks) if Q[i, j] != 0}
    
    def __repr__(self) -> str:
        return f"QUBOFormulator(n_stocks={self.n_stocks}, k={self.k}, lambda={self.lambda_param}, penalty={self.penalty:.2f})"


def create_sample_problem(n: int = 5, k: int = 2) -> Tuple[np.ndarray, np.ndarray]:
    np.random.seed(42)
    returns = np.random.uniform(0.05, 0.25, n)
    
    correlations = np.random.uniform(-0.3, 0.7, (n, n))
    correlations = (correlations + correlations.T) / 2
    np.fill_diagonal(correlations, 1.0)
    
    eigenvalues, eigenvectors = np.linalg.eigh(correlations)
    eigenvalues = np.maximum(eigenvalues, 0.01)
    correlations = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T
    
    volatilities = np.random.uniform(0.1, 0.4, n)
    covariance = np.outer(volatilities, volatilities) * correlations
    
    return returns, covariance


if __name__ == "__main__":
    print("=== QUBO Formulation Example ===\n")
    
    returns, covariance = create_sample_problem(n=5, k=2)
    print("Expected Returns:")
    print(f"  {returns}\n")
    print("Covariance Matrix:")
    print(f"{covariance}\n")
    
    qubo = QUBOFormulator(returns, covariance, k=2, lambda_param=0.5)
    print(f"Formulator: {qubo}\n")
    
    Q = qubo.build_qubo_matrix()
    print("QUBO Matrix Q:")
    print(f"{Q}\n")
    
    test_solutions = [[1, 1, 0, 0, 0], [1, 0, 1, 0, 0], [1, 1, 1, 0, 0], [1, 0, 0, 0, 0]]
    
    print("Solution Evaluations:")
    for sol in test_solutions:
        result = qubo.evaluate_components(np.array(sol))
        print(f"  x = {sol}")
        print(f"    Selected: {result['selected_count']}, "
              f"Return: {result['expected_return']:.4f}, "
              f"Risk: {result['risk']:.4f}, "
              f"Penalty: {result['penalty_term']:.2f}, "
              f"Total: {result['total_objective']:.4f}")
