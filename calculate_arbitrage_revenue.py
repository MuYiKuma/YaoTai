"""Utility for calculating annual battery arbitrage revenue."""


def calculate_arbitrage_revenue(input_data):
    """
    Calculate annual arbitrage revenue for an energy storage system.

    Expected keys in input_data:
    - capacity_kwh
    - dod
    - soh
    - efficiency
    - summer_spread
    - summer_cycles_per_day
    - non_summer_spread
    - non_summer_cycles_per_day

    Returns:
    - dict with annual_arbitrage_revenue
    """
    summer_days = 107
    non_summer_days = 141

    required_fields = [
        "capacity_kwh",
        "dod",
        "soh",
        "efficiency",
        "summer_spread",
        "summer_cycles_per_day",
        "non_summer_spread",
        "non_summer_cycles_per_day",
    ]

    # 檢查必要欄位是否完整。
    missing_fields = [field for field in required_fields if field not in input_data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    capacity_kwh = float(input_data["capacity_kwh"])
    dod = float(input_data["dod"])
    soh = float(input_data["soh"])
    efficiency = float(input_data["efficiency"])
    summer_spread = float(input_data["summer_spread"])
    summer_cycles_per_day = float(input_data["summer_cycles_per_day"])
    non_summer_spread = float(input_data["non_summer_spread"])
    non_summer_cycles_per_day = float(input_data["non_summer_cycles_per_day"])

    # 基本防呆：容量不可小於 0。
    if capacity_kwh < 0:
        raise ValueError("capacity_kwh cannot be negative")

    # 比例型參數通常應介於 0 到 1 之間，也不可讓可用能量超過原始容量。
    for name, value in {
        "dod": dod,
        "soh": soh,
        "efficiency": efficiency,
    }.items():
        if value < 0 or value > 1:
            raise ValueError(f"{name} must be between 0 and 1")

    # 次數不可為負，價差若業務上允許可自行放寬；此處先限制不可為負。
    for name, value in {
        "summer_spread": summer_spread,
        "summer_cycles_per_day": summer_cycles_per_day,
        "non_summer_spread": non_summer_spread,
        "non_summer_cycles_per_day": non_summer_cycles_per_day,
    }.items():
        if value < 0:
            raise ValueError(f"{name} cannot be negative")

    # 單次可用能量 = capacity_kwh × dod × soh × efficiency
    usable_energy_per_cycle = capacity_kwh * dod * soh * efficiency

    # 防呆：單次可用能量不應超過系統原始容量。
    usable_energy_per_cycle = min(usable_energy_per_cycle, capacity_kwh)

    # 夏月收入 = 單次能量 × summer_spread × summer_cycles_per_day × summer_days
    summer_revenue = (
        usable_energy_per_cycle
        * summer_spread
        * summer_cycles_per_day
        * summer_days
    )

    # 非夏月收入 = 單次能量 × non_summer_spread × non_summer_cycles_per_day × non_summer_days
    non_summer_revenue = (
        usable_energy_per_cycle
        * non_summer_spread
        * non_summer_cycles_per_day
        * non_summer_days
    )

    annual_arbitrage_revenue = summer_revenue + non_summer_revenue

    return {"annual_arbitrage_revenue": annual_arbitrage_revenue}
