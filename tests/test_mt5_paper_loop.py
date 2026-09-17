"""Pruebas del flujo MT5 de solo lectura hacia paper trading."""

from __future__ import annotations

import numpy as np

from app.mt5_paper_loop import run_mt5_snapshot
from risk.kill_switch import KillSwitch


def test_mt5_snapshot_fails_without_market_data(monkeypatch) -> None:
    monkeypatch.setattr("app.mt5_paper_loop.get_candles", lambda *args, **kwargs: None)

    try:
        run_mt5_snapshot("EURUSD", 15, count=10)
    except RuntimeError as exc:
        assert "datos de mercado" in str(exc)
    else:
        raise AssertionError("La ausencia de datos debería detener el flujo")


def test_mt5_snapshot_does_not_require_execution_adapter(monkeypatch) -> None:
    rates = np.array(
        [
            (1700000000 + i * 60, 1.10 + i * 0.0001, 1.101 + i * 0.0001, 1.099 + i * 0.0001, 1.1005 + i * 0.0001, 100, 0, 0)
            for i in range(60)
        ],
        dtype=[
            ("time", "i8"), ("open", "f8"), ("high", "f8"),
            ("low", "f8"), ("close", "f8"), ("tick_volume", "i8"),
            ("spread", "i8"), ("real_volume", "i8"),
        ],
    )
    monkeypatch.setattr("app.mt5_paper_loop.get_candles", lambda *args, **kwargs: rates)

    events = run_mt5_snapshot("EURUSD", 15, count=60)
    assert len(events) == 60


def test_kill_switch_stops_snapshot_before_processing(monkeypatch) -> None:
    rates = np.array(
        [(1700000000, 1.1, 1.2, 1.0, 1.1, 100, 0, 0)],
        dtype=[
            ("time", "i8"), ("open", "f8"), ("high", "f8"),
            ("low", "f8"), ("close", "f8"), ("tick_volume", "i8"),
            ("spread", "i8"), ("real_volume", "i8"),
        ],
    )
    monkeypatch.setattr("app.mt5_paper_loop.get_candles", lambda *args, **kwargs: rates)
    switch = KillSwitch()
    switch.trigger("test")

    try:
        run_mt5_snapshot("EURUSD", 15, kill_switch=switch)
    except RuntimeError as exc:
        assert "Kill switch" in str(exc)
    else:
        raise AssertionError("El kill switch debería detener el flujo")
