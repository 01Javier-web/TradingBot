"""Pruebas de la sesión integrada de paper trading."""

import pandas as pd
import pytest

from paper_trading.session import PaperTradingSession
from paper_trading.portfolio import PaperPortfolio
from strategy.signals import StrategyConfig


def _data(rows: int = 80) -> pd.DataFrame:
    close = pd.Series(range(1, rows + 1), dtype=float)
    return pd.DataFrame(
        {
            "time": pd.date_range("2026-01-01", periods=rows, freq="15min"),
            "open": close,
            "high": close + 1.0,
            "low": (close - 1.0).clip(lower=0.1),
            "close": close,
        }
    )


def test_session_runs_full_signal_to_report_flow() -> None:
    portfolio = PaperPortfolio(initial_balance=10_000)
    session = PaperTradingSession(portfolio, StrategyConfig(fast_ema_period=5, slow_ema_period=20))

    result = session.run(_data())

    assert result.rows == 80
    assert result.events == tuple(session.engine.history)
    assert result.report.initial_balance == pytest.approx(10_000)
    assert result.report.consistent
    assert result.report.final_balance == pytest.approx(portfolio.balance)
    assert result.audit.valid
    assert result.audit.event_count == len(result.events)


def test_session_rejects_invalid_market_data_before_processing() -> None:
    data = _data()
    data.loc[10, "low"] = 0

    session = PaperTradingSession(PaperPortfolio())

    with pytest.raises(ValueError, match="mayores que 0"):
        session.run(data)

    assert session.engine.history == []


def test_session_preserves_chronological_market_data() -> None:
    data = _data()
    data.loc[5, "time"] = data.loc[4, "time"]

    session = PaperTradingSession(PaperPortfolio())

    with pytest.raises(ValueError, match="timestamps duplicados"):
        session.run(data)


def test_session_does_not_send_real_orders() -> None:
    session = PaperTradingSession(PaperPortfolio())
    result = session.run(_data())

    assert result.execution_authorized is False
    assert result.mode == "simulation-first"


def test_session_can_be_reused_with_a_clean_engine_state() -> None:
    session = PaperTradingSession(PaperPortfolio())
    first = session.run(_data(30))

    assert first.rows == 30

    with pytest.raises(RuntimeError, match="sesión ya ejecutada"):
        session.run(_data(30))
