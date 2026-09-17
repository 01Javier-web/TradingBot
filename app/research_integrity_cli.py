"""CLI para auditar la integridad de investigaciones almacenadas."""

from __future__ import annotations

import argparse
from pathlib import Path

from analytics.research_integrity import validate_record_integrity
from analytics.research_registry import load_research_record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audita investigaciones registradas")
    parser.add_argument(
        "--directory",
        default="artifacts/research",
        help="Directorio de investigaciones registradas",
    )
    return parser


def audit_directory(directory: str | Path) -> tuple[tuple[str, bool, tuple[str, ...]], ...]:
    root = Path(directory)
    if not root.exists():
        return ()

    results = []
    for path in sorted(root.glob("*.json")):
        try:
            document = load_research_record(path)
            check = validate_record_integrity(document)
            results.append((path.name, check.valid, check.issues))
        except (OSError, ValueError) as exc:
            results.append((path.name, False, (str(exc),)))
    return tuple(results)


def format_audit(results) -> str:
    valid = sum(item[1] for item in results)
    lines = [
        "=== TradingBot Research Integrity Audit ===",
        f"Registros: {len(results)}",
        f"Válidos: {valid}",
        f"Inválidos: {len(results) - valid}",
    ]
    for name, is_valid, issues in results:
        lines.append(f"[{ 'OK' if is_valid else 'ERROR' }] {name}")
        lines.extend(f"    - {issue}" for issue in issues)
    lines.append("Modo: simulation-first")
    return "\n".join(lines)


def main() -> None:
    args = build_parser().parse_args()
    print(format_audit(audit_directory(args.directory)))


if __name__ == "__main__":
    main()
