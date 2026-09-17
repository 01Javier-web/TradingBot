"""Pruebas del catálogo de investigaciones."""

from pathlib import Path
import json

from analytics.research_catalog import catalog_records, catalog_to_dict, save_catalog
from analytics.research_registry import save_research_record
from app.research_demo import synthetic_data
from ai.research_pipeline import run_research
from backtesting.optimizer import ParameterGrid


def _run(fast: tuple[int, ...] = (5,)):
    return run_research(
        synthetic_data(80),
        ParameterGrid(fast_ema_periods=fast, slow_ema_periods=(20,), rsi_periods=(14,)),
    )


def test_catalog_records_reads_registered_experiments(tmp_path: Path) -> None:
    directory = tmp_path / "research"
    save_research_record(_run(), directory)
    save_research_record(_run((10,)), directory)

    records = catalog_records(directory)

    assert len(records) == 2
    assert records[0].experiment_id <= records[1].experiment_id


def test_catalog_to_dict_is_serializable(tmp_path: Path) -> None:
    directory = tmp_path / "research"
    save_research_record(_run(), directory)
    records = catalog_records(directory)

    document = catalog_to_dict(records)

    assert len(document) == 1
    assert document[0]["experiment_id"] == records[0].experiment_id
    json.dumps(document)


def test_save_catalog_writes_index(tmp_path: Path) -> None:
    directory = tmp_path / "research"
    destination = tmp_path / "catalog" / "index.json"
    save_research_record(_run(), directory)
    records = catalog_records(directory)

    save_catalog(records, destination)

    assert destination.exists()
    assert json.loads(destination.read_text(encoding="utf-8"))[0]["rows"] == 80
