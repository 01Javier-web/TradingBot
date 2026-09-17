"""Pruebas del exportador de investigación."""

from pathlib import Path

from ai.researcher import ResearchFinding
from analytics.research_report import save_research_finding


def test_research_finding_can_be_saved_as_json(tmp_path: Path) -> None:
    finding = ResearchFinding(2, 1, 1, 0.5, ("hallazgo",))
    destination = tmp_path / "research.json"

    save_research_finding(finding, destination)

    content = destination.read_text(encoding="utf-8")
    assert '"experiments": 2' in content
    assert '"generalization_rate": 0.5' in content
    assert "hallazgo" in content
