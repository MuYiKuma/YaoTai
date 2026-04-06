# storage_site_input.py

from dataclasses import dataclass, field
import pandas as pd

@dataclass
class StorageSiteInput:
    # 基本規格
    power_kw: float = 500.0
    capacity_kwh: float = 1000.0
    dod: float = 0.9
    efficiency: float = 0.92
    soh: float = 1.0
    soc_window_ratio: float = 1.0

    # 套利參數
    summer_spread: float = 2.5
    non_summer_spread: float = 2.0
    summer_cycles_per_day: float = 1.5
    non_summer_cycles_per_day: float = 1.2

    # DR 參數
    dr_capacity_kw: float = 0.0
    dr_hours: float = 2.0
    dr_rate: float = 0.0
    dr_execution_rate: float = 1.0
    dr_discount_ratio: float = 1.0

    # SR 參數
    sr_capacity_kw: float = 0.0
    sr_price: float = 0.0
    sr_hours_per_day: float = 0.0
    sr_execution_rate: float = 1.0

    # 成本與費用
    aggregator_share_ratio: float = 0.0
    aggregator_fixed_fee: float = 0.0
    ems_subscription_fee: float = 0.0
    insurance_cost: float = 0.0
    om_cost: float = 0.0
    deposit_amount: float = 0.0
    deposit_cost_rate: float = 0.0

    # ✅ 新增全年負載欄位，支援 CSV / Excel
    annual_load_profile: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
