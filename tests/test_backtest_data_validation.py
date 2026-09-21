"""Pruebas de la frontera de validación del backtesting."""

from __future__ import annotations

import pandas as pd
import pytest

from backtesting.engine import BacktestEngine


def valid_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=3, freq="15min", tz="UTC"),
            "open": [100.0, 101.0, 102.0],
            "high": [102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0],
            "close": [101.0, 102.0, 103.0],
        }
    )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda df: df.iloc[::-1],
        lambda df: pd.concat([df, df.iloc[[0]]], ignore_index=True),
        lambda df: df.assign(close=[101.0, float("nan"), 103.0]),
        lambda df: df.assign(high=[98.0, 103.0, 104.0]),
        lambda df: df.assign(close=[101.0, 0.0, 103.0]),
    ],
)
def test_backtest_rejects_invalid_market_data(mutate) -> None:
    with pytest.raises(ValueError):
        BacktestEngine().run(mutate(valid_data()))


def test_backtest_accepts_valid_market_data() -> None:
    result = BacktestEngine().run(valid_data())

    assert result.initial_balance == pytest.approx(10_000.0)
    # Con tres velas no se debe abrir una posición en la última vela para
    # evitar una operación artificial con entrada y salida simultáneas.
    assert result.final_balance == pytest.approx(10_000.0)


def test_backtest_does_not_create_last_candle_entry() -> None:
    data = valid_data()
    result = BacktestEngine().run(data)

    assert result.trades == ()
    assert result.final_balance == pytest.approx(result.initial_balance)


def test_backtest_applies_spread_and_commission_without_lookahead(monkeypatch) -> None:
    from strategy.signals import Signal

    data = pd.DataFrame({
        "time": pd.date_range("2026-01-01", periods=4, freq="15min", tz="UTC"),
        "open": [100.0, 101.0, 102.0, 103.0],
        "high": [101.0, 102.0, 103.0, 104.0],
        "low": [99.0, 100.0, 101.0, 102.0],
        "close": [100.5, 101.5, 102.5, 103.5],
    })
    signals = [Signal.BUY, Signal.WAIT, Signal.SELL, Signal.WAIT]

    def fake_signals(frame, config=None):
        result = frame.copy()
        result["signal"] = signals
        return result

    monkeypatch.setattr("backtesting.engine.generate_signals", fake_signals)
    result = BacktestEngine(quantity=1.0, commission=1.0, spread=2.0).run(data)
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.entry_time == data.iloc[1]["time"]
    assert trade.exit_time == data.iloc[3]["time"]
    assert trade.entry_price == pytest.approx(102.0)
    assert trade.exit_price == pytest.approx(102.0)
    assert trade.gross_pnl == pytest.approx(0.0)
    assert trade.net_pnl == pytest.approx(-1.0)


def test_backtest_sell_uses_inverse_pnl_direction(monkeypatch) -> None:
    from strategy.signals import Signal

    data = valid_data().copy()
    data = pd.concat(
        [
            data,
            pd.DataFrame({
                "time": [pd.Timestamp("2026-01-01 00:45:00", tz="UTC")],
                "open": [104.0], "high": [105.0], "low": [103.0], "close": [103.0],
            }),
        ],
        ignore_index=True,
    )
    signals = [Signal.SELL, Signal.WAIT, Signal.BUY, Signal.WAIT]

    def fake_signals(frame, config=None):
        result = frame.copy()
        result["signal"] = signals
        return result

    monkeypatch.setattr("backtesting.engine.generate_signals", fake_signals)
    result = BacktestEngine().run(data)
    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.side.value == "SELL"
    assert trade.gross_pnl == pytest.approx(2.0)
