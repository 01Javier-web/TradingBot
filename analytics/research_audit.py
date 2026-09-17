"""Auditoría de integridad del catálogo de investigaciones."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from analytics.research_integrity import IntegrityCheck, validate_record_integrity
from analytics.research_registry import load_research_record


@dataclass(frozen=True)
class CatalogAudit:
    """Resultado agregado de la auditoría de registros."""

    files: int
    valid: int
    invalid: int
    issues: tuple[str, ...]


def audit_catalog(directory: str | Path) -> CatalogAudit:
    """Audita todos los JSON del catálogo sin ejecutar ninguna investigación."""
    destination = Path(directory)
    if not destination.exists():
        return CatalogAudit(0, 0, 0, ())

    checks: list[IntegrityCheck] = []
    issues: list[str] = []
    paths = sorted(destination.glob("*.json"))
    for path in paths:
        try:
            check = validate_record_integrity(load_research_record(path))
        except (OSError, ValueError) as exc:
            check = IntegrityCheck(False, (f"No se pudo leer {path.name}: {exc}.",))
        checks.append(check)
        issues.extend(f"{path.name}: {issue}" for issue in check.issues)

    valid = sum(check.valid for check in checks)
    return CatalogAudit(len(checks), valid, len(checks) - valid, tuple(issues))
