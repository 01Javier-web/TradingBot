"""Demo local del pipeline completo de evidencia de investigación."""

from __future__ import annotations

from ai.research_evidence import build_evidence
from ai.research_pipeline import run_research
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
    evidence = build_evidence(list(run.results))

    print("=== TradingBot Research Evidence Demo ===")
    print(f"Resultados: {len(run.results)}")
    print(f"Validación: {'OK' if evidence.validation.valid else 'ERROR'}")
    print(f"Candidatos consistentes: {sum(item.consistent for item in evidence.candidates)}")
    for item in run.finding.findings:
        print(item)
    print("Modo: simulation-first")
    print("Ejecución real: BLOQUEADA")


if __name__ == "__main__":
    main()
