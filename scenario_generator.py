from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping
import copy


def _to_dict(base_input: Any) -> dict[str, Any]:
    """Normalize dict/dataclass input into a mutable dict copy."""
    if is_dataclass(base_input):
        return asdict(base_input)
    if isinstance(base_input, Mapping):
        return copy.deepcopy(dict(base_input))
    raise TypeError("base_input must be a dict-like object or a dataclass instance")


def generate_scenarios(base_input: Any) -> dict[str, dict[str, Any]]:
    """
    Generate proposal, standard, and conservative storage-system scenarios.

    Expected inputs include at least ``power_kw`` and may optionally include
    ``dod``, ``efficiency``, ``cycles``, and ``sr_execution_rate``.
    """
    base = _to_dict(base_input)

    try:
        power_kw = float(base["power_kw"])
    except KeyError as exc:
        raise KeyError("base_input must include 'power_kw'") from exc

    dod = float(base.get("dod", 0.95))
    efficiency = float(base.get("efficiency", 0.88))

    proposal = copy.deepcopy(base)
    proposal.update(
        {
            "dod": min(dod, 0.98),
            "efficiency": min(efficiency, 0.9),
            "dr_capacity": power_kw,
            "cycles": None,
            "cycles_note": "unlimited",
            "sr_execution_rate": min(max(float(base.get("sr_execution_rate", 0.98)), 0.95), 1.0),
        }
    )

    standard = copy.deepcopy(base)
    standard.update(
        {
            "dod": min(dod, 0.95),
            "efficiency": min(efficiency, 0.88),
            "dr_capacity": power_kw * 0.8,
            "cycles": {"summer": None, "non_summer": 1.5},
            "cycles_note": "non-summer capped at 1.5 cycles/day",
            "sr_execution_rate": 0.9,
        }
    )

    conservative = copy.deepcopy(base)
    conservative.update(
        {
            "dod": min(max(dod, 0.85), 0.9),
            "efficiency": 0.85,
            "dr_capacity": power_kw * 0.6,
            "cycles": {"summer": 1, "non_summer": 1},
            "cycles_note": "summer and non-summer capped at 1 cycle/day",
            "sr_execution_rate": 0.8,
        }
    )

    return {
        "proposal": proposal,
        "standard": standard,
        "conservative": conservative,
    }
