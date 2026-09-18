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
        manifest_data = document["manifest"]
        manifest = ResearchManifest(
            rows=int(manifest_data["rows"]),
            train_ratio=float(manifest_data["train_ratio"]),
            data_fingerprint=str(manifest_data["data_fingerprint"]),
            fast_ema_periods=tuple(int(value) for value in manifest_data["fast_ema_periods"]),
            slow_ema_periods=tuple(int(value) for value in manifest_data["slow_ema_periods"]),
            rsi_periods=tuple(int(value) for value in manifest_data["rsi_periods"]),
            schema_version=str(manifest_data.get("schema_version", "research-v1")),
        )
        expected_id = build_experiment_id(manifest)
        if document["experiment_id"] != expected_id:
            issues.append("experiment_id no corresponde al manifiesto.")
    except (KeyError, TypeError, ValueError) as exc:
        issues.append(f"Estructura de manifiesto inválida: {exc}.")

    return IntegrityCheck(valid=not issues, issues=tuple(issues))
