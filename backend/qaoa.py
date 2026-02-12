import time
import numpy as np
from itertools import combinations
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import SparsePauliOp


<<<<<<< Updated upstream
def build_qubo_matrix(returns, covariance, k, lambda_param=0.5, sector_indices=None, max_per_sector=1):
    """Build the QUBO matrix for portfolio optimization."""
=======
def classical_brute_force(returns, covariance, k, lambda_param=0.5):
    """
    Classical brute-force solver: evaluates ALL C(n,k) combinations
    using the same QUBO matrix as QAOA for a fair comparison.
    """
    n = len(returns)
    Q = build_qubo_matrix(returns, covariance, k, lambda_param)

    start_time = time.time()

    best_cost = float('inf')
    best_indices = None
    total_combinations = 0

    for combo in combinations(range(n), k):
        x = np.zeros(n)
        for i in combo:
            x[i] = 1.0
        cost = x @ Q @ x
        total_combinations += 1
        if cost < best_cost:
            best_cost = cost
            best_indices = list(combo)

    elapsed = time.time() - start_time

    best_bitstring = ''.join('1' if i in best_indices else '0' for i in range(n))

    return {
        'selected_indices': best_indices,
        'optimal_bitstring': best_bitstring,
        'optimal_cost': float(best_cost),
        'total_combinations': total_combinations,
        'computation_time': elapsed
    }


def build_qubo_matrix(returns, covariance, k, lambda_param=0.5):
>>>>>>> Stashed changes
    n = len(returns)
    penalty = max(10.0, 2.0 * max(np.max(np.abs(covariance)), np.max(np.abs(returns))) * n)
    Q = np.zeros((n, n))

    # Diagonal: return + risk + cardinality constraint
    for i in range(n):
        Q[i, i] = lambda_param * covariance[i, i] - (1 - lambda_param) * returns[i] + penalty * (1 - 2 * k)

    # Off-diagonal: risk covariance + cardinality
    for i in range(n):
        for j in range(i + 1, n):
            Q[i, j] = 2.0 * (lambda_param * covariance[i, j] + penalty)

    # Sector diversification constraint (NOVEL CONTRIBUTION)
    if sector_indices:
        sector_penalty = penalty * 0.5
        for sector_name, indices in sector_indices.items():
            if len(indices) <= max_per_sector:
                continue
            m = max_per_sector
            for i in indices:
                Q[i, i] += sector_penalty * (1 - 2 * m)
            for idx_a in range(len(indices)):
                for idx_b in range(idx_a + 1, len(indices)):
                    i, j = indices[idx_a], indices[idx_b]
                    if i < j:
                        Q[i, j] += 2.0 * sector_penalty
                    else:
                        Q[j, i] += 2.0 * sector_penalty
    return Q


def classical_brute_force(returns, covariance, k, lambda_param=0.5, sector_indices=None, max_per_sector=1):
    """Evaluate ALL C(n,k) combinations using the same QUBO matrix as QAOA."""
    n = len(returns)
    Q = build_qubo_matrix(returns, covariance, k, lambda_param, sector_indices, max_per_sector)
    start_time = time.time()
    best_cost, best_indices, total = float('inf'), None, 0

    for combo in combinations(range(n), k):
        x = np.zeros(n)
        for i in combo:
            x[i] = 1.0
        cost = x @ Q @ x
        total += 1
        if cost < best_cost:
            best_cost = cost
            best_indices = list(combo)

    return {
        'selected_indices': best_indices,
        'optimal_bitstring': ''.join('1' if i in best_indices else '0' for i in range(n)),
        'optimal_cost': float(best_cost),
        'total_combinations': total,
        'computation_time': time.time() - start_time
    }


def qubo_to_ising(Q):
    n = Q.shape[0]
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


def build_cost_hamiltonian(h, J, n):
    pauli_list, coeffs = [], []
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


def create_qaoa_circuit(gamma, beta, h, J, n):
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for layer in range(len(gamma)):
        for i in range(n):
            if h[i] != 0:
                qc.rz(2 * gamma[layer] * h[i], i)
        for i in range(n):
            for j in range(i + 1, n):
                if J[i, j] != 0:
                    qc.cx(i, j)
                    qc.rz(2 * gamma[layer] * J[i, j], j)
                    qc.cx(i, j)
        for i in range(n):
            qc.rx(2 * beta[layer], i)
    qc.measure_all()
    return qc


def evaluate_cost(params, p, h, J, n, Q, shots=1024):
    gamma, beta = params[:p], params[p:]
    qc = create_qaoa_circuit(list(gamma), list(beta), h, J, n)
    result = StatevectorSampler().run([qc], shots=shots).result()
    counts = result[0].data.meas.get_counts()
    total_cost, total_counts = 0.0, 0
    for bitstring, count in counts.items():
        x = np.array([int(b) for b in bitstring[::-1]])
        total_cost += (x @ Q @ x) * count
        total_counts += count
    return total_cost / total_counts


def optimize_qaoa(returns, covariance, k, lambda_param=0.5, p=1, maxiter=50, shots=1024,
                  sector_indices=None, max_per_sector=1):
    n = len(returns)
    Q = build_qubo_matrix(returns, covariance, k, lambda_param, sector_indices, max_per_sector)
    h, J, offset = qubo_to_ising(Q)

    np.random.seed(42)
    initial_params = np.random.uniform(0, np.pi, 2 * p)

    print(f"Running QAOA (p={p}, n={n}, k={k}, sector_diversify={sector_indices is not None})...")
    result = minimize(
        lambda params: evaluate_cost(params, p, h, J, n, Q, shots),
        initial_params, method='COBYLA', options={'maxiter': maxiter}
    )

    gamma_opt, beta_opt = result.x[:p], result.x[p:]
    final_qc = create_qaoa_circuit(list(gamma_opt), list(beta_opt), h, J, n)
    final_counts = StatevectorSampler().run([final_qc], shots=shots * 4).result()[0].data.meas.get_counts()

    best_bitstring, best_cost = None, float('inf')
    for bitstring, count in final_counts.items():
        x = np.array([int(b) for b in bitstring[::-1]])
        cost = x @ Q @ x
        if cost < best_cost:
            best_cost = cost
            best_bitstring = bitstring[::-1]

    return {
        'selected_indices': [i for i, b in enumerate(best_bitstring) if b == '1'],
        'optimal_bitstring': best_bitstring,
        'optimal_cost': best_cost,
        'iterations': result.nit if hasattr(result, 'nit') else maxiter,
        'num_qubits': n,
        'qaoa_layers': p
    }
