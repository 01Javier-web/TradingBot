"""Pruebas de evaluación descriptiva de calidad."""

from backtesting.optimizer import OptimizationResult
from ai.research_quality import assess_quality
from strategy.signals import StrategyConfig


def _result(train: float, test: float) -> OptimizationResult:
    return OptimizationResult(StrategyConfig(fast_ema_period=5, slow_ema_period=10), train, test)


def test_quality_counts_train_test_and_generalization() -> None:
    quality = assess_quality([_result(10.0, 5.0), _result(5.0, -1.0), _result(-2.0, -3.0)])

    assert quality.sample_size == 3
    assert quality.finite_results is True
    assert quality.positive_train == 2
    assert quality.positive_test == 1
    assert quality.positive_both == 1
    assert quality.generalization_rate == 1 / 3


def test_quality_empty_results_are_explicit() -> None:
    quality = assess_quality([])

    assert quality.sample_size == 0
    assert quality.finite_results is True
    assert quality.generalization_rate == 0.0
