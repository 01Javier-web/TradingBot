"""CLI local para auditar la integridad del catálogo de investigaciones."""

from __future__ import annotations

import argparse
from pathlib import Path

from analytics.research_audit import CatalogAudit, audit_catalog


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audita investigaciones registradas")
    parser.add_argument(
        "--directory",
        default="artifacts/research",
        help="Directorio donde se almacenan las corridas registradas",
    )
    return parser


def format_audit(result: CatalogAudit) -> str:
    """Genera una salida estable y explícita sobre la integridad."""
    status = "OK" if result.invalid == 0 else "ERROR"
    lines = [
        "=== TradingBot Research Audit ===",
        f"Estado: {status}",
        f"Archivos: {result.files}",
        f"Válidos: {result.valid}",
        f"Inválidos: {result.invalid}",
    ]
    if result.issues:
        lines.append("Problemas:")
        lines.extend(f"- {issue}" for issue in result.issues)
    lines.append("Modo: simulation-first")
    return "\n".join(lines)


def main() -> None:
    args = build_parser().parse_args()
    print(format_audit(audit_catalog(Path(args.directory))))


if __name__ == "__main__":
    main()
