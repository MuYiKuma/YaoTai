from __future__ import annotations

from typing import Any

from storage_site_input import StorageSiteInput


def calculate_available_energy(input_data: StorageSiteInput) -> float:
    """Calculate usable discharge energy in kWh."""
    return (
        input_data.capacity_kwh
        * input_data.dod
        * input_data.soh
        * input_data.round_trip_efficiency
    )


def calculate_arbitrage_revenue_breakdown(
    input_data: StorageSiteInput,
) -> dict[str, float]:
    """Calculate annual arbitrage revenue with seasonal breakdown.

    Model:
    - usable energy = capacity * DOD * SOH * round-trip efficiency
    - seasonal gross revenue = usable energy * spread * cycles/day * days/year
    - total arbitrage revenue = summer + non-summer

    Notes:
    - This version does NOT separately model charging loss cost.
    - If later you want Excel-style gross arbitrage / loss cost split,
      this function can be extended without changing its external contract.
    """
    available_energy_kwh = calculate_available_energy(input_data)

    summer_revenue = (
        available_energy_kwh
        * input_data.summer_spread_per_kwh
        * input_data.summer_cycles_per_day
        * input_data.summer_days_per_year
    )
    non_summer_revenue = (
        available_energy_kwh
        * input_data.non_summer_spread_per_kwh
        * input_data.non_summer_cycles_per_day
        * input_data.non_summer_days_per_year
    )
    total_revenue = summer_revenue + non_summer_revenue

    return {
        "available_energy_kwh": available_energy_kwh,
        "summer_revenue": summer_revenue,
        "non_summer_revenue": non_summer_revenue,
        "total_revenue": total_revenue,
    }


def calculate_arbitrage_revenue(input_data: StorageSiteInput) -> float:
    """Calculate total annual arbitrage revenue."""
    breakdown = calculate_arbitrage_revenue_breakdown(input_data)
    return breakdown["total_revenue"]


def calculate_dr_revenue_breakdown(
    input_data: StorageSiteInput,
) -> dict[str, float]:
    """Calculate annual DR revenue using a simplified event-based model.

    Model:
    - annual gross revenue =
        committed_capacity_kw * events_per_year * price_per_kw_event
    - net revenue = gross revenue * (1 - discount_ratio)

    Notes:
    - dr_event_hours is retained in input because it is strategically important,
      but this simplified formula does not yet price directly by event-hour.
    - Once DR commercial logic is finalized, this function should be refined
      instead of changing the rest of the pipeline.
    """
    if not input_data.dr_enabled:
        return {
            "committed_capacity_kw": 0.0,
            "events_per_year": 0.0,
            "gross_revenue": 0.0,
            "discount_amount": 0.0,
            "total_revenue": 0.0,
        }

    gross_revenue = (
        input_data.dr_committed_capacity_kw
        * input_data.dr_events_per_year
        * input_data.dr_price_per_kw_event
    )
    discount_amount = gross_revenue * input_data.dr_discount_ratio
    total_revenue = gross_revenue - discount_amount

    return {
        "committed_capacity_kw": input_data.dr_committed_capacity_kw,
        "events_per_year": input_data.dr_events_per_year,
        "gross_revenue": gross_revenue,
        "discount_amount": discount_amount,
        "total_revenue": total_revenue,
    }


def calculate_dr_revenue(input_data: StorageSiteInput) -> float:
    """Calculate total annual DR revenue."""
    breakdown = calculate_dr_revenue_breakdown(input_data)
    return breakdown["total_revenue"]


def calculate_sr_revenue_breakdown(
    input_data: StorageSiteInput,
) -> dict[str, float]:
    """Calculate annual spinning reserve revenue.

    Model:
    - daily gross revenue =
        bid_capacity_kw
        * standby_hours_per_day
        * (capacity_fee_per_mwh + performance_fee_per_mwh)
        / 1000
        * adjustment_factor
    - annual gross revenue = daily gross revenue * days_per_year
    - service fee = annual gross revenue * service_fee_ratio
    - annual net revenue = annual gross revenue - service fee
    """
    if not input_data.sr_enabled:
        return {
            "bid_capacity_kw": 0.0,
            "daily_gross_revenue": 0.0,
            "annual_gross_revenue": 0.0,
            "service_fee": 0.0,
            "total_revenue": 0.0,
        }

    combined_fee_per_mwh = (
        input_data.sr_capacity_fee_per_mwh
        + input_data.sr_performance_fee_per_mwh
    )

    daily_gross_revenue = (
        input_data.sr_bid_capacity_kw
        * input_data.sr_standby_hours_per_day
        * combined_fee_per_mwh
        / 1000.0
        * input_data.sr_adjustment_factor
    )

    annual_gross_revenue = daily_gross_revenue * input_data.sr_days_per_year
    service_fee = annual_gross_revenue * input_data.sr_service_fee_ratio
    total_revenue = annual_gross_revenue - service_fee

    return {
        "bid_capacity_kw": input_data.sr_bid_capacity_kw,
        "combined_fee_per_mwh": combined_fee_per_mwh,
        "daily_gross_revenue": daily_gross_revenue,
        "annual_gross_revenue": annual_gross_revenue,
        "service_fee": service_fee,
        "total_revenue": total_revenue,
    }


def calculate_sr_revenue(input_data: StorageSiteInput) -> float:
    """Calculate total annual spinning reserve revenue."""
    breakdown = calculate_sr_revenue_breakdown(input_data)
    return breakdown["total_revenue"]


def calculate_total_revenue_breakdown(
    input_data: StorageSiteInput,
) -> dict[str, Any]:
    """Calculate all revenue streams and return a unified breakdown."""
    arbitrage = calculate_arbitrage_revenue_breakdown(input_data)
    dr = calculate_dr_revenue_breakdown(input_data)
    sr = calculate_sr_revenue_breakdown(input_data)

    total_revenue = (
        arbitrage["total_revenue"]
        + dr["total_revenue"]
        + sr["total_revenue"]
    )

    return {
        "arbitrage": arbitrage,
        "dr": dr,
        "sr": sr,
        "total_revenue": total_revenue,
    }


def calculate_total_revenue(input_data: StorageSiteInput) -> float:
    """Calculate total annual revenue across all enabled revenue streams."""
    breakdown = calculate_total_revenue_breakdown(input_data)
    return breakdown["total_revenue"]


def detect_arbitrage_risk(input_data: StorageSiteInput) -> dict[str, Any]:
    """Assess arbitrage assumptions and classify risk level."""
    breakdown = calculate_arbitrage_revenue_breakdown(input_data)
    reasons: list[str] = []
    risk_level = "low"

    if breakdown["non_summer_revenue"] > breakdown["summer_revenue"]:
        reasons.append(
            "非夏月套利收入高於夏月套利收入，表示收益結構較依賴非夏月情境。"
        )
        risk_level = "high"

    if input_data.non_summer_cycles_per_day > 1.5:
        reasons.append(
            "非夏月每日循環次數高於 1.5 次，代表使用頻率假設偏高。"
        )
        risk_level = "high"

    spread = max(
        input_data.summer_spread_per_kwh,
        input_data.non_summer_spread_per_kwh,
    )
    if spread > 3:
        reasons.append(
            "價差假設大於 3 元/度，對價差條件依賴較高。"
        )
        if risk_level != "high":
            risk_level = "medium"

    if (
        input_data.round_trip_efficiency < 0.7
        or input_data.round_trip_efficiency > 1.0
    ):
        reasons.append(
            "round-trip efficiency 未落在合理區間（0.7 至 1.0）。"
        )
        risk_level = "high"

    if not reasons:
        reasons.append("目前套利假設未見明顯異常。")

    return {"risk_level": risk_level, "reasons": reasons}
        )

    return {"risk_level": risk_level, "reasons": reasons}
