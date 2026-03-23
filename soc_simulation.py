from __future__ import annotations

from typing import Dict, List, Sequence


EVENT_TYPES = ("arbitrage", "dr", "sr")


def simulate_soc(input_data: Dict) -> Dict[str, List[float] | int]:
    """Simulate a battery's state of charge (SOC) over multiple days.

    Expected input_data format::

        {
            "capacity_kwh": 100,
            "days": [
                {
                    "off_peak_charge_kwh": 40,
                    "events": [
                        {"type": "arbitrage", "discharge_kwh": 20},
                        {"type": "dr", "discharge_kwh": 30},
                    ],
                },
                ...
            ],
        }

    Rules:
    - Initial SOC starts at capacity_kwh.
    - Each day charges first, then discharges in event order.
    - SOC is always clamped between 0 and capacity_kwh.
    - If SOC is insufficient for an event, that event is skipped and does not count
      toward valid_cycles.

    Returns:
        {
            "soc_history": [soc_after_day_1, soc_after_day_2, ...],
            "valid_cycles": <number_of_successful_discharge_events>,
        }
    """

    capacity_kwh = float(input_data.get("capacity_kwh", 0))
    if capacity_kwh < 0:
        raise ValueError("capacity_kwh must be non-negative")

    days: Sequence[Dict] = input_data.get("days", [])
    soc = capacity_kwh
    soc_history: List[float] = []
    valid_cycles = 0

    for day in days:
        charge_kwh = max(float(day.get("off_peak_charge_kwh", 0)), 0.0)
        soc = min(capacity_kwh, soc + charge_kwh)

        for event in day.get("events", []):
            event_type = str(event.get("type", "")).lower()
            if event_type and event_type not in EVENT_TYPES:
                raise ValueError(
                    f"Unsupported event type: {event_type}. "
                    f"Expected one of {EVENT_TYPES}."
                )

            discharge_kwh = max(float(event.get("discharge_kwh", 0)), 0.0)
            if discharge_kwh <= soc:
                soc -= discharge_kwh
                valid_cycles += 1

        soc = min(capacity_kwh, max(0.0, soc))
        soc_history.append(soc)

    return {
        "soc_history": soc_history,
        "valid_cycles": valid_cycles,
    }
