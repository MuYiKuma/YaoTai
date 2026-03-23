from calculator import calculate_available_energy
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
