from __future__ import annotations

from storage_site_input import StorageSiteInput

SUMMER_DAYS = 107
NON_SUMMER_DAYS = 141
ROUND_TRIP_ADJUSTMENT = 0.927


def calculate_available_energy(input_data: StorageSiteInput) -> float:
    """Calculate the usable energy of a storage site in kWh.

    This function now also respects ``soc_window_ratio`` so the value can be
    used by both the original business calculator and the audit layer.
    """
    return (
        input_data.capacity_kwh
        * input_data.dod
        * input_data.soh
        * input_data.efficiency
        * input_data.soc_window_ratio
    )


def calculate_gross_arbitrage_revenue(input_data: StorageSiteInput) -> float:
    """Calculate annual *gross* arbitrage revenue for a storage site."""
    available_energy: float = calculate_available_energy(input_data)
    summer_revenue: float = (
        available_energy
        * input_data.summer_spread
        * input_data.summer_cycles_per_day
        * SUMMER_DAYS
    )
    non_summer_revenue: float = (
        available_energy
        * input_data.non_summer_spread
        * input_data.non_summer_cycles_per_day
        * NON_SUMMER_DAYS
    )

    return (summer_revenue + non_summer_revenue) * ROUND_TRIP_ADJUSTMENT


def calculate_gross_arbitrage_revenue_breakdown(input_data: StorageSiteInput) -> dict:
    """Calculate annual *gross* arbitrage revenue and provide a seasonal breakdown."""
    available_energy: float = calculate_available_energy(input_data)
    summer_revenue: float = (
        available_energy
        * input_data.summer_spread
        * input_data.summer_cycles_per_day
        * SUMMER_DAYS
        * ROUND_TRIP_ADJUSTMENT
    )
    non_summer_revenue: float = (
        available_energy
        * input_data.non_summer_spread
        * input_data.non_summer_cycles_per_day
        * NON_SUMMER_DAYS
        * ROUND_TRIP_ADJUSTMENT
    )
    gross_total_revenue: float = summer_revenue + non_summer_revenue

    return {
        "available_energy": available_energy,
        "summer_revenue": summer_revenue,
        "non_summer_revenue": non_summer_revenue,
        "gross_total_revenue": gross_total_revenue,
        # backward compatibility
        "total_revenue": gross_total_revenue,
    }


def calculate_gross_dr_revenue_breakdown(input_data: StorageSiteInput) -> dict:
    """Calculate simplified *gross* DR revenue.

    This remains a simplified proxy until DR is split by official program type.
    """
    gross_total_revenue = (
        input_data.dr_capacity_kw
        * input_data.dr_hours
        * input_data.dr_rate
        * input_data.dr_execution_rate
        * input_data.dr_discount_ratio
    )
    return {
        "committed_capacity_kw": input_data.dr_capacity_kw,
        "event_hours": input_data.dr_hours,
        "gross_total_revenue": gross_total_revenue,
        # backward compatibility
        "total_revenue": gross_total_revenue,
    }


def calculate_gross_sr_revenue_breakdown(input_data: StorageSiteInput) -> dict:
    """Calculate simplified *gross* SR revenue.

    Note: this is still a business-side proxy, not a full market settlement
    formula.
    """
    gross_total_revenue = (
        input_data.sr_capacity_kw
        * input_data.sr_price
        * input_data.sr_hours_per_day
        * input_data.sr_execution_rate
    )
    return {
        "bid_capacity_kw": input_data.sr_capacity_kw,
        "hours_per_day": input_data.sr_hours_per_day,
        "gross_total_revenue": gross_total_revenue,
        # backward compatibility
        "total_revenue": gross_total_revenue,
    }


def calculate_gross_total_revenue_breakdown(input_data: StorageSiteInput) -> dict:
    """Aggregate all simplified *gross* revenue components."""
    arbitrage = calculate_gross_arbitrage_revenue_breakdown(input_data)
    dr = calculate_gross_dr_revenue_breakdown(input_data)
    sr = calculate_gross_sr_revenue_breakdown(input_data)
    gross_total_revenue = (
        arbitrage["gross_total_revenue"]
        + dr["gross_total_revenue"]
        + sr["gross_total_revenue"]
    )
    return {
        "arbitrage": arbitrage,
        "dr": dr,
        "sr": sr,
        "gross_total_revenue": gross_total_revenue,
        # backward compatibility
        "total_revenue": gross_total_revenue,
    }


def detect_arbitrage_risk(input_data: StorageSiteInput) -> dict:
    """Assess arbitrage assumptions and classify the storage site's risk level."""
    breakdown: dict = calculate_gross_arbitrage_revenue_breakdown(input_data)
    reasons: list[str] = []
    risk_level: str = "low"

    if breakdown["non_summer_revenue"] > breakdown["summer_revenue"]:
        reasons.append(
            "非夏月套利收入高於夏月套利收入，代表收益結構偏向較不穩定的非夏月情境。"
        )
        risk_level = "high"

    if input_data.non_summer_cycles_per_day > 1.5:
        reasons.append(
            "非夏月每日循環次數高於 1.5 次，表示模型假設使用頻率偏高，執行風險較大。"
        )
        risk_level = "high"

    spread: float = max(input_data.summer_spread, input_data.non_summer_spread)
    if spread > 3:
        reasons.append(
            "價差假設大於 3 元/度，對市場價差的依賴較高，需留意中度風險。"
        )
        if risk_level != "high":
            risk_level = "medium"

    if input_data.efficiency < 0.9 or input_data.efficiency > 1:
        reasons.append(
            "效率參數未落在合理區間（0.9 至 1），代表效率假設可能未妥善考慮，屬高風險。"
        )
        risk_level = "high"

    if input_data.soc_window_ratio < 0.8:
        reasons.append(
            "SOC usable window 低於 0.8，代表模型可用電量假設偏保守，需確認是否重複扣減。"
        )
        if risk_level == "low":
            risk_level = "medium"

    if not reasons:
        reasons.append(
            "目前套利假設落在合理區間內，夏月收益占比與循環、效率假設皆未見明顯風險。"
        )

    return {"risk_level": risk_level, "reasons": reasons}


# Backward-compatible wrappers -------------------------------------------------

def calculate_arbitrage_revenue(input_data: StorageSiteInput) -> float:
    return calculate_gross_arbitrage_revenue(input_data)


def calculate_arbitrage_revenue_breakdown(input_data: StorageSiteInput) -> dict:
    return calculate_gross_arbitrage_revenue_breakdown(input_data)


def calculate_total_revenue_breakdown(input_data: StorageSiteInput) -> dict:
    return calculate_gross_total_revenue_breakdown(input_data)
