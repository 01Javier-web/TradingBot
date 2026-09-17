"""Ejecución reproducible de experimentos de backtesting."""

from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path

import pandas as pd

from analytics.report import PerformanceReport, build_report
from backtesting.engine import BacktestEngine
from strategy.signals import StrategyConfig


@dataclass(frozen=True)
class Experiment:
    """Identidad completa de un experimento reproducible."""

    name: str
    strategy: StrategyConfig
    initial_balance: float = 10_000.0
    quantity: float = 1.0
    commission: float = 0.0
    spread: float = 0.0


class ExperimentRunner:
    """Ejecuta configuraciones explícitas sin modificar el código de estrategia."""

    def run(self, df: pd.DataFrame, experiment: Experiment) -> PerformanceReport:
        engine = BacktestEngine(
            initial_balance=experiment.initial_balance,
            quantity=experiment.quantity,
            commission=experiment.commission,
            spread=experiment.spread,
        )
        result = engine.run(df, experiment.strategy)
        return build_report(result)

    @staticmethod
    def save_definition(experiment: Experiment, path: str | Path) -> None:
        """Guarda la configuración para poder reproducirla posteriormente."""
        payload = asdict(experiment)
        payload["strategy"] = asdict(experiment.strategy)
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
