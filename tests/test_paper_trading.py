"""Pruebas del portafolio virtual."""

import pytest

from backtesting.models import PositionSide
from paper_trading.portfolio import PaperPortfolio


def test_virtual_buy_position_updates_balance() -> None:
    portfolio = PaperPortfolio(1_000)
    portfolio.open_position(PositionSide.BUY, price=100, quantity=2, stop_loss=95)
    assert portfolio.mark_to_market(110) == pytest.approx(1_020)
    assert portfolio.close_position(110) == pytest.approx(20)
    assert portfolio.balance == pytest.approx(1_020)


def test_virtual_sell_position() -> None:
    portfolio = PaperPortfolio(1_000)
    portfolio.open_position(PositionSide.SELL, price=100, quantity=2, stop_loss=105)
    assert portfolio.close_position(90) == pytest.approx(20)


def test_only_one_position_is_allowed() -> None:
    portfolio = PaperPortfolio()
    portfolio.open_position(PositionSide.BUY, 100, 1, 95)
    with pytest.raises(ValueError):
        portfolio.open_position(PositionSide.SELL, 100, 1, 105)
