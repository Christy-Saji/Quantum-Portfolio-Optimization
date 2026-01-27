import numpy as np
from typing import Tuple, Dict, Any


class IsingTransformer:
    def __init__(self, qubo_matrix: np.ndarray):
        self.qubo_matrix = np.array(qubo_matrix)
        self.n_qubits = qubo_matrix.shape[0]
        
        if self.qubo_matrix.shape[0] != self.qubo_matrix.shape[1]:
            raise ValueError("QUBO matrix must be square")
        
        self.h, self.J, self.offset = self._compute_ising_coefficients()
    
    def _compute_ising_coefficients(self) -> Tuple[np.ndarray, np.ndarray, float]:
        n, Q = self.n_qubits, self.qubo_matrix
        h, J, offset = np.zeros(n), np.zeros((n, n)), 0.0
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    offset += Q[i, i] / 2
                    h[i] -= Q[i, i] / 2
                else:
                    offset += Q[i, j] / 4
                    h[i] -= Q[i, j] / 4
                    h[j] -= Q[i, j] / 4
                    if i < j:
                        J[i, j] += Q[i, j] / 4
                    else:
                        J[j, i] += Q[i, j] / 4
        
        return h, J, offset
    
    def get_ising_dict(self) -> Tuple[Dict[int, float], Dict[Tuple[int, int], float], float]:
        h_dict = {i: float(self.h[i]) for i in range(self.n_qubits) if self.h[i] != 0}
        J_dict = {(i, j): float(self.J[i, j]) 
                  for i in range(self.n_qubits) 
                  for j in range(i + 1, self.n_qubits) 
                  if self.J[i, j] != 0}
        return h_dict, J_dict, float(self.offset)
    
    def evaluate_ising(self, z: np.ndarray) -> float:
        z = np.array(z)
        energy = self.offset + np.dot(self.h, z)
        for i in range(self.n_qubits):
            for j in range(i + 1, self.n_qubits):
                energy += self.J[i, j] * z[i] * z[j]
        return float(energy)
    
    def spin_to_binary(self, z: np.ndarray) -> np.ndarray:
        return ((1 - np.array(z)) / 2).astype(int)
    
    def binary_to_spin(self, x: np.ndarray) -> np.ndarray:
        return (1 - 2 * np.array(x)).astype(int)
    
    def get_hamiltonian_str(self) -> str:
        terms = []
        for i in range(self.n_qubits):
            if abs(self.h[i]) > 1e-10:
                terms.append(f"{self.h[i]:+.4f}*Z_{i}")
        for i in range(self.n_qubits):
            for j in range(i + 1, self.n_qubits):
                if abs(self.J[i, j]) > 1e-10:
                    terms.append(f"{self.J[i, j]:+.4f}*Z_{i}*Z_{j}")
        if abs(self.offset) > 1e-10:
            terms.append(f"{self.offset:+.4f}")
        return "H = " + " ".join(terms) if terms else "H = 0"
    
    def verify_transformation(self, num_samples: int = 10) -> Dict[str, Any]:
        np.random.seed(42)
        errors = []
        
        for _ in range(num_samples):
            x = np.random.randint(0, 2, self.n_qubits)
            z = self.binary_to_spin(x)
            
            qubo_energy = sum(self.qubo_matrix[i, j] * x[i] * x[j] 
                            for i in range(self.n_qubits) 
                            for j in range(self.n_qubits))
            ising_energy = self.evaluate_ising(z)
            errors.append(abs(qubo_energy - ising_energy))
        
        return {
            'verified': max(errors) < 1e-10,
            'max_error': max(errors),
            'mean_error': np.mean(errors),
            'num_samples': num_samples
        }
    
    def __repr__(self) -> str:
        return f"IsingTransformer(n_qubits={self.n_qubits}, offset={self.offset:.4f})"


def qubo_to_ising(qubo_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
    transformer = IsingTransformer(qubo_matrix)
    return transformer.h, transformer.J, transformer.offset
