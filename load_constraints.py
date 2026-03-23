from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Tuple


DR_FLAG_CANDIDATES = ("is_dr_period", "dr_period", "is_dr", "dr_flag")
LOAD_CANDIDATES = ("current_load_kw", "site_load_kw", "load_kw", "avg_load_kw")
DR_CAPACITY_CANDIDATES = ("dr_capacity_kw", "dr_capacity", "available_dr_capacity_kw")
ENERGY_CANDIDATES = ("energy_kwh", "charge_energy_kwh", "available_energy_kwh")


class LoadConstraintError(ValueError):
    """Raised when required fields are missing or invalid."""



def _first_existing(record: Dict[str, Any], candidates: tuple[str, ...]) -> str | None:
    return next((name for name in candidates if name in record), None)



def _to_bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)



def _to_number(value: Any, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise LoadConstraintError(f"Field '{field_name}' must be numeric, got {value!r}") from exc



def _normalize_input(input_data: Any) -> List[Dict[str, Any]]:
    if isinstance(input_data, list):
        if not all(isinstance(item, dict) for item in input_data):
            raise TypeError("input_data must be a list of dictionaries")
        return deepcopy(input_data)
    raise TypeError("input_data must be a list of dictionaries")



def apply_load_constraints(input_data: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Apply contract capacity and DR load constraints.

    Required fields per row:
    - power_kw
    - contract_capacity_kw
    - avg_load_kw

    Optional fields per row:
    - energy_kwh / charge_energy_kwh / available_energy_kwh
    - is_dr_period / dr_period / is_dr / dr_flag
    - dr_capacity_kw / dr_capacity / available_dr_capacity_kw
    - current_load_kw / site_load_kw / load_kw
      (falls back to avg_load_kw if omitted)
    """
    adjusted_input = _normalize_input(input_data)
    load_constraint_log: List[Dict[str, Any]] = []

    for idx, row in enumerate(adjusted_input):
        for field in ("power_kw", "contract_capacity_kw", "avg_load_kw"):
            if field not in row:
                raise LoadConstraintError(f"Row {idx} is missing required field '{field}'")

        power_kw = _to_number(row["power_kw"], "power_kw")
        contract_capacity_kw = _to_number(row["contract_capacity_kw"], "contract_capacity_kw")
        avg_load_kw = _to_number(row["avg_load_kw"], "avg_load_kw")

        available_charge = max(contract_capacity_kw - avg_load_kw, 0.0)
        row["contract_capacity_kw"] = contract_capacity_kw
        row["avg_load_kw"] = avg_load_kw
        row["available_charge_kw"] = available_charge

        adjusted_power = power_kw
        constraint_sources: List[str] = []

        if available_charge < adjusted_power:
            adjusted_power = available_charge
            constraint_sources.append("contract_capacity")

        dr_flag_field = _first_existing(row, DR_FLAG_CANDIDATES)
        is_dr_period = _to_bool(row[dr_flag_field]) if dr_flag_field else False

        load_field = _first_existing(row, LOAD_CANDIDATES) or "avg_load_kw"
        current_load_kw = _to_number(row[load_field], load_field)

        available_dr_capacity = None
        dr_capacity_field = _first_existing(row, DR_CAPACITY_CANDIDATES)
        original_dr_capacity = None
        adjusted_dr_capacity = None

        if is_dr_period:
            available_dr_capacity = max(contract_capacity_kw - current_load_kw, 0.0)
            row["available_dr_capacity_kw"] = available_dr_capacity

            if available_dr_capacity < adjusted_power:
                adjusted_power = available_dr_capacity
                constraint_sources.append("dr_capacity")

            if dr_capacity_field:
                original_dr_capacity = _to_number(row[dr_capacity_field], dr_capacity_field)
                adjusted_dr_capacity = min(original_dr_capacity, available_dr_capacity)
                if adjusted_dr_capacity < original_dr_capacity:
                    row[dr_capacity_field] = adjusted_dr_capacity
                    constraint_sources.append("dr_capacity_reduced")
                else:
                    row[dr_capacity_field] = original_dr_capacity
                    adjusted_dr_capacity = original_dr_capacity
        elif dr_capacity_field:
            row[dr_capacity_field] = _to_number(row[dr_capacity_field], dr_capacity_field)

        row["power_kw"] = adjusted_power

        energy_field = _first_existing(row, ENERGY_CANDIDATES)
        original_energy = None
        adjusted_energy = None
        if energy_field:
            original_energy = _to_number(row[energy_field], energy_field)
            adjusted_energy = original_energy
            if power_kw > 0 and adjusted_power < power_kw:
                adjusted_energy = original_energy * (adjusted_power / power_kw)
                row[energy_field] = adjusted_energy
                constraint_sources.append("energy_reduced")
            else:
                row[energy_field] = original_energy

        if constraint_sources:
            load_constraint_log.append(
                {
                    "index": idx,
                    "original_power_kw": power_kw,
                    "adjusted_power_kw": adjusted_power,
                    "available_charge_kw": available_charge,
                    "is_dr_period": is_dr_period,
                    "available_dr_capacity_kw": available_dr_capacity,
                    "original_dr_capacity_kw": original_dr_capacity,
                    "adjusted_dr_capacity_kw": adjusted_dr_capacity,
                    "original_energy_kwh": original_energy,
                    "adjusted_energy_kwh": adjusted_energy,
                    "constraint_sources": sorted(set(constraint_sources)),
                }
            )

    return adjusted_input, load_constraint_log
