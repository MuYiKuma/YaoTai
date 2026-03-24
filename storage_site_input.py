from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StorageSiteInput:
    # Site / System Basics
    contract_capacity_kw: float = field(default=0.0, metadata={"unit": "kW", "description": "契約容量"})
    power_kw: float = field(default=0.0, metadata={"unit": "kW", "description": "儲能PCS額定功率"})
    capacity_kwh: float = field(default=0.0, metadata={"unit": "kWh", "description": "儲能電池額定容量"})

    # Battery / Technical Parameters
    dod: float = field(default=0.95, metadata={"unit": "ratio", "description": "放電深度（0~1）"})
    soh: float = field(default=1.0, metadata={"unit": "ratio", "description": "當前年份SOH（0~1）"})
    round_trip_efficiency: float = field(
        default=0.875,
        metadata={"unit": "ratio", "description": "充放電整體轉換效率（0~1）"},
    )
    annual_degradation_rate: float = field(
        default=0.0,
        metadata={"unit": "ratio", "description": "年衰退率（0~1）"},
    )
    min_demand_kw: float = field(
        default=0.0,
        metadata={"unit": "kW", "description": "最低需量限制"},
    )

    # Arbitrage Inputs
    summer_spread_per_kwh: float = field(
        default=0.0,
        metadata={"unit": "currency/kWh", "description": "夏月平均套利價差"},
    )
    non_summer_spread_per_kwh: float = field(
        default=0.0,
        metadata={"unit": "currency/kWh", "description": "非夏月平均套利價差"},
    )
    summer_cycles_per_day: float = field(
        default=0.0,
        metadata={"unit": "cycles/day", "description": "夏月平均每日循環次數"},
    )
    non_summer_cycles_per_day: float = field(
        default=0.0,
        metadata={"unit": "cycles/day", "description": "非夏月平均每日循環次數"},
    )
    summer_days_per_year: int = field(
        default=153,
        metadata={"unit": "days/year", "description": "夏月年天數"},
    )
    non_summer_days_per_year: int = field(
        default=212,
        metadata={"unit": "days/year", "description": "非夏月年天數"},
    )

    # Demand Response (DR) Inputs
    dr_enabled: bool = field(default=False, metadata={"description": "是否啟用需量反應收益"})
    dr_committed_capacity_kw: float = field(
        default=0.0,
        metadata={"unit": "kW", "description": "DR承諾容量"},
    )
    dr_event_hours: float = field(
        default=0.0,
        metadata={"unit": "hours/event", "description": "DR每次事件持續時數"},
    )
    dr_events_per_year: float = field(
        default=0.0,
        metadata={"unit": "events/year", "description": "DR年執行次數"},
    )
    dr_price_per_kw_event: float = field(
        default=0.0,
        metadata={"unit": "currency/kW-event", "description": "DR每kW每次事件收益"},
    )
    dr_discount_ratio: float = field(
        default=0.0,
        metadata={"unit": "ratio", "description": "DR折減比例（0~1）"},
    )

    # Spinning Reserve (SR) Inputs
    sr_enabled: bool = field(default=False, metadata={"description": "是否啟用即時備轉收益"})
    sr_bid_capacity_kw: float = field(
        default=0.0,
        metadata={"unit": "kW", "description": "SR得標容量"},
    )
    sr_capacity_fee_per_mwh: float = field(
        default=0.0,
        metadata={"unit": "currency/MWh", "description": "SR容量費"},
    )
    sr_performance_fee_per_mwh: float = field(
        default=0.0,
        metadata={"unit": "currency/MWh", "description": "SR效能費"},
    )
    sr_standby_hours_per_day: float = field(
        default=0.0,
        metadata={"unit": "hours/day", "description": "SR每日待命時數"},
    )
    sr_days_per_year: float = field(
        default=0.0,
        metadata={"unit": "days/year", "description": "SR年執行天數"},
    )
    sr_adjustment_factor: float = field(
        default=1.0,
        metadata={"unit": "ratio", "description": "SR效益調整因子（0~1）"},
    )
    sr_service_fee_ratio: float = field(
        default=0.0,
        metadata={"unit": "ratio", "description": "聚合商服務費比例（0~1）"},
    )

    # Financial Inputs
    analysis_years: int = field(default=1, metadata={"unit": "years", "description": "財務分析年限"})
    electricity_price_escalation_rate: float = field(
        default=0.0,
        metadata={"unit": "ratio", "description": "電價年漲幅率（0~1）"},
    )
    discount_rate: float = field(default=0.0, metadata={"unit": "ratio", "description": "折現率（0~1）"})

    # Optional bookkeeping
    source_sheet_name: Optional[str] = field(default=None, metadata={"description": "來源sheet名稱"})
    source_case_name: Optional[str] = field(default=None, metadata={"description": "案場名稱或案例識別"})
