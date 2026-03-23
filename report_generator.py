from __future__ import annotations

from typing import Any


def _to_float(value: Any, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number") from exc


def generate_analysis_report(results: dict[str, Any]) -> dict[str, Any]:
    """Generate a normalized analysis report from revenue scenarios.

    Expected input keys:
    - proposal_revenue
    - standard_revenue
    - conservative_revenue
    - optional issues / key_issues
    """

    if not isinstance(results, dict):
        raise ValueError("results must be a dictionary")

    proposal = _to_float(results.get("proposal_revenue"), "proposal_revenue")
    standard = _to_float(results.get("standard_revenue"), "standard_revenue")
    conservative = _to_float(results.get("conservative_revenue"), "conservative_revenue")

    provided_issues = results.get("key_issues", results.get("issues", []))
    if provided_issues is None:
        provided_issues = []
    if not isinstance(provided_issues, list):
        raise ValueError("key_issues must be a list")

    key_issues = list(provided_issues)

    proposal_gap_ratio = ((proposal - standard) / standard) if standard else 0.0
    scenario_gap_ratio = ((standard - conservative) / standard) if standard else 0.0

    conclusions: list[str] = []

    if proposal_gap_ratio > 0.3:
        conclusions.append("模型偏樂觀")
        key_issues.append("proposal 與 standard 差距過大")

    if abs(scenario_gap_ratio) <= 0.1:
        conclusions.append("模型穩健")

    if abs(proposal_gap_ratio) > 0.3 or abs(scenario_gap_ratio) > 0.3:
        conclusions.append("需重新評估")
        key_issues.append("情境差距超過 30%")

    if not conclusions:
        conclusions.append("模型落在合理區間")

    unique_issues = []
    seen = set()
    for issue in key_issues:
        if issue not in seen:
            seen.add(issue)
            unique_issues.append(issue)

    risk_score = min(
        100,
        round(abs(proposal_gap_ratio) * 100 * 0.6 + abs(scenario_gap_ratio) * 100 * 0.4, 2),
    )

    return {
        "proposal_revenue": proposal,
        "standard_revenue": standard,
        "conservative_revenue": conservative,
        "risk_score": risk_score,
        "key_issues": unique_issues,
        "conclusion": "；".join(conclusions),
    }
