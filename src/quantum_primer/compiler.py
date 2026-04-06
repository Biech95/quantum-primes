"""Quantum Prime Compiler — analyze quantum circuits via irreducible primitives."""

from __future__ import annotations
import json
from dataclasses import dataclass, field
from collections import Counter
from typing import Optional

from quantum_primer.primes import QPrime, QStatus, QPRIME_DB, UNITARY_PRIMES, NON_UNITARY_PRIMES
from quantum_primer.factorizations import get_gate_primes, GATE_TO_PRIMES
from quantum_primer.hardware import HardwareProfile, get_hardware, HARDWARE


@dataclass
class GateAnalysis:
    """Analysis of a single gate in the circuit."""
    name: str
    qubits: list
    primes: set = field(default_factory=set)
    support: QStatus = QStatus.NATIVE
    native_gate: str = ""


@dataclass
class CompilationReport:
    """Full compilation report for a quantum circuit."""
    circuit_name: str
    hardware_name: str
    num_qubits: int
    gates: list = field(default_factory=list)
    swap_count: int = 0

    @property
    def total_gates(self) -> int:
        return len([g for g in self.gates if g.primes])

    @property
    def native_gates(self) -> int:
        return len([g for g in self.gates if g.support == QStatus.NATIVE])

    @property
    def composite_gates(self) -> int:
        return len([g for g in self.gates if g.support == QStatus.COMPOSITE])

    @property
    def prime_histogram(self) -> dict:
        c = Counter()
        for g in self.gates:
            c.update(g.primes)
        return {p.value: count for p, count in c.most_common()}

    @property
    def native_coverage(self) -> float:
        total = self.total_gates
        if total == 0:
            return 1.0
        return self.native_gates / total

    @property
    def summary(self) -> str:
        total = self.total_gates
        native = self.native_gates
        composite = self.composite_gates
        noop = len(self.gates) - total

        lines = [
            f"═══ Quantum Prime Report: {self.circuit_name} ═══",
            f"Hardware: {self.hardware_name}",
            f"Qubits: {self.num_qubits}",
            f"",
            f"Gates: {total} compute + {noop} barrier/id = {len(self.gates)} total",
            f"  Native:    {native} ({native/max(total,1)*100:.0f}%)",
            f"  Composite: {composite} ({composite/max(total,1)*100:.0f}%)",
            f"  Native coverage: {self.native_coverage*100:.1f}%",
            f"",
            f"SWAPs needed: {self.swap_count}",
            f"  SWAP cost: {self.swap_count * 3} entangling gates",
            f"",
            f"Prime histogram:",
        ]
        for name, count in self.prime_histogram.items():
            lines.append(f"  {name:<25}: {count}")

        # Which primes are missing from hardware?
        all_primes = set()
        for g in self.gates:
            all_primes |= g.primes
        if all_primes:
            hw = get_hardware(self._hw_key) if hasattr(self, '_hw_key') else None
            if hw:
                composite_primes = [p for p in all_primes
                                   if hw.prime_support.get(p) == QStatus.COMPOSITE]
                if composite_primes:
                    lines.append(f"\nPrimes requiring decomposition on {hw.name}:")
                    for p in composite_primes:
                        info = QPRIME_DB[p]
                        lines.append(f"  {p.name}: {info.prime.value} ({info.symbol})")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "circuit": self.circuit_name,
            "hardware": self.hardware_name,
            "qubits": self.num_qubits,
            "total_gates": self.total_gates,
            "native_gates": self.native_gates,
            "composite_gates": self.composite_gates,
            "native_coverage": round(self.native_coverage, 4),
            "swap_count": self.swap_count,
            "swap_cost_entangling": self.swap_count * 3,
            "prime_histogram": self.prime_histogram,
            "gates": [
                {"name": g.name, "qubits": g.qubits,
                 "primes": [p.value for p in g.primes],
                 "support": g.support.name}
                for g in self.gates if g.primes
            ],
        }

    def to_json(self, indent=2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class QuantumPrimeCompiler:
    """Analyze quantum circuits via quantum prime decomposition."""

    def __init__(self, hardware: str | HardwareProfile = "ibm_heron"):
        if isinstance(hardware, str):
            self.hardware = get_hardware(hardware)
            self._hw_key = hardware
        else:
            self.hardware = hardware
            self._hw_key = hardware.name

    def compile(self, circuit, circuit_name: str = "") -> CompilationReport:
        """Compile a circuit (list of gate dicts or Qiskit QuantumCircuit)."""
        if not circuit_name:
            circuit_name = "circuit"

        # Try Qiskit QuantumCircuit
        if hasattr(circuit, 'data') and hasattr(circuit, 'num_qubits'):
            return self._compile_qiskit(circuit, circuit_name)

        # List of gate dicts: [{"gate": "h", "qubits": [0]}, ...]
        if isinstance(circuit, list):
            return self._compile_gatelist(circuit, circuit_name)

        raise TypeError(f"Expected QuantumCircuit or list of gate dicts, got {type(circuit)}")

    def _compile_qiskit(self, qc, name: str) -> CompilationReport:
        """Compile a Qiskit QuantumCircuit."""
        gates = []
        for instruction in qc.data:
            gate_name = instruction.operation.name
            qubits = [qc.find_bit(q).index for q in instruction.qubits]
            primes = get_gate_primes(gate_name)
            support = self._get_support(primes)
            gates.append(GateAnalysis(
                name=gate_name,
                qubits=qubits,
                primes=primes,
                support=support,
            ))

        swap_count = self._estimate_swaps(qc)

        report = CompilationReport(
            circuit_name=name,
            hardware_name=self.hardware.name,
            num_qubits=qc.num_qubits,
            gates=gates,
            swap_count=swap_count,
        )
        report._hw_key = self._hw_key
        return report

    def _compile_gatelist(self, gatelist: list, name: str) -> CompilationReport:
        """Compile from a list of gate dictionaries."""
        gates = []
        all_qubits = set()
        for gd in gatelist:
            gate_name = gd.get("gate", gd.get("name", "unknown"))
            qubits = gd.get("qubits", [])
            all_qubits.update(qubits)
            primes = get_gate_primes(gate_name)
            support = self._get_support(primes)
            gates.append(GateAnalysis(
                name=gate_name,
                qubits=qubits,
                primes=primes,
                support=support,
            ))

        report = CompilationReport(
            circuit_name=name,
            hardware_name=self.hardware.name,
            num_qubits=max(all_qubits) + 1 if all_qubits else 0,
            gates=gates,
            swap_count=0,
        )
        report._hw_key = self._hw_key
        return report

    def _get_support(self, primes: set) -> QStatus:
        """Determine hardware support level for a set of primes."""
        if not primes:
            return QStatus.NATIVE
        statuses = [self.hardware.prime_support.get(p, QStatus.COMPOSITE) for p in primes]
        if QStatus.UNAVAILABLE in statuses:
            return QStatus.UNAVAILABLE
        if QStatus.COMPOSITE in statuses:
            return QStatus.COMPOSITE
        return QStatus.NATIVE

    def _estimate_swaps(self, qc) -> int:
        """Estimate SWAP gates needed based on connectivity."""
        if self.hardware.connectivity == "all-to-all":
            return 0

        # Count 2-qubit gates between non-adjacent qubits
        # Simple heuristic: each 2Q gate on non-neighbors needs ~1 SWAP
        swap_estimate = 0
        for instruction in qc.data:
            qubits = [qc.find_bit(q).index for q in instruction.qubits]
            if len(qubits) >= 2:
                # Heuristic: distance-based estimate
                dist = abs(qubits[0] - qubits[1])
                if dist > 1:
                    swap_estimate += dist - 1

        return swap_estimate


def compile(circuit, hardware: str = "ibm_heron",
            circuit_name: str = "") -> CompilationReport:
    """Convenience function: analyze a quantum circuit via prime decomposition."""
    compiler = QuantumPrimeCompiler(hardware=hardware)
    return compiler.compile(circuit, circuit_name=circuit_name)
