"""Demo local de investigación sobre datos sintéticos.

Este comando no necesita MT5 y no ejecuta operaciones reales.
"""

from __future__ import annotations

import pandas as pd

from ai.research_pipeline import run_research
from backtesting.optimizer import ParameterGrid


def synthetic_data(rows: int = 160) -> pd.DataFrame:
    """Genera OHLC determinista para probar el pipeline de investigación."""
    if rows < 2:
        raise ValueError("rows debe ser al menos 2")
    close = pd.Series(range(1, rows + 1), dtype=float)
    low = (close - 1).clip(lower=0.1)
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=rows, freq="15min"),
            "open": close,
            "high": close + 1,
            "low": low,
            "close": close,
        }
    )


def main() -> None:
    run = run_research(
        synthetic_data(),
        ParameterGrid(fast_ema_periods=(5, 10), slow_ema_periods=(20, 30), rsi_periods=(14,)),
    )
    print("=== TradingBot Research Demo ===")
    for item in run.finding.findings:
        print(item)
    print(f"Configuraciones evaluadas: {len(run.results)}")
    print("Modo: simulation-first")
    print("Ejecución real: BLOQUEADA")


if __name__ == "__main__":
    main()
