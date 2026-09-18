"""Pruebas del optimizador controlado."""

import pandas as pd

from backtesting.optimizer import ParameterGrid, optimize


import pytest


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


@pytest.mark.parametrize("kwargs", [
    {"fast_ema_periods": ()},
    {"slow_ema_periods": ()},
    {"rsi_periods": ()},
    {"fast_ema_periods": (0,)},
    {"rsi_periods": (True,)},
])
def test_invalid_parameter_grid_is_rejected(kwargs: dict) -> None:
    with pytest.raises(ValueError):
        ParameterGrid(**kwargs)


def test_optimizer_evaluates_valid_combinations_on_train_and_test() -> None:
    results = optimize(
        make_data(),
        ParameterGrid(fast_ema_periods=(5, 10), slow_ema_periods=(10, 20), rsi_periods=(14,)),
    )
    assert len(results) == 3
    assert all(result.config.fast_ema_period < result.config.slow_ema_period for result in results)


def test_parameter_grid_rejects_duplicate_values() -> None:
    with pytest.raises(ValueError, match="duplicados"):
        ParameterGrid(fast_ema_periods=(5, 5), slow_ema_periods=(20,))


def test_optimizer_rejects_non_finite_train_ratio() -> None:
    with pytest.raises(ValueError, match="finito"):
        optimize(make_data(), ParameterGrid(fast_ema_periods=(5,), slow_ema_periods=(20,)), train_ratio=float("nan"))
