"""Comprobaciones de integridad para investigaciones almacenadas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from analytics.research_id import build_experiment_id
from analytics.research_manifest import ResearchManifest


@dataclass(frozen=True)
class IntegrityCheck:
    """Resultado de comprobar que un registro conserva su identidad."""

    valid: bool
    issues: tuple[str, ...]


def validate_record_integrity(document: dict[str, Any]) -> IntegrityCheck:
    """Verifica estructura mínima y que el ID corresponda al manifiesto."""
    issues: list[str] = []
    try:
        if not isinstance(document, dict):
            raise TypeError("el documento debe ser un objeto")
        experiment_id = document.get("experiment_id")
        if not isinstance(experiment_id, str):
            raise ValueError("experiment_id debe ser texto")
        manifest_data = document["manifest"]
        if not isinstance(manifest_data, dict):
            raise TypeError("manifest debe ser un objeto")
        manifest = ResearchManifest(
            rows=manifest_data["rows"],
            train_ratio=manifest_data["train_ratio"],
            data_fingerprint=manifest_data["data_fingerprint"],
            fast_ema_periods=tuple(manifest_data["fast_ema_periods"]),
            slow_ema_periods=tuple(manifest_data["slow_ema_periods"]),
            rsi_periods=tuple(manifest_data["rsi_periods"]),
            schema_version=manifest_data.get("schema_version", "research-v1"),
        )
        expected_id = build_experiment_id(manifest)
        if experiment_id != expected_id:
            issues.append("experiment_id no corresponde al manifiesto.")
        for section in ("finding", "validation", "quality", "decision", "candidates"):
            expected_type = list if section == "candidates" else dict
            if not isinstance(document.get(section), expected_type):
                issues.append(f"{section} debe ser {'una lista' if section == 'candidates' else 'un objeto'}.")
    except (KeyError, TypeError, ValueError) as exc:
        issues.append(f"Estructura de manifiesto inválida: {exc}.")

    return IntegrityCheck(valid=not issues, issues=tuple(issues))
