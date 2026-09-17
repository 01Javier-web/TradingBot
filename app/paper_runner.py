"""Runner de paper trading sobre un snapshot de MT5, sin ejecución real."""

from __future__ import annotations

import argparse

import MetaTrader5 as mt5

from app.mt5_paper_loop import run_mt5_snapshot
from mt5.connection import initialize, last_error, shutdown
from risk.kill_switch import KillSwitch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TradingBot en modo paper trading")
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--timeframe", type=int, default=mt5.TIMEFRAME_M15)
    parser.add_argument("--count", type=int, default=200)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    switch = KillSwitch()

    if not initialize():
        print("ERROR: no se pudo inicializar MetaTrader 5")
        print(f"Error MT5: {last_error()}")
        return 1

    try:
        print(f"Paper Trading | {args.symbol} | velas={args.count}")
        print("MODO SEGURO: no se enviarán órdenes a MT5.")
        events = run_mt5_snapshot(
            args.symbol,
            args.timeframe,
            count=args.count,
            kill_switch=switch,
        )
        for event in events:
            if event != "WAIT":
                print(event)
        print(f"Procesadas: {len(events)} velas")
        return 0
    finally:
        shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
