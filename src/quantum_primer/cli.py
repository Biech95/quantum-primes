"""CLI entry point: quantum-prime."""

import argparse
from quantum_primer.primes import QPRIME_DB, UNITARY_PRIMES, NON_UNITARY_PRIMES
from quantum_primer.hardware import HARDWARE
from quantum_primer.factorizations import ALGORITHM_FACTORIZATIONS


def main():
    parser = argparse.ArgumentParser(
        prog="quantum-prime",
        description="Quantum Primes: Analyze quantum circuits via irreducible primitives",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("primes", help="List the 12 quantum primes")
    sub.add_parser("hardware", help="List hardware profiles")
    sub.add_parser("algorithms", help="Show algorithm factorizations")

    p_compare = sub.add_parser("compare", help="Compare hardware platforms for an algorithm")
    p_compare.add_argument("algorithm", help="Algorithm name (e.g., 'Shor', 'VQE')")

    args = parser.parse_args()

    if args.command == "primes":
        cmd_primes()
    elif args.command == "hardware":
        cmd_hardware()
    elif args.command == "algorithms":
        cmd_algorithms()
    elif args.command == "compare":
        cmd_compare(args.algorithm)
    else:
        parser.print_help()


def cmd_primes():
    print("Quantum Primes — 12 Irreducible Quantum Computational Primitives\n")
    print("Unitary (Q1-Q8):")
    for p in sorted(UNITARY_PRIMES, key=lambda x: x.name):
        info = QPRIME_DB[p]
        print(f"  {p.name:>3}  {info.symbol:<12} {p.value:<25} ← {info.classical_analog}")
    print("\nNon-Unitary (Q9-Q12):")
    for p in sorted(NON_UNITARY_PRIMES, key=lambda x: x.name):
        info = QPRIME_DB[p]
        print(f"  {p.name:>3}  {info.symbol:<12} {p.value:<25} ← {info.classical_analog}")


def cmd_hardware():
    print("Hardware Profiles\n")
    for key, hw in HARDWARE.items():
        native = sum(1 for s in hw.prime_support.values()
                     if s.name == "NATIVE")
        print(f"  {key:<20} {hw.name}")
        print(f"  {'':20} 2Q gate: {hw.native_2q}")
        print(f"  {'':20} Connectivity: {hw.connectivity}")
        print(f"  {'':20} Native primes: {native}/12")
        print(f"  {'':20} 2Q fidelity: {hw.typical_2q_fidelity*100:.1f}%")
        print()


def cmd_algorithms():
    print("Algorithm Factorizations\n")
    print(f"  {'Algorithm':<22} {'Primes':<40} {'Count'}")
    print(f"  {'-'*70}")
    for name, primes in ALGORITHM_FACTORIZATIONS.items():
        prime_str = ", ".join(sorted(p.name for p in primes))
        print(f"  {name:<22} {prime_str:<40} {len(primes)}")


def cmd_compare(algo_name: str):
    # Find algorithm
    matched = None
    for name, primes in ALGORITHM_FACTORIZATIONS.items():
        if algo_name.lower() in name.lower():
            matched = (name, primes)
            break

    if not matched:
        print(f"Unknown algorithm '{algo_name}'. Available:")
        for name in ALGORITHM_FACTORIZATIONS:
            print(f"  {name}")
        return

    name, primes = matched
    print(f"═══ {name} — Hardware Comparison ═══")
    print(f"Required primes: {', '.join(sorted(p.name for p in primes))}\n")

    print(f"  {'Platform':<22} {'Native':<8} {'Composite':<10} {'Coverage':<10} {'SWAPs'}")
    print(f"  {'-'*60}")

    for hw_key, hw in HARDWARE.items():
        native = sum(1 for p in primes
                     if hw.prime_support.get(p, None) and
                     hw.prime_support[p].name == "NATIVE")
        composite = len(primes) - native
        coverage = native / len(primes) * 100
        swaps = "0" if hw.connectivity == "all-to-all" else "varies"
        print(f"  {hw.name:<22} {native:<8} {composite:<10} {coverage:<9.0f}% {swaps}")

    # Best platform
    best_key = max(HARDWARE.keys(),
                   key=lambda k: sum(1 for p in primes
                                     if HARDWARE[k].prime_support.get(p, None) and
                                     HARDWARE[k].prime_support[p].name == "NATIVE"))
    print(f"\n  Best fit: {HARDWARE[best_key].name}")


if __name__ == "__main__":
    main()
