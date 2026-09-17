"""Pruebas de integración del estado expuesto por LivePaperRunner."""

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


def test_runner_status_reflects_virtual_engine(monkeypatch) -> None:
    monkeypatch.setattr("app.live_paper.get_candles", lambda *args, **kwargs: _rates())
    runner = LivePaperRunner(PaperTradingEngine(PaperPortfolio()), poll_seconds=1)

    runner.process_once()
    status = runner.status()

    assert status.balance == 10_000
    assert status.equity == 10_000
    assert status.kill_switch_active is False
    assert status.event_counts


def test_runner_status_reflects_kill_switch(monkeypatch) -> None:
    monkeypatch.setattr("app.live_paper.get_candles", lambda *args, **kwargs: _rates())
    switch = KillSwitch()
    switch.trigger("test stop")
    runner = LivePaperRunner(PaperTradingEngine(PaperPortfolio()), kill_switch=switch)

    status = runner.status()

    assert status.kill_switch_active is True
    assert status.kill_switch_reason == "test stop"
