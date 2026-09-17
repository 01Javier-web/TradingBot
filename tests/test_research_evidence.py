"""Pruebas del paquete de evidencia de investigación."""

from ai.research_evidence import build_evidence
from backtesting.optimizer import OptimizationResult
from strategy.signals import StrategyConfig


def test_build_evidence_validates_and_classifies() -> None:
    config = StrategyConfig(fast_ema_period=5, slow_ema_period=10)
    results = [OptimizationResult(config, 10.0, 2.0)]

    evidence = build_evidence(results)

    assert evidence.validation.valid is True
    assert len(evidence.candidates) == 1
    assert evidence.candidates[0].consistent is True


def test_build_evidence_stops_classification_when_invalid() -> None:
    config = StrategyConfig(fast_ema_period=5, slow_ema_period=10)
    results = [
        OptimizationResult(config, 10.0, 2.0),
        OptimizationResult(config, 8.0, 1.0),
    ]

    evidence = build_evidence(results)

    assert evidence.validation.valid is False
    assert evidence.candidates == ()
