from storage_site_input import StorageSiteInput

ARBITRAGE_SETTLEMENT_RATIO: float = 0.927
SUMMER_DAYS: int = 107
NON_SUMMER_DAYS: int = 141


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



def calculate_arbitrage_revenue_breakdown(input_data: StorageSiteInput) -> dict:
    """Calculate the annual arbitrage revenue breakdown for a storage site.

    The result includes the available energy, summer revenue, non-summer
    revenue, and total revenue after applying the settlement ratio.

    Args:
        input_data: Storage site input parameters.

    Returns:
        A dictionary with available energy, seasonal arbitrage revenues, and the
        total annual revenue.
    """
    available_energy: float = calculate_available_energy(input_data)
    summer_revenue: float = (
        available_energy
        * input_data.summer_spread
        * input_data.summer_cycles_per_day
        * SUMMER_DAYS
        * ARBITRAGE_SETTLEMENT_RATIO
    )
    non_summer_revenue: float = (
        available_energy
        * input_data.non_summer_spread
        * input_data.non_summer_cycles_per_day
        * NON_SUMMER_DAYS
        * ARBITRAGE_SETTLEMENT_RATIO
    )
    total_revenue: float = summer_revenue + non_summer_revenue

    return {
        "available_energy": available_energy,
        "summer_revenue": summer_revenue,
        "non_summer_revenue": non_summer_revenue,
        "total_revenue": total_revenue,
    }



def calculate_arbitrage_revenue(input_data: StorageSiteInput) -> float:
    """Calculate annual arbitrage revenue for a storage site.

    Args:
        input_data: Storage site input parameters.

    Returns:
        The total annual arbitrage revenue.
    """
    return calculate_arbitrage_revenue_breakdown(input_data)["total_revenue"]
