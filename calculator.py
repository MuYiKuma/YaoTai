# calculator.py
from storage_site_input import StorageSiteInput
import pandas as pd

# 假設值（如果沒有 annual_load_profile 時使用）
SUMMER_DAYS = 107
NON_SUMMER_DAYS = 258
ROUND_TRIP_ADJUSTMENT = 0.92  # 電池充放電效率

def calculate_available_energy(input_data: StorageSiteInput):
    """
    計算可用電量：
    - 若提供 annual_load_profile → 取 min(電池容量, 當日負載)
    - 若無負載資料 → 使用摘要公式
    """
    if input_data.annual_load_profile.empty:
        return input_data.capacity_kwh * input_data.dod * input_data.soh * input_data.efficiency * input_data.soc_window_ratio
    else:
        # annual_load_profile 必須有 'month' 與 'load_kwh' 欄位
        available_energy = input_data.annual_load_profile['load_kwh'].apply(
            lambda load: min(load, input_data.capacity_kwh) * input_data.dod * input_data.soh * input_data.efficiency * input_data.soc_window_ratio
        )
        return available_energy

def calculate_gross_arbitrage_revenue_breakdown(input_data: StorageSiteInput):
    """
    計算套利毛收入（夏季 / 非夏季）
    """
    energy = calculate_available_energy(input_data)

    # 夏季月份
    summer_months = [6,7,8,9]

    if isinstance(energy, pd.Series):
        summer_energy = energy[input_data.annual_load_profile['month'].isin(summer_months)].sum()
        non_summer_energy = energy[~input_data.annual_load_profile['month'].isin(summer_months)].sum()
    else:
        summer_energy = energy * SUMMER_DAYS
        non_summer_energy = energy * NON_SUMMER_DAYS

    summer_revenue = summer_energy * input_data.summer_spread * input_data.summer_cycles_per_day * ROUND_TRIP_ADJUSTMENT
    non_summer_revenue = non_summer_energy * input_data.non_summer_spread * input_data.non_summer_cycles_per_day * ROUND_TRIP_ADJUSTMENT

    gross_total_revenue = summer_revenue + non_summer_revenue

    return {
        "available_energy": energy,
        "summer_revenue": summer_revenue,
        "non_summer_revenue": non_summer_revenue,
        "gross_total_revenue": gross_total_revenue,
        "total_revenue": gross_total_revenue,
    }

def calculate_gross_total_revenue_breakdown(input_data: StorageSiteInput):
    """
    計算毛收入拆解（套利 + DR + SR）
    """
    arbitrage = calculate_gross_arbitrage_revenue_breakdown(input_data)

    # DR
    dr_total_revenue = input_data.dr_capacity_kw * input_data.dr_hours * input_data.dr_rate * input_data.dr_execution_rate
    dr = {
        "committed_capacity_kw": input_data.dr_capacity_kw,
        "event_hours": input_data.dr_hours,
        "gross_total_revenue": dr_total_revenue,
        "total_revenue": dr_total_revenue
    }

    # SR
    sr_total_revenue = input_data.sr_capacity_kw * input_data.sr_hours_per_day * input_data.sr_price * input_data.sr_execution_rate
    sr = {
        "bid_capacity_kw": input_data.sr_capacity_kw,
        "hours_per_day": input_data.sr_hours_per_day,
        "gross_total_revenue": sr_total_revenue,
        "total_revenue": sr_total_revenue
    }

    gross_total_revenue = arbitrage["gross_total_revenue"] + dr_total_revenue + sr_total_revenue

    return {
        "arbitrage": arbitrage,
        "dr": dr,
        "sr": sr,
        "gross_total_revenue": gross_total_revenue,
        "total_revenue": gross_total_revenue
    }
