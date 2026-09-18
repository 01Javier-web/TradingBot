"""Pruebas adicionales de integridad del backtesting y research."""

import pandas as pd
import pytest

from analytics.research_manifest import ResearchManifest
from backtesting.metrics import max_drawdown, profit_factor, win_rate
from backtesting.models import BacktestResult, PositionSide, Trade
from backtesting.optimizer import OptimizationResult, ParameterGrid
from backtesting.splits import chronological_split
from backtesting.walk_forward import walk_forward
from strategy.signals import StrategyConfig


def _data(rows: int = 30) -> pd.DataFrame:
    close = pd.Series(range(100, 100 + rows), dtype=float)
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=rows, freq="h"),
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
        }
    )


def test_trade_rejects_invalid_side_and_non_positive_quantity() -> None:
    with pytest.raises(ValueError):
        Trade(pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2026-01-02", tz="UTC"), "BUY", 10, 11, 1, 1, 0)
    with pytest.raises(ValueError):
        Trade(pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2026-01-02", tz="UTC"), PositionSide.BUY, 10, 11, 0, 1, 0)


def test_trade_rejects_zero_duration() -> None:
    instant = pd.Timestamp("2026-01-01", tz="UTC")
    with pytest.raises(ValueError, match="posterior"):
        Trade(instant, instant, PositionSide.BUY, 10, 11, 1, 1, 0)


def test_backtest_result_requires_coherent_trade_accounting() -> None:
    trade = Trade(pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2026-01-02", tz="UTC"), PositionSide.BUY, 100, 110, 1, 10, 1)
    with pytest.raises(ValueError, match="final_balance"):
        BacktestResult(100.0, 100.0, (trade,), (100.0, 100.0))


def test_backtest_result_requires_coherent_equity_endpoints() -> None:
    with pytest.raises(ValueError, match="terminar"):
        BacktestResult(100.0, 110.0, (), (100.0, 105.0))


def test_metrics_reject_non_finite_values() -> None:
    with pytest.raises(ValueError):
        max_drawdown([100.0, float("nan")])
    with pytest.raises(ValueError):
        win_rate([1.0, float("inf")])
    with pytest.raises(ValueError):
        profit_factor([1.0, float("-inf")])


@pytest.mark.parametrize("ratio", [True, 0.0, 1.0, float("nan"), "0.7"])
def test_chronological_split_rejects_invalid_ratio(ratio: object) -> None:
    with pytest.raises(ValueError):
        chronological_split(_data(), ratio)  # type: ignore[arg-type]


def test_parameter_grid_rejects_list_values() -> None:
    with pytest.raises(ValueError, match="tuple"):
        ParameterGrid(fast_ema_periods=[5, 10], slow_ema_periods=(20,))  # type: ignore[arg-type]


def test_manifest_normalizes_fingerprint_case() -> None:
    manifest = ResearchManifest.from_grid(
        30,
        ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,)),
        data_fingerprint="A" * 64,
    )
    assert manifest.data_fingerprint == "a" * 64
    assert manifest.schema_version == "research-v1"


def test_walk_forward_with_step_one_keeps_test_starts_strictly_advancing() -> None:
    windows = walk_forward(_data(20), StrategyConfig(fast_ema_period=3, slow_ema_period=6), 8, 4, step=1)
    assert len(windows) == 9
    assert all(a.test_start < b.test_start for a, b in zip(windows, windows[1:]))


def test_optimization_result_rejects_non_finite_pnl() -> None:
    config = StrategyConfig(fast_ema_period=5, slow_ema_period=10)
    with pytest.raises(ValueError):
        OptimizationResult(config, float("nan"), 1.0)


def test_backtest_consistency_rejects_overlapping_trades() -> None:
    from backtesting.consistency import validate_backtest_result
    first = Trade(pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp("2026-01-03", tz="UTC"), PositionSide.BUY, 100, 101, 1, 1, 0)
    second = Trade(pd.Timestamp("2026-01-02", tz="UTC"), pd.Timestamp("2026-01-04", tz="UTC"), PositionSide.SELL, 100, 99, 1, 1, 0)
    result = object.__new__(BacktestResult)
    object.__setattr__(result, "initial_balance", 100.0)
    object.__setattr__(result, "final_balance", 102.0)
    object.__setattr__(result, "trades", (first, second))
    object.__setattr__(result, "equity_curve", (100.0, 102.0))
    check = validate_backtest_result(result)
    assert check.valid is False
    assert any("solapa" in issue for issue in check.issues)
