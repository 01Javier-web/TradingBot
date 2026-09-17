"""Pruebas del runner periódico de paper trading."""

from __future__ import annotations

import numpy as np

from app.live_paper import LivePaperRunner
from paper_trading.engine import PaperTradingEngine
from paper_trading.portfolio import PaperPortfolio
from risk.kill_switch import KillSwitch


def _rates(close: float = 1.1):
    return np.array(
        [(1700000000 + i * 60, close, close + 0.001, close - 0.001, close, 100, 0, 0) for i in range(60)],
        dtype=[
            ("time", "i8"), ("open", "f8"), ("high", "f8"),
            ("low", "f8"), ("close", "f8"), ("tick_volume", "i8"),
            ("spread", "i8"), ("real_volume", "i8"),
        ],
    )


def test_process_once_ignores_same_candle(monkeypatch) -> None:
    monkeypatch.setattr("app.live_paper.get_candles", lambda *args, **kwargs: _rates())
    runner = LivePaperRunner(PaperTradingEngine(PaperPortfolio()), poll_seconds=1)
    first = runner.process_once()
    second = runner.process_once()
    assert "signal=" in first
    assert second == "WAIT: sin vela nueva"


def test_kill_switch_blocks_live_paper(monkeypatch) -> None:
    monkeypatch.setattr("app.live_paper.get_candles", lambda *args, **kwargs: _rates())
    switch = KillSwitch()
    switch.trigger("manual stop")
    runner = LivePaperRunner(PaperTradingEngine(PaperPortfolio()), kill_switch=switch)
    try:
        runner.process_once()
    except RuntimeError as exc:
        assert "Kill switch" in str(exc)
    else:
        raise AssertionError("El kill switch debería bloquear el ciclo")
