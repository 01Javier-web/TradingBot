"""CLI de observabilidad para una sesión de paper trading."""

from __future__ import annotations

import argparse

from analytics.paper_status import build_paper_status, format_paper_status
from paper_trading.portfolio import PaperPortfolio


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Muestra el estado de un portafolio virtual")
    parser.add_argument("--balance", type=float, default=10_000.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    portfolio = PaperPortfolio(args.balance)
    status = build_paper_status(portfolio, [])
    print(format_paper_status(status))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
