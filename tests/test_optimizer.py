"""Pruebas del optimizador controlado."""

import pandas as pd

from backtesting.optimizer import ParameterGrid, optimize


def make_data() -> pd.DataFrame:
    close = [100 + i * 0.15 for i in range(100)]
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=100, freq="15min"),
            "open": close,
            "high": [x + 0.2 for x in close],
            "low": [x - 0.2 for x in close],
            "close": close,
        }
    )


def test_optimizer_evaluates_valid_combinations_on_train_and_test() -> None:
    results = optimize(
        make_data(),
        ParameterGrid(fast_ema_periods=(5, 10), slow_ema_periods=(10, 20), rsi_periods=(14,)),
    )
    assert len(results) == 3
    assert all(result.config.fast_ema_period < result.config.slow_ema_period for result in results)
