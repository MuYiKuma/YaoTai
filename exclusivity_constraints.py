from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Tuple


def _clamp(value: float, minimum: float = 0.0, maximum: float | None = None) -> float:
    value = max(minimum, value)
    if maximum is not None:
        value = min(value, maximum)
    return value


def apply_exclusivity_constraints(input_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Apply exclusivity rules between DR, SR, and arbitrage usage.

    Expected keys in ``input_data`` (all optional unless noted):
      - capacity_kwh: battery energy capacity
      - dod: depth of discharge multiplier, defaults to 1.0
      - soh: state of health multiplier, defaults to 1.0
      - dr_enabled: bool
      - sr_enabled: bool
      - arbitrage_cycles: planned arbitrage cycles
      - dr_energy_kwh: planned DR energy usage
      - sr_reserve_ratio: capacity ratio reserved for SR, defaults to 0.20 when SR is enabled
      - dr_capacity_reduction_ratio: capacity haircut from DR, defaults to 0.30 when DR is enabled
      - arbitrage_cycle_reduction_ratio: arbitrage haircut from DR, defaults to 0.30 when DR is enabled
      - arbitrage_energy_kwh_per_cycle: energy required per arbitrage cycle. If omitted,
        capacity_kwh * dod * soh is used as a conservative default.

    Returns:
      (adjusted_input_data, constraint_log)
    """

    data = deepcopy(input_data)
    constraint_log: List[Dict[str, Any]] = []

    capacity_kwh = float(data.get("capacity_kwh", 0.0) or 0.0)
    dod = _clamp(float(data.get("dod", 1.0) or 1.0), 0.0, 1.0)
    soh = _clamp(float(data.get("soh", 1.0) or 1.0), 0.0, 1.0)

    total_energy_budget = capacity_kwh * dod * soh
    available_capacity_kwh = total_energy_budget
    data["effective_energy_budget_kwh"] = total_energy_budget

    dr_enabled = bool(data.get("dr_enabled", False))
    sr_enabled = bool(data.get("sr_enabled", False))

    arbitrage_cycles = _clamp(float(data.get("arbitrage_cycles", 0.0) or 0.0))
    dr_energy_kwh = _clamp(float(data.get("dr_energy_kwh", 0.0) or 0.0))

    default_energy_per_cycle = total_energy_budget if total_energy_budget > 0 else 1.0
    arbitrage_energy_kwh_per_cycle = _clamp(
        float(data.get("arbitrage_energy_kwh_per_cycle", default_energy_per_cycle) or default_energy_per_cycle)
    )

    def log_adjustment(rule: str, field: str, before: float, after: float, reason: str) -> None:
        if abs(before - after) > 1e-9:
            constraint_log.append(
                {
                    "rule": rule,
                    "field": field,
                    "before": before,
                    "after": after,
                    "reason": reason,
                }
            )

    if dr_enabled:
        cycle_reduction_ratio = _clamp(
            float(data.get("arbitrage_cycle_reduction_ratio", 0.30) or 0.30), 0.20, 0.50
        )
        capacity_reduction_ratio = _clamp(
            float(data.get("dr_capacity_reduction_ratio", 0.30) or 0.30), 0.20, 0.50
        )

        reduced_cycles = arbitrage_cycles * (1.0 - cycle_reduction_ratio)
        log_adjustment(
            "dr_reduces_arbitrage",
            "arbitrage_cycles",
            arbitrage_cycles,
            reduced_cycles,
            f"DR enabled, arbitrage cycles reduced by {cycle_reduction_ratio:.0%}.",
        )
        arbitrage_cycles = reduced_cycles

        reduced_capacity = available_capacity_kwh * (1.0 - capacity_reduction_ratio)
        log_adjustment(
            "dr_reduces_capacity",
            "available_capacity_kwh",
            available_capacity_kwh,
            reduced_capacity,
            f"DR enabled, available capacity reduced by {capacity_reduction_ratio:.0%}.",
        )
        available_capacity_kwh = reduced_capacity

    sr_reserved_kwh = 0.0
    if sr_enabled:
        sr_reserve_ratio = _clamp(float(data.get("sr_reserve_ratio", 0.20) or 0.20), 0.0, 1.0)
        sr_reserved_kwh = available_capacity_kwh * sr_reserve_ratio
        post_sr_capacity = max(available_capacity_kwh - sr_reserved_kwh, 0.0)
        log_adjustment(
            "sr_reserves_capacity",
            "available_capacity_kwh",
            available_capacity_kwh,
            post_sr_capacity,
            f"SR enabled, reserved {sr_reserve_ratio:.0%} of remaining capacity.",
        )
        available_capacity_kwh = post_sr_capacity

        dr_cap_before_sr = dr_energy_kwh
        dr_energy_kwh = min(dr_energy_kwh, available_capacity_kwh)
        log_adjustment(
            "sr_reduces_dr_capacity",
            "dr_energy_kwh",
            dr_cap_before_sr,
            dr_energy_kwh,
            "SR reservation reduced DR-available energy.",
        )

    arbitrage_energy_kwh = arbitrage_cycles * arbitrage_energy_kwh_per_cycle
    if arbitrage_energy_kwh > available_capacity_kwh and arbitrage_energy_kwh_per_cycle > 0:
        adjusted_cycles = available_capacity_kwh / arbitrage_energy_kwh_per_cycle
        log_adjustment(
            "arbitrage_limited_by_capacity",
            "arbitrage_cycles",
            arbitrage_cycles,
            adjusted_cycles,
            "Arbitrage usage exceeded remaining capacity and was scaled down.",
        )
        arbitrage_cycles = adjusted_cycles
        arbitrage_energy_kwh = arbitrage_cycles * arbitrage_energy_kwh_per_cycle

    total_energy_used = dr_energy_kwh + arbitrage_energy_kwh
    max_energy_allowed = min(total_energy_budget, available_capacity_kwh)

    if total_energy_used > max_energy_allowed:
        overflow = total_energy_used - max_energy_allowed

        dr_before = dr_energy_kwh
        dr_energy_kwh = max(dr_energy_kwh - overflow, 0.0)
        overflow -= dr_before - dr_energy_kwh
        log_adjustment(
            "resolve_double_count",
            "dr_energy_kwh",
            dr_before,
            dr_energy_kwh,
            "Total DR + arbitrage energy exceeded the exclusivity limit, so DR was reduced first.",
        )

        if overflow > 1e-9 and arbitrage_energy_kwh_per_cycle > 0:
            cycles_before = arbitrage_cycles
            max_arbitrage_energy = max(arbitrage_energy_kwh - overflow, 0.0)
            arbitrage_cycles = max_arbitrage_energy / arbitrage_energy_kwh_per_cycle
            arbitrage_energy_kwh = arbitrage_cycles * arbitrage_energy_kwh_per_cycle
            log_adjustment(
                "resolve_double_count",
                "arbitrage_cycles",
                cycles_before,
                arbitrage_cycles,
                "Remaining overflow was removed from arbitrage to avoid double counting energy.",
            )

    total_energy_used = dr_energy_kwh + arbitrage_cycles * arbitrage_energy_kwh_per_cycle
    data.update(
        {
            "capacity_kwh": capacity_kwh,
            "dod": dod,
            "soh": soh,
            "dr_enabled": dr_enabled,
            "sr_enabled": sr_enabled,
            "available_capacity_kwh": available_capacity_kwh,
            "sr_reserved_kwh": sr_reserved_kwh,
            "dr_energy_kwh": dr_energy_kwh,
            "arbitrage_cycles": arbitrage_cycles,
            "arbitrage_energy_kwh_per_cycle": arbitrage_energy_kwh_per_cycle,
            "arbitrage_energy_kwh": arbitrage_cycles * arbitrage_energy_kwh_per_cycle,
            "total_energy_used_kwh": total_energy_used,
            "max_energy_allowed_kwh": max_energy_allowed,
        }
    )

    constraint_log.append(
        {
            "rule": "final_energy_check",
            "field": "total_energy_used_kwh",
            "before": total_energy_used,
            "after": total_energy_used,
            "reason": (
                "Verified no double counting: total_energy_used_kwh <= "
                "min(effective_energy_budget_kwh, available_capacity_kwh)."
            ),
        }
    )

    return data, constraint_log
