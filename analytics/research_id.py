"""Identificador reproducible para corridas de investigación."""

from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

from analytics.research_manifest import ResearchManifest


def build_experiment_id(manifest: ResearchManifest) -> str:
    """Genera un identificador estable a partir del contexto de investigación."""
    payload: dict[str, Any] = {
        "rows": manifest.rows,
        "train_ratio": manifest.train_ratio,
        "data_fingerprint": manifest.data_fingerprint,
        "fast_ema_periods": manifest.fast_ema_periods,
        "slow_ema_periods": manifest.slow_ema_periods,
        "rsi_periods": manifest.rsi_periods,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode("utf-8")).hexdigest()
