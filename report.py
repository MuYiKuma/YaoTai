from __future__ import annotations

from collections.abc import Iterable
from numbers import Number
from typing import Any


def _extract_risk_score(warnings: Any) -> float:
    """Extract a numeric risk score from the warnings payload.

    Supported inputs:
    - a number, e.g. 55
    - a dict containing ``risk_score``
    - an iterable containing numbers and/or dicts with ``risk_score``

    Any unsupported item is ignored.
    """
    if isinstance(warnings, Number):
        return float(warnings)

    if isinstance(warnings, dict):
        risk_score = warnings.get("risk_score", 0)
        return float(risk_score) if isinstance(risk_score, Number) else 0.0

    if isinstance(warnings, Iterable) and not isinstance(warnings, (str, bytes)):
        score = 0.0
        for item in warnings:
            if isinstance(item, Number):
                score += float(item)
            elif isinstance(item, dict) and isinstance(item.get("risk_score"), Number):
                score += float(item["risk_score"])
        return score

    return 0.0


def _normalize_warnings(warnings: Any) -> list[Any]:
    if warnings is None:
        return []
    if isinstance(warnings, list):
        return warnings
    if isinstance(warnings, tuple):
        return list(warnings)
    return [warnings]


def generate_report(arbitrage: float, dr: float, sr: float, warnings: Any) -> dict[str, Any]:
    """Generate a revenue report with a risk classification.

    ``risk_level`` is determined from the extracted ``risk_score``:
    - > 70: high
    - 40 ~ 70: medium
    - < 40: low
    """
    total_revenue = arbitrage + dr + sr
    risk_score = _extract_risk_score(warnings)

    if risk_score > 70:
        risk_level = "high"
    elif risk_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "total_revenue": total_revenue,
        "breakdown": {
            "arbitrage": arbitrage,
            "dr": dr,
            "sr": sr,
        },
        "warnings": _normalize_warnings(warnings),
        "risk_level": risk_level,
    }
