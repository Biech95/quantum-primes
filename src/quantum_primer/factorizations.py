"""Gate-to-prime mapping and algorithm factorizations."""

from quantum_primer.primes import QPrime as Q

# ── Gate → Prime mapping ──
# Maps standard gate names to the quantum prime(s) they realize.

GATE_TO_PRIMES = {
    # Single-qubit superposition / basis
    "h":        {Q.Q1, Q.Q7},
    "hadamard":  {Q.Q1, Q.Q7},

    # Phase / Z-rotations
    "rz":       {Q.Q2},
    "p":        {Q.Q2},
    "phase":    {Q.Q2},
    "s":        {Q.Q2},
    "sdg":      {Q.Q2},
    "t":        {Q.Q2},
    "tdg":      {Q.Q2},
    "z":        {Q.Q2},
    "u1":       {Q.Q2},

    # Parameterized rotations (amplitude-changing)
    "rx":       {Q.Q5},
    "ry":       {Q.Q5},
    "u2":       {Q.Q5, Q.Q2},
    "u3":       {Q.Q5, Q.Q2},
    "u":        {Q.Q5, Q.Q2},
    "sx":       {Q.Q5},
    "sxdg":     {Q.Q5},
    "x":        {Q.Q5},
    "y":        {Q.Q5},

    # Entangling gates
    "cx":       {Q.Q3, Q.Q4},
    "cnot":     {Q.Q3, Q.Q4},
    "cz":       {Q.Q3, Q.Q4},
    "cy":       {Q.Q3, Q.Q4},
    "ecr":      {Q.Q3},
    "iswap":    {Q.Q3},
    "swap":     {Q.Q3},
    "dcx":      {Q.Q3, Q.Q4},
    "xx":       {Q.Q3},
    "yy":       {Q.Q3},
    "zz":       {Q.Q3},
    "rzz":      {Q.Q3, Q.Q2},
    "rxx":      {Q.Q3, Q.Q5},
    "ryy":      {Q.Q3, Q.Q5},
    "xx_plus_yy": {Q.Q3, Q.Q5},
    "fsim":     {Q.Q3, Q.Q2},
    "sycamore": {Q.Q3, Q.Q2},
    "ms":       {Q.Q3, Q.Q5},  # Mølmer-Sørensen

    # Multi-qubit controlled
    "ccx":      {Q.Q3, Q.Q4},
    "toffoli":  {Q.Q3, Q.Q4},
    "ccz":      {Q.Q3, Q.Q4},
    "cswap":    {Q.Q3, Q.Q4},
    "fredkin":  {Q.Q3, Q.Q4},
    "mcx":      {Q.Q3, Q.Q4},
    "mcp":      {Q.Q3, Q.Q4, Q.Q2},

    # Controlled rotations
    "crx":      {Q.Q4, Q.Q5},
    "cry":      {Q.Q4, Q.Q5},
    "crz":      {Q.Q4, Q.Q2},
    "cp":       {Q.Q4, Q.Q2},
    "cu":       {Q.Q4, Q.Q5, Q.Q2},

    # Measurement
    "measure":      {Q.Q9},
    "measurement":  {Q.Q9},

    # Reset
    "reset":    {Q.Q11},

    # Barriers / identity (no prime)
    "barrier":  set(),
    "id":       set(),
    "delay":    set(),
    "nop":      set(),
}


def get_gate_primes(gate_name: str) -> set:
    """Look up which quantum primes a gate realizes."""
    clean = gate_name.lower().replace("gate", "").replace("_", "").strip()
    # Exact match
    if clean in GATE_TO_PRIMES:
        return GATE_TO_PRIMES[clean]
    # Substring match
    for key, primes in GATE_TO_PRIMES.items():
        if key in clean or clean in key:
            return primes
    return set()


# ── Algorithm factorizations ──
# Each: (name, set of primes used)

ALGORITHM_FACTORIZATIONS = {
    "Shor":              {Q.Q1, Q.Q2, Q.Q4, Q.Q7, Q.Q9},
    "Grover":            {Q.Q1, Q.Q2, Q.Q6, Q.Q7, Q.Q9},
    "VQE":               {Q.Q3, Q.Q5, Q.Q7, Q.Q8, Q.Q9, Q.Q10},
    "QAOA":              {Q.Q1, Q.Q2, Q.Q5, Q.Q8, Q.Q9, Q.Q10},
    "QPE":               {Q.Q1, Q.Q2, Q.Q4, Q.Q7, Q.Q9},
    "HHL":               {Q.Q2, Q.Q4, Q.Q5, Q.Q7, Q.Q8, Q.Q9, Q.Q12},
    "QEC":               {Q.Q3, Q.Q4, Q.Q9, Q.Q10, Q.Q11, Q.Q12},
    "QML":               {Q.Q3, Q.Q5, Q.Q7, Q.Q8, Q.Q9, Q.Q10},
    "Simulation":        {Q.Q8, Q.Q9},
    "QKD":               {Q.Q1, Q.Q3, Q.Q7, Q.Q9, Q.Q10},
    "Random Walks":      {Q.Q1, Q.Q4, Q.Q7, Q.Q9},
    "Amp. Estimation":   {Q.Q2, Q.Q6, Q.Q7, Q.Q9},
    "Approx. Counting":  {Q.Q2, Q.Q6, Q.Q7, Q.Q9, Q.Q10},
    "Teleportation":     {Q.Q3, Q.Q4, Q.Q7, Q.Q9, Q.Q10, Q.Q12},
    "GHZ Preparation":   {Q.Q1, Q.Q3, Q.Q4},
}
