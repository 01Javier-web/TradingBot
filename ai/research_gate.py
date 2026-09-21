"""Gate de selección y validación final para investigación.

Separa explícitamente dos momentos:
1. seleccionar un candidato usando únicamente métricas de train;
2. evaluar ese candidato sobre las métricas de test ya calculadas.

El módulo no autoriza ejecución ni convierte el candidato en una orden.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from ai.research_pipeline import ResearchRun
from backtesting.optimizer import OptimizationResult
from strategy.signals import StrategyConfig


@dataclass(frozen=True)
class ValidationSelection:
    """Candidato elegido para validación, sin consultar métricas de test."""

    experiment_id: str
    config: StrategyConfig
    train_pnl: float
    train_drawdown: float | None
    train_trades: int | None
    candidates: int

    def __post_init__(self) -> None:
        if not isinstance(self.experiment_id, str) or len(self.experiment_id) != 64:
            raise ValueError("experiment_id debe ser SHA-256 hexadecimal")
        if not isinstance(self.config, StrategyConfig):
            raise ValueError("config debe ser StrategyConfig")
        if not isfinite(float(self.train_pnl)):
            raise ValueError("train_pnl debe ser finito")
        if self.train_drawdown is not None and (
            not isfinite(float(self.train_drawdown)) or self.train_drawdown < 0
        ):
            raise ValueError("train_drawdown debe ser finito y no negativo o None")
        if self.train_trades is not None and (
            not isinstance(self.train_trades, int) or isinstance(self.train_trades, bool)
            or self.train_trades < 0
        ):
            raise ValueError("train_trades debe ser entero no negativo o None")
        if not isinstance(self.candidates, int) or isinstance(self.candidates, bool) or self.candidates < 1:
            raise ValueError("candidates debe ser entero positivo")


@dataclass(frozen=True)
class FinalValidation:
    """Resultado de evaluar el candidato seleccionado sobre test."""

    experiment_id: str
    config: StrategyConfig
    valid: bool
    test_pnl: float | None
    test_trades: int | None
    test_drawdown: float | None
    test_win_rate: float | None
    test_profit_factor: float | None
    issues: tuple[str, ...]

    @property
    def complete(self) -> bool:
        """Indica si todas las métricas principales de test están disponibles."""
        return (
            self.test_pnl is not None
            and self.test_trades is not None
            and self.test_drawdown is not None
            and self.test_win_rate is not None
        )


def select_for_validation(run: ResearchRun) -> ValidationSelection:
    """Selecciona un candidato usando exclusivamente métricas de train.

    Esta función no lee test_pnl, test_trades, test_drawdown, test_win_rate ni
    test_profit_factor para ordenar o desempatar candidatos.
    """
    if not isinstance(run, ResearchRun):
        raise ValueError("run debe ser ResearchRun")
    if not run.results:
        raise ValueError("No hay resultados para seleccionar")

    # El criterio es deliberadamente simple y auditable: mayor PnL de train.
    # Los empates se resuelven por la representación estable de StrategyConfig,
    # nunca por métricas de test.
    selected = min(
        run.results,
        key=lambda item: (
            -float(item.train_pnl),
            repr(item.config),
        ),
    )

    return ValidationSelection(
        experiment_id=run.experiment_id,
        config=selected.config,
        train_pnl=float(selected.train_pnl),
        train_drawdown=selected.train_drawdown,
        train_trades=selected.train_trades,
        candidates=len(run.results),
    )


def validate_selected_candidate(
    run: ResearchRun,
    selection: ValidationSelection,
) -> FinalValidation:
    """Evalúa sobre test exactamente el candidato seleccionado desde train."""
    if not isinstance(run, ResearchRun):
        raise ValueError("run debe ser ResearchRun")
    if not isinstance(selection, ValidationSelection):
        raise ValueError("selection debe ser ValidationSelection")

    issues: list[str] = []

    if selection.experiment_id != run.experiment_id:
        issues.append("La selección pertenece a un experimento diferente.")

    matches = [item for item in run.results if item.config == selection.config]
    if len(matches) != 1:
        issues.append("La configuración seleccionada no identifica exactamente un resultado.")

    if issues:
        return FinalValidation(
            experiment_id=run.experiment_id,
            config=selection.config,
            valid=False,
            test_pnl=None,
            test_trades=None,
            test_drawdown=None,
            test_win_rate=None,
            test_profit_factor=None,
            issues=tuple(issues),
        )

    result: OptimizationResult = matches[0]

    if result.test_trades is None or result.test_drawdown is None or result.test_win_rate is None:
        issues.append("Faltan métricas principales de test para la configuración seleccionada.")

    return FinalValidation(
        experiment_id=run.experiment_id,
        config=selection.config,
        valid=not issues,
        test_pnl=float(result.test_pnl),
        test_trades=result.test_trades,
        test_drawdown=result.test_drawdown,
        test_win_rate=result.test_win_rate,
        test_profit_factor=result.test_profit_factor,
        issues=tuple(issues),
    )


__all__ = [
    "FinalValidation",
    "ValidationSelection",
    "select_for_validation",
    "validate_selected_candidate",
]
