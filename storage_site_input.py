from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

VoltageType = Literal["high_voltage", "extra_high_voltage"]
TariffType = Literal["three_period"]


@dataclass(slots=True)
class StorageSiteInput:
    """儲能案場輸入資料。

    單位說明：
    - kW: 功率
    - kWh: 電量容量
    - hr/day: 每日小時數
    - ratio: 0~1 之間的比例值
    - NTD/kW, NTD/kWh: 金額單價
    """

    # 基本資料
    contract_capacity_kw: float = field(default=499.0, metadata={"unit": "kW"})
    voltage_type: VoltageType = field(default="high_voltage", metadata={"unit": "enum"})
    tariff_type: TariffType = field(default="three_period", metadata={"unit": "enum"})

    # 儲能系統
    power_kw: float = field(default=500.0, metadata={"unit": "kW"})
    capacity_kwh: float = field(default=1000.0, metadata={"unit": "kWh"})
    dod: float = field(default=0.9, metadata={"unit": "ratio"})
    efficiency: float = field(default=0.92, metadata={"unit": "ratio"})
    soh: float = field(default=1.0, metadata={"unit": "ratio"})
    degradation_rate: float = field(default=0.02, metadata={"unit": "ratio/year"})

    # 策略
    summer_cycles_per_day: float = field(default=1.5, metadata={"unit": "cycle/day"})
    non_summer_cycles_per_day: float = field(default=1.2, metadata={"unit": "cycle/day"})
    dr_capacity_kw: float = field(default=0.0, metadata={"unit": "kW"})
    dr_hours: float = field(default=2.0, metadata={"unit": "hour/event"})
    dr_rate: float = field(default=0.0, metadata={"unit": "NTD/kW"})
    dr_execution_rate: float = field(default=1.0, metadata={"unit": "ratio"})
    dr_discount_ratio: float = field(default=1.0, metadata={"unit": "ratio"})
    sr_capacity_kw: float = field(default=0.0, metadata={"unit": "kW"})
    sr_price: float = field(default=0.0, metadata={"unit": "NTD/kW"})
    sr_hours_per_day: float = field(default=0.0, metadata={"unit": "hour/day"})
    sr_execution_rate: float = field(default=1.0, metadata={"unit": "ratio"})

    # 電價
    summer_spread: float = field(default=2.5, metadata={"unit": "NTD/kWh"})
    non_summer_spread: float = field(default=2.0, metadata={"unit": "NTD/kWh"})

    def __post_init__(self) -> None:
        self._validate_enum("voltage_type", self.voltage_type, {"high_voltage", "extra_high_voltage"})
        self._validate_enum("tariff_type", self.tariff_type, {"three_period"})

        positive_fields = {
            "contract_capacity_kw": self.contract_capacity_kw,
            "power_kw": self.power_kw,
            "capacity_kwh": self.capacity_kwh,
            "dr_hours": self.dr_hours,
            "summer_spread": self.summer_spread,
            "non_summer_spread": self.non_summer_spread,
        }
        for name, value in positive_fields.items():
            self._validate_number(name, value, minimum=0.0)

        cycle_fields = {
            "summer_cycles_per_day": self.summer_cycles_per_day,
            "non_summer_cycles_per_day": self.non_summer_cycles_per_day,
            "sr_hours_per_day": self.sr_hours_per_day,
            "dr_capacity_kw": self.dr_capacity_kw,
            "dr_rate": self.dr_rate,
            "sr_capacity_kw": self.sr_capacity_kw,
            "sr_price": self.sr_price,
        }
        for name, value in cycle_fields.items():
            self._validate_number(name, value, minimum=0.0)

        ratio_fields = {
            "dod": self.dod,
            "efficiency": self.efficiency,
            "soh": self.soh,
            "degradation_rate": self.degradation_rate,
            "dr_execution_rate": self.dr_execution_rate,
            "dr_discount_ratio": self.dr_discount_ratio,
            "sr_execution_rate": self.sr_execution_rate,
        }
        for name, value in ratio_fields.items():
            self._validate_number(name, value, minimum=0.0, maximum=1.0)

    @staticmethod
    def _validate_enum(name: str, value: str, allowed: set[str]) -> None:
        if value not in allowed:
            raise ValueError(f"{name} must be one of {sorted(allowed)}, got {value!r}")

    @staticmethod
    def _validate_number(
        name: str,
        value: float,
        *,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"{name} must be an int or float, got {type(value).__name__}")
        if minimum is not None and value < minimum:
            raise ValueError(f"{name} must be >= {minimum}, got {value}")
        if maximum is not None and value > maximum:
            raise ValueError(f"{name} must be <= {maximum}, got {value}")
