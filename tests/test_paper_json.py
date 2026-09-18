"""Pruebas de serialización reproducible."""

import json

import pandas as pd

from analytics.paper_json import paper_session_to_json
from paper_trading.portfolio import PaperPortfolio
from paper_trading.session import PaperTradingSession


def _data() -> pd.DataFrame:
    close = pd.Series(range(1, 35), dtype=float)
    return pd.DataFrame({
        "time": pd.date_range("2026-01-01", periods=len(close), freq="15min"),
        "open": close,
        "high": close + 1,
        "low": (close - 1).clip(lower=0.1),
        "close": close,
    })


def test_paper_json_is_valid_and_deterministic() -> None:
    result = PaperTradingSession(PaperPortfolio()).run(_data())
    first = paper_session_to_json(result)
    second = paper_session_to_json(result)

    assert first == second
    payload = json.loads(first)
    assert payload["mode"] == "simulation-first"
    assert payload["execution_authorized"] is False
    assert payload["audit"]["valid"] is True


def test_paper_json_is_sorted_for_reproducible_diffs() -> None:
    result = PaperTradingSession(PaperPortfolio()).run(_data())
    serialized = paper_session_to_json(result)

    assert serialized.startswith('{"audit":')
    assert '"events":' in serialized
