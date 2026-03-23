from storage_site_input import StorageSiteInput


def calculate_available_energy(input_data: StorageSiteInput) -> float:
    """Calculate the usable energy of a storage site in kWh.

    The available energy is computed from the installed capacity adjusted by
    depth of discharge (DoD), state of health (SoH), and round-trip efficiency.

    Args:
        input_data: Storage site input parameters.

    Returns:
        The available energy in kWh.
    """
    return (
        input_data.capacity_kwh
        * input_data.dod
        * input_data.soh
        * input_data.efficiency
    )


def calculate_arbitrage_revenue(input_data: StorageSiteInput) -> float:
    """Calculate annual arbitrage revenue for a storage site.

    Revenue is based on available energy, seasonal price spreads, expected daily
    cycles, and a fixed round-trip efficiency adjustment factor.

    Args:
        input_data: Storage site input parameters.

    Returns:
        The total annual arbitrage revenue.
    """
    available_energy: float = calculate_available_energy(input_data)
    summer_revenue: float = (
        available_energy
        * input_data.summer_spread
        * input_data.summer_cycles_per_day
        * 107
    )
    non_summer_revenue: float = (
        available_energy
        * input_data.non_summer_spread
        * input_data.non_summer_cycles_per_day
        * 141
    )

    return (summer_revenue + non_summer_revenue) * 0.927


def calculate_arbitrage_revenue_breakdown(input_data: StorageSiteInput) -> dict:
    """Calculate annual arbitrage revenue and provide a seasonal breakdown.

    The breakdown uses the available energy, seasonal price spreads, expected
    daily cycles, and the same annual day counts as the aggregate arbitrage
    calculation.

    Args:
        input_data: Storage site input parameters.

    Returns:
        A dictionary containing available energy, summer revenue,
        non-summer revenue, and total revenue.
    """
    available_energy: float = calculate_available_energy(input_data)
    summer_revenue: float = (
        available_energy
        * input_data.summer_spread
        * input_data.summer_cycles_per_day
        * 107
        * 0.927
    )
    non_summer_revenue: float = (
        available_energy
        * input_data.non_summer_spread
        * input_data.non_summer_cycles_per_day
        * 141
        * 0.927
    )
    total_revenue: float = summer_revenue + non_summer_revenue

    return {
        "available_energy": available_energy,
        "summer_revenue": summer_revenue,
        "non_summer_revenue": non_summer_revenue,
        "total_revenue": total_revenue,
    }


def detect_arbitrage_risk(input_data: StorageSiteInput) -> dict:
    """Assess arbitrage assumptions and classify the storage site's risk level.

    This helper first computes the seasonal revenue breakdown, then evaluates
    whether the arbitrage case relies on unusually strong non-summer revenue,
    aggressive cycling assumptions, unusually large price spread assumptions, or
    an invalid / unmodeled efficiency range.

    Args:
        input_data: Storage site input parameters.

    Returns:
        A dictionary with the overall risk level and a list of human-readable
        reasons explaining the decision.
    """
    breakdown: dict = calculate_arbitrage_revenue_breakdown(input_data)
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

    if not reasons:
        reasons.append(
            "目前套利假設落在合理區間內，夏月收益占比與循環、效率假設皆未見明顯風險。"
        )

    return {"risk_level": risk_level, "reasons": reasons}
