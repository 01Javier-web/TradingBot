"""Pruebas del motor de backtesting."""

import pandas as pd
import pytest

from backtesting.engine import BacktestEngine
from backtesting.metrics import max_drawdown, profit_factor, win_rate


def test_backtest_rejects_unsorted_data() -> None:
    df = pd.DataFrame(
        {
            "time": pd.to_datetime(["2026-01-02", "2026-01-01"]),
            "open": [2, 1],
            "high": [3, 2],
            "low": [1, 0],
            "close": [2, 1],
        }
    )
    with pytest.raises(ValueError):
        BacktestEngine().run(df)


def test_backtest_is_next_candle_entry() -> None:
    rows = 80
    close = pd.Series(range(1, rows + 1), dtype=float)
    df = pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=rows, freq="h"),
            "open": close + 0.1,
            "high": close + 1.0,
            "low": (close - 1.0).clip(lower=0.1),
            "close": close,
        }
    )
    result = BacktestEngine(quantity=1).run(df)
    assert result.trades
    assert result.trades[0].entry_time == pd.Timestamp(df.loc[2, "time"], tz="UTC")
    assert result.trades[0].entry_price == pytest.approx(df.loc[2, "open"])


def test_equity_curve_marks_open_positions_to_market_and_closes_at_end() -> None:
    rows = 80
    close = pd.Series(range(1, rows + 1), dtype=float)
    df = pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=rows, freq="h"),
            "open": close + 0.1,
            "high": close + 1.0,
            "low": (close - 1.0).clip(lower=0.1),
            "close": close,
        }
    )

    result = BacktestEngine(quantity=1).run(df)

    assert len(result.equity_curve) == len(df)
    assert result.equity_curve[0] == pytest.approx(result.initial_balance)
    assert result.equity_curve[-1] == pytest.approx(result.final_balance)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"initial_balance": float("nan")},
        {"quantity": float("inf")},
        {"commission": float("nan")},
        {"spread": float("inf")},
        {"commission": -0.1},
        {"spread": -0.1},
    ],
)
def test_backtest_rejects_invalid_cost_or_balance_parameters(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        BacktestEngine(**kwargs)


def test_metrics() -> None:
    pnls = [10.0, -5.0, 5.0]
    assert win_rate(pnls) == pytest.approx(2 / 3)
    assert profit_factor(pnls) == pytest.approx(3.0)
    assert max_drawdown([100.0, 120.0, 90.0, 110.0]) == pytest.approx(0.25)
