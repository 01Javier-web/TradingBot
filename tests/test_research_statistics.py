"""Pruebas de robustez estadística de la investigación."""

import pytest

from ai.research_quality import assess_quality
from analytics.research_statistics import (
    ResearchStatisticsConfig,
    assess_statistics,
)
from backtesting.optimizer import OptimizationResult
from strategy.signals import StrategyConfig


def _result(
    train: float,
    test: float,
    *,
    test_trades: int | None = 40,
    test_drawdown: float | None = 0.10,
    test_win_rate: float | None = 0.50,
    test_profit_factor: float | None = 1.20,
) -> OptimizationResult:
    return OptimizationResult(
        StrategyConfig(fast_ema_period=5, slow_ema_period=20),
        train,
        test,
        train_trades=50 if test_trades is not None else None,
        test_trades=test_trades,
        train_drawdown=0.08 if test_drawdown is not None else None,
        test_drawdown=test_drawdown,
        train_win_rate=0.55 if test_win_rate is not None else None,
        test_win_rate=test_win_rate,
        train_profit_factor=1.30 if test_profit_factor is not None else None,
        test_profit_factor=test_profit_factor,
    )


def test_optimizer_metrics_are_exposed_through_quality_results() -> None:
    result = _result(100.0, 50.0)

    assert result.test_trades == 40
    assert result.test_drawdown == pytest.approx(0.10)
    assert result.test_win_rate == pytest.approx(0.50)
    assert result.test_profit_factor == pytest.approx(1.20)


def test_statistics_detects_small_sample_and_weak_generalization() -> None:
    statistics = assess_statistics(
        [
            _result(100.0, 10.0, test_trades=12),
            _result(100.0, -2.0, test_trades=40),
        ]
    )

    assert statistics.insufficient_test_sample == 1
    assert statistics.train_positive_test_negative == 1
    assert statistics.weak_test_generalization == 1
    assert statistics.statistically_incomplete is False
    assert statistics.warnings


def test_statistics_detects_high_drawdown() -> None:
    statistics = assess_statistics(
        [_result(100.0, 50.0, test_drawdown=0.40)],
        ResearchStatisticsConfig(maximum_test_drawdown=0.25),
    )

    assert statistics.high_test_drawdown == 1


def test_statistics_preserves_missing_metric_information() -> None:
    statistics = assess_statistics(
        [_result(10.0, 5.0, test_profit_factor=None)]
    )

    assert statistics.metrics_available == 0
    assert statistics.statistically_incomplete is False
    assert statistics.unbounded_test_profit_factor == 1
    assert any("profit factor no acotado" in warning for warning in statistics.warnings)


def test_statistics_rejects_invalid_configuration() -> None:
    with pytest.raises(ValueError):
        ResearchStatisticsConfig(minimum_test_trades=-1)
    with pytest.raises(ValueError):
        ResearchStatisticsConfig(maximum_test_drawdown=-0.1)
