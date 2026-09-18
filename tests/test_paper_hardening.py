"""Pruebas de fronteras adicionales para paper trading."""

import pandas as pd
import pytest

from analytics.paper_audit import audit_paper_events
from paper_trading.engine import PaperTradingEngine
from paper_trading.live import run_bounded_paper_loop
from paper_trading.portfolio import PaperPortfolio
from paper_trading.session import PaperTradingSession
from strategy.signals import Signal


@pytest.mark.parametrize("quantity", [True, 0, float("nan"), float("inf"), "1"])
def test_paper_engine_rejects_invalid_quantity(quantity: object) -> None:
    with pytest.raises(ValueError):
        PaperTradingEngine(PaperPortfolio(), quantity=quantity)  # type: ignore[arg-type]


def test_paper_engine_rejects_negative_atr() -> None:
    engine = PaperTradingEngine(PaperPortfolio())
    result = engine.process(pd.Series({"close": 100.0, "atr": -1.0, "signal": Signal.BUY}))
    assert result == "WAIT: ATR inválido"
    assert engine.history[-1]["action"] == "REJECTED"


@pytest.mark.parametrize("interval", [True, float("nan"), float("inf"), "1"])
def test_live_loop_rejects_invalid_interval(interval: object) -> None:
    with pytest.raises(ValueError):
        run_bounded_paper_loop(
            type("Feed", (), {"latest": lambda self, symbol, timeframe, count: pd.DataFrame()})(),
            lambda: PaperTradingSession(PaperPortfolio()),
            symbol="TEST",
            timeframe=15,
            interval_seconds=interval,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("value", [True, 0, -1, 1.5, "15"])
def test_live_loop_rejects_invalid_timeframe(value: object) -> None:
    with pytest.raises(ValueError):
        run_bounded_paper_loop(
            type("Feed", (), {"latest": lambda self, symbol, timeframe, count: pd.DataFrame()})(),
            lambda: PaperTradingSession(PaperPortfolio()),
            symbol="TEST",
            timeframe=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("field", ["polls", "count"])
def test_live_loop_rejects_invalid_integer_fields(field: str) -> None:
    kwargs = {"symbol": "TEST", "timeframe": 15, "polls": 1, "count": 10}
    kwargs[field] = 0
    with pytest.raises(ValueError):
        run_bounded_paper_loop(
            type("Feed", (), {"latest": lambda self, symbol, timeframe, count: pd.DataFrame()})(),
            lambda: PaperTradingSession(PaperPortfolio()),
            **kwargs,
        )


def test_paper_engine_rejects_present_but_invalid_market_time() -> None:
    engine = PaperTradingEngine(PaperPortfolio())
    result = engine.process(
        pd.Series({"time": "not-a-timestamp", "close": 100.0, "atr": 1.0, "signal": Signal.BUY})
    )

    assert result == "WAIT: market_time inválido"
    assert engine.history[-1]["action"] == "REJECTED"
    assert engine.history[-1]["reason"] == "market_time inválido"


def test_audit_rejects_action_without_required_context() -> None:
    result = audit_paper_events([{"sequence": 1, "action": "OPEN"}])

    assert result.valid is False
    assert "OPEN requiere side" in result.issues
    assert "OPEN requiere price" in result.issues
    assert "OPEN requiere quantity" in result.issues
    assert "OPEN requiere stop_loss" in result.issues


def test_audit_accepts_complete_rejection_event() -> None:
    result = audit_paper_events(
        [
            {
                "sequence": 1,
                "action": "REJECTED",
                "reason": "ATR inválido",
                "market_time": "2026-01-01T00:00:00+00:00",
            }
        ]
    )

    assert result.valid is True
    assert result.event_count == 1


def test_audit_rejects_invalid_market_time() -> None:
    result = audit_paper_events(
        [
            {
                "sequence": 1,
                "action": "REJECTED",
                "reason": "precio inválido",
                "market_time": "not-a-timestamp",
            }
        ]
    )

    assert result.valid is False
    assert "market_time inválido" in result.issues
