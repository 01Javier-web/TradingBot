"""Pruebas de clasificación descriptiva de resultados."""

from ai.research_selection import classify_consistency
from backtesting.optimizer import OptimizationResult
from strategy.signals import StrategyConfig


def test_consistency_classification_preserves_input_order() -> None:
    config_a = StrategyConfig(fast_ema_period=5, slow_ema_period=10)
    config_b = StrategyConfig(fast_ema_period=6, slow_ema_period=12)
    results = [
        OptimizationResult(config_a, 10.0, -1.0),
        OptimizationResult(config_b, 5.0, 2.0),
    ]

    candidates = classify_consistency(results)

    assert len(candidates) == 2
    assert candidates[0].result is results[0]
    assert candidates[0].consistent is False
    assert candidates[1].result is results[1]
    assert candidates[1].consistent is True


def test_consistency_classification_handles_empty_input() -> None:
    assert classify_consistency([]) == ()
