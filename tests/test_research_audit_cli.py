"""Pruebas del CLI de auditoría de investigaciones."""

from analytics.research_audit import CatalogAudit
from app.research_audit_cli import format_audit


def test_format_audit_reports_clean_catalog() -> None:
    output = format_audit(CatalogAudit(3, 3, 0, ()))

    assert "Archivos: 3" in output
    assert "Válidos: 3" in output
    assert "Inválidos: 0" in output
    assert "Problemas:" not in output


def test_format_audit_reports_issues() -> None:
    output = format_audit(CatalogAudit(2, 1, 1, ("bad.json: problema",)))

    assert "Inválidos: 1" in output
    assert "- bad.json: problema" in output
    assert "Modo: simulation-first" in output
