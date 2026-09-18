"""Serialización determinista de resultados de paper trading."""

from __future__ import annotations

import json
from dataclasses import asdict

from paper_trading.session import PaperSessionResult


def paper_session_to_dict(result: PaperSessionResult) -> dict[str, object]:
    """Convierte una sesión a una estructura JSON-safe y estable."""
    payload = asdict(result)
    payload["events"] = [dict(event) for event in result.events]
    payload["report"] = asdict(result.report)
    payload["audit"] = asdict(result.audit)
    return payload


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
