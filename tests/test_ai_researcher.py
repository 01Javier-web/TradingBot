"""Pruebas de la capa de investigación sin autoridad de ejecución."""

from backtesting.optimizer import OptimizationResult
from ai.researcher import summarize_optimization
from strategy.signals import StrategyConfig


def test_researcher_summarizes_train_and_test_results() -> None:
    config = StrategyConfig(fast_ema_period=5, slow_ema_period=10)
    results = [
        OptimizationResult(config, 10.0, 5.0),
        OptimizationResult(config, 8.0, -2.0),
        OptimizationResult(config, -1.0, 3.0),
    ]

    finding = summarize_optimization(results)

    assert finding.experiments == 3
    assert finding.profitable_train == 2
    assert finding.profitable_test == 2
    assert finding.generalization_rate == 1 / 3
    assert len(finding.findings) == 4


def test_researcher_handles_empty_results() -> None:
    finding = summarize_optimization([])

    assert finding.experiments == 0
    assert finding.generalization_rate == 0.0
    assert finding.findings == ("No hay resultados para analizar.",)
