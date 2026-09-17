"""CLI local para inspeccionar el gate de revisión de una investigación."""

from __future__ import annotations

from ai.research_decision import build_research_decision
from ai.research_pipeline import run_research
from analytics.research_decision_report import decision_to_dict
from app.research_demo import synthetic_data
from backtesting.optimizer import ParameterGrid


def main() -> None:
    run = run_research(
        synthetic_data(),
        ParameterGrid(
            fast_ema_periods=(5, 10),
            slow_ema_periods=(20, 30),
            rsi_periods=(14,),
        ),
    )
    decision = build_research_decision(run)
    report = decision_to_dict(decision)

    print("=== TradingBot Research Decision ===")
    print(f"Revisión requerida: {'SÍ' if report['review_required'] else 'NO'}")
    for reason in report["reasons"]:
        print(f"- {reason}")
    print("Ejecución autorizada: NO")
    print("Modo: simulation-first")


if __name__ == "__main__":
    main()
