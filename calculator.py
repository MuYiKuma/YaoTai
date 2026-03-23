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
