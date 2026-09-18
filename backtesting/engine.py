"""Motor determinista de backtesting, sin ejecución real."""

from __future__ import annotations

from math import isfinite

import pandas as pd

from backtesting.models import BacktestResult, PositionSide, Trade
from backtesting.metrics import max_drawdown, profit_factor, win_rate
from data.quality import validate_time_series
from strategy.signals import Signal, StrategyConfig, generate_signals


class BacktestEngine:
    """Simula entradas en la vela siguiente a la señal para evitar look-ahead."""

    def __init__(
        self,
        initial_balance: float = 10_000.0,
        quantity: float = 1.0,
        commission: float = 0.0,
        spread: float = 0.0,
    ) -> None:
        values = (initial_balance, quantity, commission, spread)
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
            raise ValueError("Los parámetros de backtest deben ser numéricos")
        if not all(isfinite(float(value)) for value in values):
            raise ValueError("Los parámetros de backtest deben ser finitos")
        if initial_balance <= 0 or quantity <= 0 or commission < 0 or spread < 0:
            raise ValueError("Parámetros de backtest inválidos")
        self.initial_balance = float(initial_balance)
        self.quantity = float(quantity)
        self.commission = float(commission)
        self.spread = float(spread)

    def run(self, df: pd.DataFrame, config: StrategyConfig | None = None) -> BacktestResult:
        """Ejecuta un backtest solo sobre datos de mercado estrictamente validados."""
        data = validate_time_series(df)

        if len(data) < 2:
            return BacktestResult(
                self.initial_balance,
                self.initial_balance,
                (),
                (self.initial_balance,),
            )

        data = generate_signals(data, config).reset_index(drop=True)
        balance = self.initial_balance
        equity = [balance]
        position: PositionSide | None = None
        entry_price = 0.0
        entry_time = None
        trades: list[Trade] = []

        for i in range(len(data) - 1):
            signal = data.loc[i, "signal"]
            next_price = float(data.loc[i + 1, "open"])
            next_close = float(data.loc[i + 1, "close"])
            next_time = data.loc[i + 1, "time"]

            if position is None and signal in (Signal.BUY, Signal.SELL):
                # No se abre una operación en la última vela: no existe una
                # vela posterior para representar una salida temporalmente posterior.
                if i == len(data) - 2:
                    if position is None:
                        equity.append(balance)
                    continue
                position = PositionSide(signal.value)
                entry_price = (
                    next_price + self.spread / 2
                    if position is PositionSide.BUY
                    else next_price - self.spread / 2
                )
                entry_time = next_time
            elif position is not None and (
                (position is PositionSide.BUY and signal is Signal.SELL)
                or (position is PositionSide.SELL and signal is Signal.BUY)
            ):
                exit_price = (
                    next_price - self.spread / 2
                    if position is PositionSide.BUY
                    else next_price + self.spread / 2
                )
                direction = 1 if position is PositionSide.BUY else -1
                gross = (exit_price - entry_price) * direction * self.quantity
                trade = Trade(
                    entry_time,
                    next_time,
                    position,
                    entry_price,
                    exit_price,
                    self.quantity,
                    gross,
                    self.commission,
                )
                balance += trade.net_pnl
                trades.append(trade)
                position = None

            if position is None:
                equity.append(balance)
            else:
                direction = 1 if position is PositionSide.BUY else -1
                unrealized = (next_close - entry_price) * direction * self.quantity
                equity.append(balance + unrealized)

        # Cierre forzoso al último close solo si la entrada ocurrió antes.
        if position is not None:
            if entry_time is None or entry_time >= data.iloc[-1]["time"]:
                raise RuntimeError("La posición no puede cerrarse en el mismo instante de entrada")
            exit_price = float(data.iloc[-1]["close"])
            direction = 1 if position is PositionSide.BUY else -1
            gross = (exit_price - entry_price) * direction * self.quantity
            trade = Trade(
                entry_time,
                data.iloc[-1]["time"],
                position,
                entry_price,
                exit_price,
                self.quantity,
                gross,
                self.commission,
            )
            balance += trade.net_pnl
            trades.append(trade)
            equity[-1] = balance
        elif equity[-1] != balance:
            equity[-1] = balance

        return BacktestResult(
            self.initial_balance,
            balance,
            tuple(trades),
            tuple(equity),
        )


__all__ = ["BacktestEngine", "BacktestResult", "max_drawdown", "profit_factor", "win_rate"]
