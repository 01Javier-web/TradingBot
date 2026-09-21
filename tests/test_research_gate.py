"""Pruebas del gate que separa selección train y validación test."""

from dataclasses import replace

import pytest

from ai.research_evidence import build_evidence
from ai.research_gate import (
    FinalValidation,
    ValidationSelection,
    select_for_validation,
    validate_selected_candidate,
)
from ai.research_pipeline import run_research
from ai.researcher import summarize_optimization
from app.research_demo import synthetic_data
from backtesting.optimizer import ParameterGrid
from strategy.signals import StrategyConfig


def _run():
    return run_research(
        synthetic_data(80),
        ParameterGrid(
            fast_ema_periods=(5, 10),
            slow_ema_periods=(20, 30),
            rsi_periods=(14,),
        ),
    )


def _replace_results(run, results):
    return run.__class__(
        results=tuple(results),
        finding=summarize_optimization(list(results)),
        evidence=build_evidence(list(results)),
        manifest=run.manifest,
        experiment_id=run.experiment_id,
    )


def test_selection_uses_train_pnl_not_test_pnl() -> None:
    run = _run()
    first, second = run.results[:2]

    train_winner = replace(first, train_pnl=100.0, test_pnl=-999.0)
    test_winner = replace(second, train_pnl=50.0, test_pnl=999.0)
    altered_results = (train_winner, test_winner, *run.results[2:])
    altered = _replace_results(run, altered_results)

    selection = select_for_validation(altered)

    assert selection.config == train_winner.config
    assert selection.train_pnl == 100.0


def test_selection_records_experiment_identity() -> None:
    run = _run()

    selection = select_for_validation(run)

    assert selection.experiment_id == run.experiment_id
    assert selection.candidates == len(run.results)
    assert selection.config in {result.config for result in run.results}


def test_final_validation_uses_selected_configuration() -> None:
    run = _run()
    selection = select_for_validation(run)

    validation = validate_selected_candidate(run, selection)

    selected = next(result for result in run.results if result.config == selection.config)
    assert isinstance(validation, FinalValidation)
    assert validation.valid is True
    assert validation.config == selected.config
    assert validation.test_pnl == selected.test_pnl
    assert validation.test_trades == selected.test_trades
    assert validation.test_drawdown == selected.test_drawdown
    assert validation.test_win_rate == selected.test_win_rate
    assert validation.test_profit_factor == selected.test_profit_factor
    assert validation.complete is True


def test_final_validation_rejects_different_experiment() -> None:
    run = _run()
    selection = select_for_validation(run)
    foreign = ValidationSelection(
        experiment_id="0" * 64,
        config=selection.config,
        train_pnl=selection.train_pnl,
        train_drawdown=selection.train_drawdown,
        train_trades=selection.train_trades,
        candidates=selection.candidates,
    )

    validation = validate_selected_candidate(run, foreign)

    assert validation.valid is False
    assert any("experimento diferente" in issue for issue in validation.issues)


def test_final_validation_rejects_unknown_configuration() -> None:
    run = _run()
    selection = select_for_validation(run)
    foreign_config = StrategyConfig(fast_ema_period=3, slow_ema_period=50, rsi_period=14)
    foreign = ValidationSelection(
        experiment_id=selection.experiment_id,
        config=foreign_config,
        train_pnl=selection.train_pnl,
        train_drawdown=selection.train_drawdown,
        train_trades=selection.train_trades,
        candidates=selection.candidates,
    )

    validation = validate_selected_candidate(run, foreign)

    assert validation.valid is False
    assert any("no identifica exactamente" in issue for issue in validation.issues)


def test_final_validation_rejects_incomplete_test_metrics() -> None:
    run = _run()
    selection = select_for_validation(run)
    target = next(result for result in run.results if result.config == selection.config)
    incomplete = replace(target, test_trades=None)

    altered_results = tuple(
        incomplete if item.config == target.config else item
        for item in run.results
    )
    altered = _replace_results(run, altered_results)

    validation = validate_selected_candidate(altered, selection)

    assert validation.valid is False
    assert validation.complete is False
    assert validation.test_pnl == target.test_pnl
    assert any("métricas principales de test" in issue for issue in validation.issues)


def test_selection_requires_research_run() -> None:
    with pytest.raises(ValueError, match="ResearchRun"):
        select_for_validation(None)  # type: ignore[arg-type]
