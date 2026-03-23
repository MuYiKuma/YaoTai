from calculator import calculate_arbitrage_revenue, calculate_available_energy
from storage_site_input import StorageSiteInput


def test_calculate_available_energy() -> None:
    input_data = StorageSiteInput(
        capacity_kwh=1000,
        dod=0.9,
        soh=1.0,
        efficiency=0.92,
    )

    result = calculate_available_energy(input_data)

    assert result == 828.0


def test_calculate_arbitrage_revenue() -> None:
    input_data = StorageSiteInput(
        capacity_kwh=1000,
        dod=0.9,
        soh=1.0,
        efficiency=0.92,
        summer_spread=2.5,
        non_summer_spread=2.0,
        summer_cycles_per_day=1.5,
        non_summer_cycles_per_day=1.2,
    )

    result = calculate_arbitrage_revenue(input_data)

    assert result == 567722.7954
