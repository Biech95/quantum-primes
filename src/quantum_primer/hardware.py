"""Hardware profiles — native gate sets and prime support per platform."""

from dataclasses import dataclass, field
from quantum_primer.primes import QPrime as Q, QStatus as S


@dataclass
class HardwareProfile:
    name: str
    description: str
    native_2q: str
    native_1q: list
    connectivity: str  # "all-to-all", "grid", "heavy-hex", "linear", "reconfigurable"
    prime_support: dict = field(default_factory=dict)  # QPrime → QStatus
    typical_2q_fidelity: float = 0.99


HARDWARE = {
    "ibm_heron": HardwareProfile(
        name="IBM Heron",
        description="156-qubit superconducting transmon, ECR/RZZ(θ) native, heavy-hex topology",
        native_2q="ECR / RZZ(θ)",
        native_1q=["Rz (virtual)", "SX", "X"],
        connectivity="heavy-hex",
        typical_2q_fidelity=0.998,
        prime_support={
            Q.Q1: S.NATIVE,       # SX ≈ √X gives superposition
            Q.Q2: S.NATIVE,       # Rz is virtual (free)
            Q.Q3: S.NATIVE,       # ECR / RZZ
            Q.Q4: S.COMPOSITE,    # ECR + 1Q gates
            Q.Q5: S.NATIVE,       # Rz, SX parameterized
            Q.Q6: S.COMPOSITE,    # Q1+Q2+Q3 composition
            Q.Q7: S.COMPOSITE,    # SX + Rz sequence
            Q.Q8: S.COMPOSITE,    # Trotter: repeated Q3+Q5
            Q.Q9: S.NATIVE,       # Measurement supported
            Q.Q10: S.NATIVE,      # Dynamic circuits
            Q.Q11: S.NATIVE,      # Mid-circuit reset
            Q.Q12: S.NATIVE,      # Dynamic circuits + conditional
        },
    ),
    "google_willow": HardwareProfile(
        name="Google Willow",
        description="105-qubit superconducting transmon, fSim(θ,φ) native, grid topology",
        native_2q="fSim(θ,φ) / √iSWAP",
        native_1q=["PhasedXZ(θ,φ)", "Rz (virtual)"],
        connectivity="grid",
        typical_2q_fidelity=0.995,
        prime_support={
            Q.Q1: S.NATIVE,       # PhasedXZ
            Q.Q2: S.NATIVE,       # Rz virtual + fSim phase
            Q.Q3: S.NATIVE,       # fSim
            Q.Q4: S.COMPOSITE,    # fSim + 1Q
            Q.Q5: S.NATIVE,       # PhasedXZ parameterized
            Q.Q6: S.COMPOSITE,    # Q1+Q2+Q3
            Q.Q7: S.NATIVE,       # PhasedXZ
            Q.Q8: S.NATIVE,       # fSim IS Hamiltonian evolution
            Q.Q9: S.NATIVE,
            Q.Q10: S.COMPOSITE,   # Limited dynamic circuits
            Q.Q11: S.COMPOSITE,   # Limited mid-circuit reset
            Q.Q12: S.COMPOSITE,
        },
    ),
    "ionq_forte": HardwareProfile(
        name="IonQ Forte",
        description="36 algorithmic qubits, trapped Yb-171 ions, XX(θ) native, all-to-all",
        native_2q="XX(θ) (Mølmer-Sørensen)",
        native_1q=["GPi(φ)", "GPi2(φ)", "Rz (virtual)"],
        connectivity="all-to-all",
        typical_2q_fidelity=0.995,
        prime_support={
            Q.Q1: S.NATIVE,       # GPi2
            Q.Q2: S.NATIVE,       # Rz virtual
            Q.Q3: S.NATIVE,       # XX(θ)
            Q.Q4: S.COMPOSITE,    # XX + 1Q
            Q.Q5: S.NATIVE,       # GPi, GPi2 parameterized
            Q.Q6: S.COMPOSITE,    # Q1+Q2+Q3
            Q.Q7: S.COMPOSITE,    # GPi2 + Rz
            Q.Q8: S.NATIVE,       # XX(θ) IS Hamiltonian evolution
            Q.Q9: S.NATIVE,
            Q.Q10: S.NATIVE,
            Q.Q11: S.NATIVE,
            Q.Q12: S.NATIVE,
        },
    ),
    "quantinuum_h2": HardwareProfile(
        name="Quantinuum H2",
        description="56-qubit trapped-ion QCCD, ZZPhase(θ) native, all-to-all via shuttling",
        native_2q="ZZPhase(θ)",
        native_1q=["U1q(θ,φ)", "Rz (virtual)"],
        connectivity="all-to-all",
        typical_2q_fidelity=0.999,
        prime_support={
            Q.Q1: S.NATIVE,       # U1q
            Q.Q2: S.NATIVE,       # Rz virtual
            Q.Q3: S.NATIVE,       # ZZPhase
            Q.Q4: S.COMPOSITE,    # ZZ + 1Q
            Q.Q5: S.NATIVE,       # U1q parameterized
            Q.Q6: S.COMPOSITE,    # Q1+Q2+Q3
            Q.Q7: S.COMPOSITE,    # U1q sequences
            Q.Q8: S.NATIVE,       # ZZPhase IS Hamiltonian evolution
            Q.Q9: S.NATIVE,
            Q.Q10: S.NATIVE,      # Full classical feedback
            Q.Q11: S.NATIVE,      # Mid-circuit reset
            Q.Q12: S.NATIVE,      # Mid-circuit measurement + conditional
        },
    ),
    "xanadu_photonic": HardwareProfile(
        name="Xanadu (Photonic)",
        description="Continuous-variable photonic, beam splitters + squeezing, measurement-based",
        native_2q="Beam splitter + Two-mode squeeze",
        native_1q=["Phase shift(φ)", "Displacement(α)"],
        connectivity="linear",
        typical_2q_fidelity=0.99,
        prime_support={
            Q.Q1: S.NATIVE,       # Beam splitter
            Q.Q2: S.NATIVE,       # Phase shift
            Q.Q3: S.NATIVE,       # Two-mode squeezing
            Q.Q4: S.COMPOSITE,    # KLM protocol
            Q.Q5: S.NATIVE,       # Phase(θ)
            Q.Q6: S.COMPOSITE,
            Q.Q7: S.NATIVE,       # BS network = unitary transform
            Q.Q8: S.NATIVE,       # Squeezing IS Hamiltonian evolution
            Q.Q9: S.NATIVE,       # Photon detection
            Q.Q10: S.COMPOSITE,
            Q.Q11: S.UNAVAILABLE, # Photons cannot be reset
            Q.Q12: S.NATIVE,      # Heralding
        },
    ),
    "neutral_atom": HardwareProfile(
        name="Neutral Atom (QuEra/Pasqal)",
        description="256+ qubits, Rydberg CZ native, reconfigurable topology, native multi-qubit gates",
        native_2q="CZ (Rydberg blockade)",
        native_1q=["Rx(θ) global", "Ry(θ) global", "Rz(θ) local"],
        connectivity="reconfigurable",
        typical_2q_fidelity=0.995,
        prime_support={
            Q.Q1: S.NATIVE,       # Rx global
            Q.Q2: S.NATIVE,       # Rz local
            Q.Q3: S.NATIVE,       # CZ Rydberg
            Q.Q4: S.NATIVE,       # CCZ native (multi-qubit blockade!)
            Q.Q5: S.NATIVE,       # Rx, Ry, Rz parameterized
            Q.Q6: S.COMPOSITE,
            Q.Q7: S.COMPOSITE,    # Rx + Rz
            Q.Q8: S.NATIVE,       # Rydberg Hamiltonian native
            Q.Q9: S.NATIVE,
            Q.Q10: S.COMPOSITE,
            Q.Q11: S.COMPOSITE,
            Q.Q12: S.COMPOSITE,
        },
    ),
}


def get_hardware(name: str) -> HardwareProfile:
    if name not in HARDWARE:
        available = ", ".join(HARDWARE.keys())
        raise ValueError(f"Unknown hardware '{name}'. Available: {available}")
    return HARDWARE[name]
