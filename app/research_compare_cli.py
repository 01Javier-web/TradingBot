"""CLI para comparar el contexto de dos investigaciones registradas."""

from __future__ import annotations

import argparse
from pathlib import Path

from analytics.research_compare import compare_context
from analytics.research_registry import list_research_records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compara dos investigaciones registradas")
    parser.add_argument("first", help="ID de la primera investigación")
    parser.add_argument("second", help="ID de la segunda investigación")
    parser.add_argument(
        "--directory",
        default="artifacts/research",
        help="Directorio donde se almacenan las corridas registradas",
    )
    return parser


def find_record(records, experiment_id: str):
    for record in records:
        if record.experiment_id == experiment_id:
            return record
    raise ValueError(f"No existe la investigación {experiment_id}")


def format_comparison(first, second, comparison) -> str:
    lines = [
        "=== TradingBot Research Comparison ===",
        f"Primera investigación: {first.experiment_id}",
        f"Segunda investigación: {second.experiment_id}",
        f"Mismos datos: {'SI' if comparison.same_data else 'NO'}",
        f"Mismo número de filas: {'SI' if comparison.same_rows else 'NO'}",
        f"Mismo train ratio: {'SI' if comparison.same_train_ratio else 'NO'}",
        f"Mismo grid EMA rápidas: {'SI' if comparison.same_fast_ema_grid else 'NO'}",
        f"Mismo grid EMA lentas: {'SI' if comparison.same_slow_ema_grid else 'NO'}",
        f"Mismo grid RSI: {'SI' if comparison.same_rsi_grid else 'NO'}",
        f"Mismo contexto: {'SI' if comparison.same_context else 'NO'}",
        "Nota: la comparación describe contexto y no selecciona una estrategia.",
        "Modo: simulation-first",
    ]
    return "\n".join(lines)


def main() -> None:
    args = build_parser().parse_args()
    records = list_research_records(Path(args.directory))
    first = find_record(records, args.first)
    second = find_record(records, args.second)
    comparison = compare_context(first, second)
    print(format_comparison(first, second, comparison))


if __name__ == "__main__":
    main()
