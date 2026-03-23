from __future__ import annotations

from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(score: float, lower: int = 0, upper: int = 100) -> int:
    return max(lower, min(upper, int(round(score))))


def validate_model(input_data):
    """Validate a storage model and return readable warnings plus a risk score.

    Expected keys in ``input_data`` include:
    - power_kw
    - duration
    - capacity_kwh
    - dod
    - soh
    - dr_capacity_kw
    - dr_hours
    - non_summer_cycles_per_day
    - efficiency
    - price_growth_rate (optional; supports either 0.06 or 6 for 6%)
    """

    warnings: list[str] = []
    risk_score = 0.0

    power_kw = _to_float(input_data.get("power_kw"))
    duration = _to_float(input_data.get("duration"))
    capacity_kwh = _to_float(input_data.get("capacity_kwh"))
    dod = _to_float(input_data.get("dod"))
    soh = _to_float(input_data.get("soh"), default=1.0)
    dr_capacity_kw = _to_float(input_data.get("dr_capacity_kw"))
    dr_hours = _to_float(input_data.get("dr_hours"))
    non_summer_cycles_per_day = _to_float(input_data.get("non_summer_cycles_per_day"))
    efficiency = _to_float(input_data.get("efficiency"))

    raw_price_growth = input_data.get("price_growth_rate")
    if raw_price_growth is None:
        raw_price_growth = input_data.get("electricity_price_growth")
    price_growth_rate = None if raw_price_growth is None else _to_float(raw_price_growth)
    if price_growth_rate is not None and price_growth_rate > 1:
        price_growth_rate = price_growth_rate / 100.0

    available_energy = capacity_kwh * dod * soh
    scheduled_energy = power_kw * duration

    # 1. Energy conservation
    if scheduled_energy > available_energy:
        warnings.append(
            "能量守恆檢查未通過：排程需用電量 "
            f"{scheduled_energy:.2f} kWh，高於可用能量 {available_energy:.2f} kWh。"
            "請檢查 power_kw、duration、capacity_kwh、DoD 或 SoH 設定。"
        )
        risk_score += 35

    # 2. DR check
    dr_required_energy = dr_capacity_kw * dr_hours
    if dr_required_energy > available_energy:
        warnings.append(
            "DR 檢查未通過：需預留的需量反應能量 "
            f"{dr_required_energy:.2f} kWh，高於目前可用能量 {available_energy:.2f} kWh。"
            "建議調整 DR 容量、持續時間或儲能可用容量。"
        )
        risk_score += 25

    # 3. Arbitrage cycle check
    if non_summer_cycles_per_day > 2:
        warnings.append(
            "套利循環風險偏高：non_summer_cycles_per_day = "
            f"{non_summer_cycles_per_day:.2f}，已超過 2 次/日，"
            "可能加速電池老化並放大收益假設風險。"
        )
        excess_cycles = non_summer_cycles_per_day - 2
        risk_score += min(20, 8 + excess_cycles * 6)

    # 4. DoD check
    if dod > 0.95:
        warnings.append(
            f"DoD 警告：dod = {dod:.2%}，已高於 95%。"
            "過深充放電可能增加衰退風險並縮短電池壽命。"
        )
        risk_score += 10

    # 5. Efficiency check
    if efficiency > 0.9:
        warnings.append(
            f"效率警告：efficiency = {efficiency:.2%}，高於 90%。"
            "若此值缺乏設備實測或保證數據支持，模型收益可能偏樂觀。"
        )
        risk_score += 8

    # 6. Electricity price growth
    if price_growth_rate is not None and price_growth_rate > 0.05:
        warnings.append(
            f"電價成長警告：假設年成長率為 {price_growth_rate:.2%}，高於 5%。"
            "請確認此成長率是否有政策、歷史資料或情境分析支持。"
        )
        risk_score += 7

    if not warnings:
        warnings.append("模型檢查通過：目前未發現明顯風險或不合理假設。")

    return {
        "warnings": warnings,
        "risk_score": _clamp(risk_score),
    }
