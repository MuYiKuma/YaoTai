import streamlit as st
import pandas as pd
from storage_site_input import StorageSiteInput
from audit_layer import calculate_audited_revenue_breakdown, apply_scenario
from strategy_rules import apply_strategy_constraints, generate_strategy_warnings

st.set_page_config(page_title="儲能案場審計工具", layout="wide")
st.title("儲能案場審計工具")

scenario = st.selectbox("選擇情境", ["樂觀情境", "基準情境", "保守情境"])
scenario_map = {
    "樂觀情境": "optimistic",
    "基準情境": "base",
    "保守情境": "conservative"
}
scenario_en = scenario_map[scenario]

uploaded_file = st.file_uploader("上傳全年負載 CSV", type=["csv"])

power_kw = st.number_input("PCS 功率 (kW)", value=500.0)
capacity_kwh = st.number_input("電池容量 (kWh)", value=1044.0)
# ===== 先定義所有輸入 =====
power_kw = st.number_input("PCS 功率 (kW)", value=500.0)
capacity_kwh = st.number_input("電池容量 (kWh)", value=1044.0)
dod = st.number_input("DoD", value=0.9)
efficiency = st.number_input("效率", value=0.86)
soh = st.number_input("SOH", value=1.0)
soc_window_ratio = st.number_input("SOC window", value=0.85)

summer_spread = st.number_input("夏季價差", value=2.5)
non_summer_spread = st.number_input("非夏季價差", value=1.8)

summer_cycles_per_day = st.number_input("夏季 cycles/day", value=1.0)
non_summer_cycles_per_day = st.number_input("非夏季 cycles/day", value=0.8)

dr_capacity_kw = st.number_input("DR 容量", value=250.0)
dr_hours = st.number_input("DR 時數", value=4.0)
dr_rate = st.number_input("DR 費率", value=1.84)
dr_execution_rate = st.number_input("DR 執行率", value=0.9)

sr_capacity_kw = st.number_input("SR 容量", value=350.0)
sr_price = st.number_input("SR 價格", value=400.0)
sr_hours_per_day = st.number_input("SR 每日時數", value=2.0)
sr_execution_rate = st.number_input("SR 執行率", value=0.9)

aggregator_share_ratio = st.number_input("分潤比例", value=0.2)
aggregator_fixed_fee = st.number_input("固定費", value=400000.0)
ems_subscription_fee = st.number_input("EMS 年費", value=70992.0)
insurance_cost = st.number_input("保險費", value=120060.0)
om_cost = st.number_input("維運費", value=204102.0)
deposit_amount = st.number_input("保證金", value=153300.0)
deposit_cost_rate = st.number_input("保證金成本率", value=0.05)
if st.button("跑審計"):

    # 先建立模型物件
    x = StorageSiteInput(
        power_kw=power_kw,
        capacity_kwh=capacity_kwh,
        dod=dod,
        efficiency=efficiency,
        soh=soh,
        soc_window_ratio=soc_window_ratio,
        summer_spread=summer_spread,
        non_summer_spread=non_summer_spread,
        summer_cycles_per_day=summer_cycles_per_day,
        non_summer_cycles_per_day=non_summer_cycles_per_day,
        dr_capacity_kw=dr_capacity_kw,
        dr_hours=dr_hours,
        dr_rate=dr_rate,
        dr_execution_rate=dr_execution_rate,
        sr_capacity_kw=sr_capacity_kw,
        sr_price=sr_price,
        sr_hours_per_day=sr_hours_per_day,
        sr_execution_rate=sr_execution_rate,
        aggregator_share_ratio=aggregator_share_ratio,
        aggregator_fixed_fee=aggregator_fixed_fee,
        ems_subscription_fee=ems_subscription_fee,
        insurance_cost=insurance_cost,
        om_cost=om_cost,
        deposit_amount=deposit_amount,
        deposit_cost_rate=deposit_cost_rate,
    )

    # 如果有 CSV 就轉換
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        # 轉成模型需要欄位
        df["date"] = pd.to_datetime(df["Time"], errors="coerce")
        df["month"] = df["date"].dt.month
        df["load_kwh"] = df["Power(kW)"] * 0.25

        x.annual_load_profile = df  # ✅ 這時候 x 已存在

    # 套用情境、策略、計算審計
    x = apply_scenario(x, scenario_en)
    x, strategy_notes = apply_strategy_constraints(x)
    strategy_warnings = generate_strategy_warnings(x)
    result = calculate_audited_revenue_breakdown(x)
