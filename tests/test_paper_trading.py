"""Pruebas del portafolio virtual."""

from math import inf, nan

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


@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_portfolio_rejects_non_finite_initial_balance(value: float) -> None:
    with pytest.raises(ValueError):
        PaperPortfolio(value)


@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_portfolio_rejects_non_finite_position_values(value: float) -> None:
    portfolio = PaperPortfolio()

    with pytest.raises(ValueError):
        portfolio.open_position(PositionSide.BUY, value, 1, 95)
    with pytest.raises(ValueError):
        portfolio.open_position(PositionSide.BUY, 100, value, 95)
    with pytest.raises(ValueError):
        portfolio.open_position(PositionSide.BUY, 100, 1, value)


@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_portfolio_rejects_non_finite_prices(value: float) -> None:
    portfolio = PaperPortfolio()

    with pytest.raises(ValueError):
        portfolio.close_position(value)
    with pytest.raises(ValueError):
        portfolio.mark_to_market(value)
