"""Serialización determinista de resultados de paper trading."""

from __future__ import annotations

import json
import math
from dataclasses import asdict

from paper_trading.session import PaperSessionResult


def _json_safe(value: object) -> object:
    """Normaliza valores no finitos para producir JSON estándar."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def paper_session_to_dict(result: PaperSessionResult) -> dict[str, object]:
    """Convierte una sesión a una estructura JSON-safe y estable."""
    payload = asdict(result)
    payload["events"] = [dict(event) for event in result.events]
    payload["report"] = asdict(result.report)
    payload["audit"] = asdict(result.audit)
    return _json_safe(payload)  # type: ignore[return-value]


def paper_session_to_json(result: PaperSessionResult) -> str:
    """Genera JSON determinista para logs y evidencia reproducible."""
    return json.dumps(
        paper_session_to_dict(result),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


__all__ = ["paper_session_to_dict", "paper_session_to_json"]
