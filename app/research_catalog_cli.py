"""CLI local para inspeccionar el catálogo de investigaciones."""

from __future__ import annotations

import argparse
from pathlib import Path

from analytics.research_catalog import catalog_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lista investigaciones registradas")
    parser.add_argument(
        "--directory",
        default="artifacts/research",
        help="Directorio donde se almacenan las corridas registradas",
    )
    return parser


def format_catalog(records) -> str:
    """Genera una salida estable sin ordenar por rentabilidad."""
    lines = [
        "=== TradingBot Research Catalog ===",
        f"Investigaciones: {len(records)}",
    ]
    for index, record in enumerate(records, start=1):
        lines.extend(
            [
                f"[{index}] ID: {record.experiment_id}",
                f"    Datos: {record.data_fingerprint}",
                f"    Filas: {record.rows}",
                f"    Train ratio: {record.train_ratio}",
                f"    EMA rápidas: {record.fast_ema_periods}",
                f"    EMA lentas: {record.slow_ema_periods}",
                f"    RSI: {record.rsi_periods}",
            ]
        )
    lines.append("Modo: simulation-first")
    return "\n".join(lines)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    records = catalog_records(Path(args.directory))
    print(format_catalog(records))


if __name__ == "__main__":
    main()
