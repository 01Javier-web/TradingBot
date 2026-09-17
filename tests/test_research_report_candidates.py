"""Pruebas del resumen serializable de candidatos."""

from ai.research_selection import ResearchCandidate
from analytics.research_report import candidate_summary
from backtesting.optimizer import OptimizationResult
from strategy.signals import StrategyConfig


def test_candidate_summary_contains_config_and_pnl() -> None:
    config = StrategyConfig(fast_ema_period=5, slow_ema_period=10, rsi_period=14)
    result = OptimizationResult(config, 10.0, 4.0)
    candidates = (ResearchCandidate(result, True),)

    summary = candidate_summary(candidates)

    assert summary == [
        {
            "fast_ema_period": 5,
            "slow_ema_period": 10,
            "rsi_period": 14,
            "train_pnl": 10.0,
            "test_pnl": 4.0,
            "consistent": True,
        }
    ]
