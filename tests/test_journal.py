"""Pruebas del registro de operaciones."""

import json

from paper_trading.journal import TradeJournal


def test_journal_records_and_saves_jsonl(tmp_path) -> None:
    journal = TradeJournal()
    journal.record("OPEN", side="BUY", price=100.0, quantity=1.0)
    journal.record("CLOSE", side="BUY", price=105.0, quantity=1.0, pnl=5.0)

    destination = tmp_path / "trades.jsonl"
    journal.save_jsonl(destination)

    lines = destination.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["event"] == "OPEN"
    assert json.loads(lines[1])["pnl"] == 5.0
