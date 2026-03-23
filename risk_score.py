from typing import Any, Dict, List


MEDIUM_RISK_THRESHOLD = 20
HIGH_RISK_THRESHOLD = 50


def calculate_risk_score(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate a rule-based risk score from input metrics."""
    score = 0
    reasons: List[str] = []

    dod = float(input_data.get("dod", 0))
    efficiency = float(input_data.get("efficiency", 0))
    dr_capacity = input_data.get("dr_capacity")
    power_kw = input_data.get("power_kw")
    sr_execution_rate = float(input_data.get("sr_execution_rate", 0))
    cycles_per_day = float(input_data.get("cycles_per_day", 0))
    electricity_growth = float(input_data.get("electricity_growth", 0))
    no_load_constraint = bool(input_data.get("no_load_constraint", False))
    energy_double_count = bool(input_data.get("energy_double_count", False))

    if dod > 0.95:
        score += 8
        reasons.append("dod > 0.95")
    if efficiency > 0.9:
        score += 8
        reasons.append("efficiency > 0.9")
    if dr_capacity is not None and power_kw is not None and dr_capacity == power_kw:
        score += 10
        reasons.append("dr_capacity == power_kw")
    if sr_execution_rate >= 0.95:
        score += 8
        reasons.append("sr_execution_rate >= 0.95")
    if cycles_per_day > 1.5:
        score += 10
        reasons.append("cycles_per_day > 1.5")
    if electricity_growth > 0.05:
        score += 10
        reasons.append("electricity_growth > 0.05")
    if no_load_constraint:
        score += 15
        reasons.append("no_load_constraint is true")
    if energy_double_count:
        score += 20
        reasons.append("energy_double_count is true")

    if score >= HIGH_RISK_THRESHOLD:
        level = "high"
    elif score >= MEDIUM_RISK_THRESHOLD:
        level = "medium"
    else:
        level = "low"

    return {
        "score": score,
        "level": level,
        "reasons": reasons,
    }
