import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import SparsePauliOp


def build_qubo_matrix(returns, covariance, k, lambda_param=0.5):
    n = len(returns)
    penalty = max(10.0, 2.0 * max(np.max(np.abs(covariance)), np.max(np.abs(returns))) * n)
    
    Q = np.zeros((n, n))
    for i in range(n):
        Q[i, i] = lambda_param * covariance[i, i] - (1 - lambda_param) * returns[i] + penalty * (1 - 2 * k)
    
    for i in range(n):
        for j in range(i + 1, n):
            Q[i, j] = 2.0 * (lambda_param * covariance[i, j] + penalty)
    
    return Q


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
    
    p = len(gamma)
    for layer in range(p):
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
    
    sampler = StatevectorSampler()
    result = sampler.run([qc], shots=shots).result()
    counts = result[0].data.meas.get_counts()
    
    total_cost, total_counts = 0.0, 0
    for bitstring, count in counts.items():
        x = np.array([int(b) for b in bitstring[::-1]])
        total_cost += (x @ Q @ x) * count
        total_counts += count
    
    return total_cost / total_counts


def optimize_qaoa(returns, covariance, k, lambda_param=0.5, p=1, maxiter=50, shots=1024):
    n = len(returns)
    
    Q = build_qubo_matrix(returns, covariance, k, lambda_param)
    h, J, offset = qubo_to_ising(Q)
    
    np.random.seed(42)
    initial_params = np.random.uniform(0, np.pi, 2 * p)
    
    print(f"Running QAOA optimization (p={p}, n={n}, k={k})...")
    result = minimize(
        lambda params: evaluate_cost(params, p, h, J, n, Q, shots),
        initial_params,
        method='COBYLA',
        options={'maxiter': maxiter}
    )
    
    gamma_opt, beta_opt = result.x[:p], result.x[p:]
    final_qc = create_qaoa_circuit(list(gamma_opt), list(beta_opt), h, J, n)
    final_result = StatevectorSampler().run([final_qc], shots=shots * 4).result()
    final_counts = final_result[0].data.meas.get_counts()
    
    best_bitstring, best_cost = None, float('inf')
    for bitstring, count in final_counts.items():
        x = np.array([int(b) for b in bitstring[::-1]])
        cost = x @ Q @ x
        if cost < best_cost:
            best_cost = cost
            best_bitstring = bitstring[::-1]
    
    selected_indices = [i for i, b in enumerate(best_bitstring) if b == '1']
    
    return {
        'selected_indices': selected_indices,
        'optimal_bitstring': best_bitstring,
        'optimal_cost': best_cost,
        'iterations': result.nit if hasattr(result, 'nit') else maxiter,
        'num_qubits': n,
        'qaoa_layers': p
    }
