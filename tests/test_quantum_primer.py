"""Tests for the quantum prime compiler."""

from quantum_primer import compile, QuantumPrimeCompiler, QPrime, QStatus
from quantum_primer.primes import QPRIME_DB, UNITARY_PRIMES, NON_UNITARY_PRIMES
from quantum_primer.factorizations import get_gate_primes, ALGORITHM_FACTORIZATIONS
from quantum_primer.hardware import get_hardware, HARDWARE


# ── Prime definitions ──

def test_12_primes():
    assert len(QPrime) == 12

def test_8_unitary():
    assert len(UNITARY_PRIMES) == 8

def test_4_non_unitary():
    assert len(NON_UNITARY_PRIMES) == 4

def test_all_primes_have_info():
    for p in QPrime:
        assert p in QPRIME_DB


# ── Gate mapping ──

def test_hadamard_primes():
    primes = get_gate_primes("h")
    assert QPrime.Q1 in primes  # Superposition
    assert QPrime.Q7 in primes  # Basis transform

def test_cnot_primes():
    primes = get_gate_primes("cx")
    assert QPrime.Q3 in primes  # Entanglement
    assert QPrime.Q4 in primes  # Controlled

def test_rz_primes():
    primes = get_gate_primes("rz")
    assert QPrime.Q2 in primes  # Phase encoding

def test_measure_primes():
    primes = get_gate_primes("measure")
    assert QPrime.Q9 in primes  # Measurement

def test_barrier_no_primes():
    primes = get_gate_primes("barrier")
    assert len(primes) == 0


# ── Hardware profiles ──

def test_6_platforms():
    assert len(HARDWARE) == 6

def test_ionq_all_to_all():
    hw = get_hardware("ionq_forte")
    assert hw.connectivity == "all-to-all"

def test_ibm_heavy_hex():
    hw = get_hardware("ibm_heron")
    assert hw.connectivity == "heavy-hex"

def test_all_platforms_have_12_primes():
    for key, hw in HARDWARE.items():
        assert len(hw.prime_support) == 12, f"{key} has {len(hw.prime_support)} primes"

def test_quantinuum_highest_fidelity():
    hw = get_hardware("quantinuum_h2")
    assert hw.typical_2q_fidelity >= 0.999


# ── Algorithm factorizations ──

def test_15_algorithms():
    assert len(ALGORITHM_FACTORIZATIONS) == 15

def test_shor_has_qft():
    primes = ALGORITHM_FACTORIZATIONS["Shor"]
    assert QPrime.Q7 in primes  # Basis transform (QFT)

def test_grover_has_reflection():
    primes = ALGORITHM_FACTORIZATIONS["Grover"]
    assert QPrime.Q6 in primes  # Reflection

def test_vqe_has_feedback():
    primes = ALGORITHM_FACTORIZATIONS["VQE"]
    assert QPrime.Q10 in primes  # Classical feedback

def test_qec_has_reset():
    primes = ALGORITHM_FACTORIZATIONS["QEC"]
    assert QPrime.Q11 in primes  # Reset

def test_measurement_almost_universal():
    count = sum(1 for primes in ALGORITHM_FACTORIZATIONS.values() if QPrime.Q9 in primes)
    assert count >= 14  # 14 of 15


# ── Compilation from gate list ──

def test_compile_bell_pair():
    circuit = [
        {"gate": "h", "qubits": [0]},
        {"gate": "cx", "qubits": [0, 1]},
        {"gate": "measure", "qubits": [0]},
        {"gate": "measure", "qubits": [1]},
    ]
    report = compile(circuit, hardware="ionq_forte", circuit_name="Bell")
    assert report.num_qubits == 2
    assert report.total_gates == 4
    assert report.swap_count == 0  # All-to-all
    assert QPrime.Q1 in set().union(*(g.primes for g in report.gates))
    assert QPrime.Q3 in set().union(*(g.primes for g in report.gates))
    assert QPrime.Q9 in set().union(*(g.primes for g in report.gates))

def test_compile_ghz():
    circuit = [{"gate": "h", "qubits": [0]}]
    for i in range(1, 5):
        circuit.append({"gate": "cx", "qubits": [0, i]})
    report = compile(circuit, hardware="ibm_heron", circuit_name="GHZ-5")
    assert report.total_gates == 5
    print(report.summary)

def test_compile_qft():
    """A 4-qubit QFT circuit."""
    circuit = []
    n = 4
    for i in range(n):
        circuit.append({"gate": "h", "qubits": [i]})
        for j in range(i + 1, n):
            circuit.append({"gate": "cp", "qubits": [j, i]})
    for i in range(n // 2):
        circuit.append({"gate": "swap", "qubits": [i, n - 1 - i]})
    report = compile(circuit, hardware="google_willow", circuit_name="QFT-4")
    assert report.total_gates > 0
    print(report.summary)


# ── JSON output ──

def test_json_output():
    circuit = [
        {"gate": "h", "qubits": [0]},
        {"gate": "cx", "qubits": [0, 1]},
    ]
    report = compile(circuit, hardware="ibm_heron")
    j = report.to_json()
    import json
    d = json.loads(j)
    assert "circuit" in d
    assert "prime_histogram" in d


# ── Hardware comparison ──

def test_native_coverage_ionq_vs_ibm():
    circuit = [
        {"gate": "h", "qubits": [0]},
        {"gate": "cx", "qubits": [0, 1]},
        {"gate": "rz", "qubits": [0]},
        {"gate": "measure", "qubits": [0]},
    ]
    r_ionq = compile(circuit, hardware="ionq_forte")
    r_ibm = compile(circuit, hardware="ibm_heron")
    # Both should have reasonable coverage
    assert r_ionq.native_coverage > 0
    assert r_ibm.native_coverage > 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
