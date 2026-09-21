"""Serialización completa de una corrida de investigación."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai.research_decision import build_research_decision
from ai.research_gate import select_for_validation, validate_selected_candidate
from ai.research_pipeline import ResearchRun
from ai.research_quality import assess_quality
from analytics.research_decision_report import decision_to_dict
from analytics.research_manifest import manifest_to_dict
from analytics.research_report import candidate_summary


def research_run_to_dict(run: ResearchRun) -> dict[str, Any]:
    """Convierte una corrida en un documento JSON estable y auditable."""
    quality = assess_quality(list(run.results))
    selection = select_for_validation(run)
    final_validation = validate_selected_candidate(run, selection)
    decision = decision_to_dict(build_research_decision(run, final_validation=final_validation))
    return {
        "experiment_id": run.experiment_id,
        "manifest": manifest_to_dict(run.manifest),
        "finding": {
            "experiments": run.finding.experiments,
            "profitable_train": run.finding.profitable_train,
            "profitable_test": run.finding.profitable_test,
            "generalization_rate": run.finding.generalization_rate,
            "findings": list(run.finding.findings),
        },
        "validation": {
            "valid": run.evidence.validation.valid,
            "issues": list(run.evidence.validation.issues),
        },
        "quality": {
            "sample_size": quality.sample_size,
            "finite_results": quality.finite_results,
            "positive_train": quality.positive_train,
            "positive_test": quality.positive_test,
            "positive_both": quality.positive_both,
            "generalization_rate": quality.generalization_rate,
            "statistics": {
                "results": quality.statistics.results,
                "metrics_available": quality.statistics.metrics_available,
                "insufficient_test_sample": quality.statistics.insufficient_test_sample,
                "high_test_drawdown": quality.statistics.high_test_drawdown,
                "train_positive_test_negative": quality.statistics.train_positive_test_negative,
                "weak_test_generalization": quality.statistics.weak_test_generalization,
                "median_test_trades": quality.statistics.median_test_trades,
                "median_test_drawdown": quality.statistics.median_test_drawdown,
                "median_test_win_rate": quality.statistics.median_test_win_rate,
                "median_test_profit_factor": quality.statistics.median_test_profit_factor,
                "unbounded_test_profit_factor": quality.statistics.unbounded_test_profit_factor,
                "parameter_variants": quality.statistics.parameter_variants,
                "statistically_incomplete": quality.statistics.statistically_incomplete,
                "warnings": list(quality.statistics.warnings),
            },
        },
        "decision": decision,
        "validation_gate": {
            "selection": {
                "experiment_id": selection.experiment_id,
                "config": {
                    "fast_ema_period": selection.config.fast_ema_period,
                    "slow_ema_period": selection.config.slow_ema_period,
                    "rsi_period": selection.config.rsi_period,
                },
                "train_pnl": selection.train_pnl,
                "train_drawdown": selection.train_drawdown,
                "train_trades": selection.train_trades,
                "candidates": selection.candidates,
            },
            "final_validation": {
                "experiment_id": final_validation.experiment_id,
                "valid": final_validation.valid,
                "config": {
                    "fast_ema_period": final_validation.config.fast_ema_period,
                    "slow_ema_period": final_validation.config.slow_ema_period,
                    "rsi_period": final_validation.config.rsi_period,
                },
                "test_pnl": final_validation.test_pnl,
                "test_trades": final_validation.test_trades,
                "test_drawdown": final_validation.test_drawdown,
                "test_win_rate": final_validation.test_win_rate,
                "test_profit_factor": final_validation.test_profit_factor,
                "issues": list(final_validation.issues),
            },
        },
        "candidates": candidate_summary(run.evidence.candidates),
    }


def save_research_run(run: ResearchRun, path: str | Path, *, overwrite: bool = False) -> None:
    """Guarda una corrida de forma idempotente y evita reemplazos accidentales."""
    if not isinstance(run, ResearchRun):
        raise ValueError("run debe ser ResearchRun")
    destination = Path(path)
    if destination.exists() and destination.is_dir():
        raise ValueError("path debe apuntar a un archivo")
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(
        research_run_to_dict(run),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
        allow_nan=False,
    )
    if destination.exists() and not overwrite:
        existing = destination.read_text(encoding="utf-8")
        if existing != content:
            raise FileExistsError("El archivo ya contiene una corrida diferente.")
        return
    destination.write_text(content, encoding="utf-8")
