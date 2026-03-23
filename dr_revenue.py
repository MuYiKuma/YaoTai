"""Demand response revenue calculation utilities."""


def calculate_dr_revenue(input_data):
    """Calculate annual demand response revenue.

    Expected keys in ``input_data``:
    - power_kw
    - dr_capacity_kw
    - dr_hours
    - available_energy
    - dr_rate
    - dr_execution_rate
    - dr_discount_ratio

    Returns:
        dict: Contains ``annual_dr_revenue`` when the inputs are valid.
        dict: Contains ``warning`` when any constraint is violated.
    """
    power_kw = input_data.get("power_kw", 0)
    dr_capacity_kw = input_data.get("dr_capacity_kw", 0)
    dr_hours = input_data.get("dr_hours", 0)
    available_energy = input_data.get("available_energy", 0)
    dr_rate = input_data.get("dr_rate", 0)
    dr_execution_rate = input_data.get("dr_execution_rate", 0)
    dr_discount_ratio = input_data.get("dr_discount_ratio", 0)

    if dr_capacity_kw > power_kw:
        return {"warning": "dr_capacity_kw 不可大於 power_kw"}

    daily_reduction = dr_capacity_kw * dr_hours
    if daily_reduction > available_energy:
        return {"warning": "dr_capacity_kw × dr_hours 不可大於可用能量"}

    daily_revenue = (
        daily_reduction
        * dr_rate
        * dr_execution_rate
        * dr_discount_ratio
    )
    annual_dr_revenue = daily_revenue * 128

    return {"annual_dr_revenue": annual_dr_revenue}
