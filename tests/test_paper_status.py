from backtesting.models import PositionSide
from analytics.paper_status import build_paper_status, format_paper_status
from paper_trading.portfolio import PaperPortfolio


def test_status_flat_uses_balance_as_equity():
    portfolio = PaperPortfolio(10_000)
    status = build_paper_status(portfolio, [{"action": "WAIT"}])

    assert status.balance == 10_000
    assert status.equity == 10_000
    assert status.unrealized_pnl == 0
    assert status.position == "FLAT"
    assert status.event_counts == {"WAIT": 1}


def test_status_open_position_marks_to_market():
    portfolio = PaperPortfolio(10_000)
    portfolio.open_position(PositionSide.BUY, 100, 2, 98)
    status = build_paper_status(portfolio, [{"action": "OPEN"}], mark_price=103)

    assert status.position == "BUY"
    assert status.entry_price == 100
    assert status.stop_loss == 98
    assert status.quantity == 2
    assert status.equity == 10_006
    assert status.unrealized_pnl == 6


def test_format_status_includes_kill_switch():
    portfolio = PaperPortfolio(10_000)
    status = build_paper_status(
        portfolio,
        [],
        kill_switch_active=True,
        kill_switch_reason="drawdown",
    )
    text = format_paper_status(status)

    assert "PAPER STATUS" in text
    assert "ACTIVO" in text
    assert "drawdown" in text
