
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np


def create_oracle(n_qubits, marked_state):
    
    #Creates phase oracle that flips sign of |marked_state>
   # marked_state example: "101" for 3 qubits
  
    oracle = QuantumCircuit(n_qubits)

    # apply X gates where bit is 0
    for i, bit in enumerate(marked_state):
        if bit == "0":
            oracle.x(i)

    # multi-controlled Z
    oracle.h(n_qubits - 1)
    oracle.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    oracle.h(n_qubits - 1)

    # revert X gates
    for i, bit in enumerate(marked_state):
        if bit == "0":
            oracle.x(i)

    oracle.name = "Oracle"
    return oracle


def create_diffuser(n_qubits):
    ###Grover diffusion operator
    diffuser = QuantumCircuit(n_qubits)

    diffuser.h(range(n_qubits))
    diffuser.x(range(n_qubits))

    diffuser.h(n_qubits - 1)
    diffuser.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    diffuser.h(n_qubits - 1)

    diffuser.x(range(n_qubits))
    diffuser.h(range(n_qubits))

    diffuser.name = "Diffuser"
    return diffuser


def grover_circuit(n_qubits, marked_state):
   ## Builds full Grover circuit
    qc = QuantumCircuit(n_qubits, n_qubits)

    oracle = create_oracle(n_qubits, marked_state)
    diffuser = create_diffuser(n_qubits)

    # equal superposition
    qc.h(range(n_qubits))

    # optimal iterations
    iterations = int(np.floor(np.pi/4 * np.sqrt(2**n_qubits)))

    for _ in range(iterations):
        qc.append(oracle.to_gate(), range(n_qubits))
        qc.append(diffuser.to_gate(), range(n_qubits))

    qc.measure(range(n_qubits), range(n_qubits))

    return qc


def run_grover(n_qubits=3, marked_state="101", shots=1024):

    qc = grover_circuit(n_qubits, marked_state)

    simulator = AerSimulator()
    compiled = transpile(qc, simulator)

    result = simulator.run(compiled, shots=shots).result()
    counts = result.get_counts()

    print("\nResults:")
    print(counts)

    return qc, counts


if __name__ == "__main__":

    n_qubits = 3
    marked_state = "101"

    qc, counts = run_grover(n_qubits, marked_state)

    print("\nCircuit:")
    print(qc.draw())
