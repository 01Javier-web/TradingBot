"""Pruebas del ciclo seguro de paper trading."""

import pandas as pd
import pytest

from paper_trading.cycle import run_paper_cycle
from paper_trading.portfolio import PaperPortfolio
from paper_trading.session import PaperTradingSession


def _data(rows: int = 40) -> pd.DataFrame:
    close = pd.Series(range(1, rows + 1), dtype=float)
    return pd.DataFrame({
        "time": pd.date_range("2026-01-01", periods=rows, freq="15min"),
        "open": close,
        "high": close + 1,
        "low": (close - 1).clip(lower=0.1),
        "close": close,
    })


def test_cycle_validates_then_processes_and_reports() -> None:
    session = PaperTradingSession(PaperPortfolio())
    result = run_paper_cycle(_data(), session)

    assert result.rows_processed == 40
    assert result.session.rows == 40
    assert result.session.report.consistent
    assert result.mode == "simulation-first"
    assert result.execution_authorized is False


def test_cycle_rejects_bad_data_before_creating_events() -> None:
    data = _data()
    data.loc[3, "high"] = 0

    session = PaperTradingSession(PaperPortfolio())
    with pytest.raises(ValueError, match="mayores que 0"):
        run_paper_cycle(data, session)

    assert session.engine.history == []
