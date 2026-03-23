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
