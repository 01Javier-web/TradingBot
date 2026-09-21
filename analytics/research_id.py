"""Identificador reproducible para corridas de investigación."""

from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

from analytics.research_manifest import ResearchManifest, manifest_to_dict


def build_experiment_id(manifest: ResearchManifest) -> str:
    """Genera un ID estable a partir de todo el manifiesto."""
    if not isinstance(manifest, ResearchManifest):
        raise ValueError("manifest debe ser ResearchManifest")
    payload: dict[str, Any] = manifest_to_dict(manifest)
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return sha256(canonical.encode("utf-8")).hexdigest()
