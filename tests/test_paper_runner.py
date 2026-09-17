"""Pruebas del CLI de paper trading."""

from __future__ import annotations

import app.paper_runner as runner


def test_parser_defaults() -> None:
    args = runner.build_parser().parse_args([])
    assert args.symbol == "EURUSD"
    assert args.count == 200


def test_main_reports_mt5_initialization_failure(monkeypatch, capsys) -> None:
    monkeypatch.setattr(runner, "initialize", lambda: False)
    monkeypatch.setattr(runner, "last_error", lambda: (-6, "Terminal: Authorization failed"))

    assert runner.main() == 1
    output = capsys.readouterr().out
    assert "no se pudo inicializar" in output
