from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class StorageSiteInput:
    """儲能系統模型。

    這個 schema 同時支援：
    1. 業務端的毛收入試算
    2. 審計端的調整參數與業主淨收益評估
    """

    # 基本
    contract_capacity_kw: float = field(default=499.0, metadata={"unit": "kW"})
    power_kw: float = field(default=500.0, metadata={"unit": "kW"})
    capacity_kwh: float = field(default=1000.0, metadata={"unit": "kWh"})

    # 電池
    dod: float = field(default=0.9, metadata={"unit": "ratio"})
    efficiency: float = field(default=0.92, metadata={"unit": "ratio"})
    soh: float = field(default=1.0, metadata={"unit": "ratio"})
    degradation_rate: float = field(default=0.02, metadata={"unit": "ratio/year"})
    soc_window_ratio: float = field(default=1.0, metadata={"unit": "ratio"})

    # 套利
    summer_spread: float = field(default=2.5, metadata={"unit": "NTD/kWh"})
    non_summer_spread: float = field(default=2.0, metadata={"unit": "NTD/kWh"})
    summer_cycles_per_day: float = field(default=1.5, metadata={"unit": "cycle/day"})
    non_summer_cycles_per_day: float = field(default=1.2, metadata={"unit": "cycle/day"})

    # 需量反應（DR）
    dr_capacity_kw: float = field(default=0.0, metadata={"unit": "kW"})
    dr_hours: float = field(default=2.0, metadata={"unit": "hour/event"})
    dr_rate: float = field(default=0.0, metadata={"unit": "NTD/kW"})
    dr_execution_rate: float = field(default=1.0, metadata={"unit": "ratio"})
    dr_discount_ratio: float = field(default=1.0, metadata={"unit": "ratio"})

    # 即時備轉（SR）
    sr_capacity_kw: float = field(default=0.0, metadata={"unit": "kW"})
    sr_price: float = field(default=0.0, metadata={"unit": "NTD/kW"})
    sr_hours_per_day: float = field(default=0.0, metadata={"unit": "hour/day"})
    sr_execution_rate: float = field(default=1.0, metadata={"unit": "ratio"})

    # 審計調整參數
    bid_ratio: float = field(default=1.0, metadata={"unit": "ratio"})
    arb_allocation_ratio: float = field(default=1.0, metadata={"unit": "ratio"})
    dr_allocation_ratio: float = field(default=1.0, metadata={"unit": "ratio"})
    sr_allocation_ratio: float = field(default=1.0, metadata={"unit": "ratio"})
    arb_realization_ratio: float = field(default=1.0, metadata={"unit": "ratio"})
    dr_realization_ratio: float = field(default=1.0, metadata={"unit": "ratio"})
    sr_realization_ratio: float = field(default=1.0, metadata={"unit": "ratio"})

    # 商務成本 / 業主淨收益
    aggregator_share_ratio: float = field(default=0.0, metadata={"unit": "ratio"})
    aggregator_fixed_fee: float = field(default=0.0, metadata={"unit": "NTD/year"})
    ems_subscription_fee: float = field(default=0.0, metadata={"unit": "NTD/year"})
    insurance_cost: float = field(default=0.0, metadata={"unit": "NTD/year"})
    om_cost: float = field(default=0.0, metadata={"unit": "NTD/year"})
    deposit_amount: float = field(default=0.0, metadata={"unit": "NTD"})
    deposit_cost_rate: float = field(default=0.0, metadata={"unit": "ratio/year"})

    # 資本支出 / 增補
    capex: float = field(default=0.0, metadata={"unit": "NTD"})
    augmentation_year: int | None = field(default=None, metadata={"unit": "year"})
    augmentation_capex: float = field(default=0.0, metadata={"unit": "NTD"})
    # 在 dataclass 裡面加
    annual_load_profile: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
