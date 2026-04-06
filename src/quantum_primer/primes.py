"""Quantum Primes — the 12 irreducible quantum computational primitives."""

from enum import Enum, auto
from dataclasses import dataclass


class QPrime(Enum):
    """The 12 quantum primes."""
    # Unitary (Q1-Q8)
    Q1 = "Superposition"
    Q2 = "Phase Encoding"
    Q3 = "Entanglement"
    Q4 = "Controlled Conditionality"
    Q5 = "Parameterized Rotation"
    Q6 = "Reflection"
    Q7 = "Basis Transformation"
    Q8 = "Hamiltonian Evolution"
    # Non-unitary (Q9-Q12)
    Q9 = "Measurement"
    Q10 = "Classical Feedback"
    Q11 = "Reset"
    Q12 = "Post-Selection"


class QStatus(Enum):
    """How well a hardware platform supports a prime."""
    NATIVE = auto()      # Directly available as a hardware gate
    COMPOSITE = auto()   # Requires decomposition into native gates
    UNAVAILABLE = auto() # Not supported


UNITARY_PRIMES = {QPrime.Q1, QPrime.Q2, QPrime.Q3, QPrime.Q4,
                  QPrime.Q5, QPrime.Q6, QPrime.Q7, QPrime.Q8}
NON_UNITARY_PRIMES = {QPrime.Q9, QPrime.Q10, QPrime.Q11, QPrime.Q12}


@dataclass
class QPrimeInfo:
    prime: QPrime
    symbol: str
    role: str
    classical_analog: str

QPRIME_DB = {
    QPrime.Q1:  QPrimeInfo(QPrime.Q1,  "H",         "Uniform amplitude spreading",       "P1 (Σ)"),
    QPrime.Q2:  QPrimeInfo(QPrime.Q2,  "Rz(θ)",     "Information → relative phases",     "P2 (×c)"),
    QPrime.Q3:  QPrimeInfo(QPrime.Q3,  "CNOT/CZ",   "Non-separable correlations",        "P11 (×)"),
    QPrime.Q4:  QPrimeInfo(QPrime.Q4,  "C-U",       "Operation gated by quantum state",  "P5 (argmax)"),
    QPrime.Q5:  QPrimeInfo(QPrime.Q5,  "Rx/Ry(θ)",  "Continuous tunable rotation",       "P6 (σ)"),
    QPrime.Q6:  QPrimeInfo(QPrime.Q6,  "2|ψ⟩⟨ψ|-I", "Inversion about subspace",         "P12 (1/x)"),
    QPrime.Q7:  QPrimeInfo(QPrime.Q7,  "QFT/H",     "Conjugate representation change",   "P3/P4 (eˣ/ln)"),
    QPrime.Q8:  QPrimeInfo(QPrime.Q8,  "e^{-iHt}",  "Continuous time evolution",         "P8 (∫)"),
    QPrime.Q9:  QPrimeInfo(QPrime.Q9,  "M",         "Projective collapse",               "P7 (θ)"),
    QPrime.Q10: QPrimeInfo(QPrime.Q10, "CF",        "Classical control of quantum ops",  "P9 (d/dt)"),
    QPrime.Q11: QPrimeInfo(QPrime.Q11, "|0⟩",      "Non-unitary re-initialization",     "P10 (ξ)"),
    QPrime.Q12: QPrimeInfo(QPrime.Q12, "PS",        "Conditional continuation",          "— (quantum-only)"),
}
