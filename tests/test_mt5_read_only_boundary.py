"""Protege la frontera de solo lectura de la integración MT5.

El paper trading no debe depender de esta capa ni enviar órdenes.
"""

from pathlib import Path


def test_mt5_account_and_connection_do_not_expose_order_submission() -> None:
    root = Path(__file__).resolve().parents[1]
    for relative in ("mt5/account.py", "mt5/connection.py"):
        source = (root / relative).read_text(encoding="utf-8")
        assert "order_send" not in source
        assert "positions_get" not in source
        assert "order_modify" not in source


def test_paper_trading_engine_does_not_import_mt5_package() -> None:
    root = Path(__file__).resolve().parents[1]
    source = (root / "paper_trading/engine.py").read_text(encoding="utf-8")
    assert "import MetaTrader5" not in source
    assert "from mt5" not in source
    assert "order_send" not in source
