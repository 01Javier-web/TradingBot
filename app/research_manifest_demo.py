"""Demo del manifiesto de reproducibilidad, sin conexión a MT5."""

from __future__ import annotations

from analytics.research_manifest import ResearchManifest
from backtesting.optimizer import ParameterGrid


def main() -> None:
    grid = ParameterGrid(
        fast_ema_periods=(5, 10),
        slow_ema_periods=(20, 30),
        rsi_periods=(14,),
    )
    manifest = ResearchManifest.from_grid(160, grid)

    print("=== TradingBot Research Manifest ===")
    print(f"Filas de datos: {manifest.rows}")
    print(f"Train ratio: {manifest.train_ratio}")
    print(f"EMA rápidas: {manifest.fast_ema_periods}")
    print(f"EMA lentas: {manifest.slow_ema_periods}")
    print(f"RSI: {manifest.rsi_periods}")
    print("Credenciales: no incluidas")
    print("Modo: simulation-first")


if __name__ == "__main__":
    main()
