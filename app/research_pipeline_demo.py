"""Demo del pipeline completo de evidencia de investigación."""

from __future__ import annotations

from pathlib import Path

from ai.research_pipeline import run_research
from analytics.research_registry import save_research_record
from analytics.research_text import format_research_run
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
    path = save_research_record(run, Path("artifacts/research"))
    print(format_research_run(run))
    print(f"Experiment ID: {run.experiment_id}")
    print(f"Registro: {path}")


if __name__ == "__main__":
    main()
