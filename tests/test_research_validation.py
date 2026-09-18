"""Pruebas de calidad de resultados de investigación."""

from backtesting.optimizer import OptimizationResult
from ai.research_validation import validate_results
from strategy.signals import StrategyConfig


def test_validation_accepts_unique_finite_results() -> None:
    config = StrategyConfig(fast_ema_period=5, slow_ema_period=10)
    result = OptimizationResult(config, 10.0, 2.0)

    validation = validate_results([result])

    assert validation.valid is True
    assert validation.issues == ()


def test_validation_rejects_duplicate_configs() -> None:
    config = StrategyConfig(fast_ema_period=5, slow_ema_period=10)
    results = [
        OptimizationResult(config, 10.0, 2.0),
        OptimizationResult(config, 8.0, 1.0),
    ]

    validation = validate_results(results)

    assert validation.valid is False
    assert "configuraciones duplicadas" in validation.issues[0]


def test_validation_rejects_empty_results() -> None:
    validation = validate_results([])

    assert validation.valid is False
    assert validation.issues == ("No hay resultados de optimización.",)


def test_validation_rejects_non_list_results() -> None:
    validation = validate_results(())  # type: ignore[arg-type]
    assert validation.valid is False
    assert "lista" in validation.issues[0]


def test_validation_rejects_wrong_result_type() -> None:
    validation = validate_results([object()])  # type: ignore[list-item]
    assert validation.valid is False
    assert "OptimizationResult" in validation.issues[0]
