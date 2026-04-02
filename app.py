import streamlit as st
from storage_site_input import StorageSiteInput
from audit_layer import calculate_audited_revenue_breakdown, apply_scenario

st.set_page_config(page_title="儲能案場審計工具", layout="wide")

st.title("儲能案場審計工具")

st.subheader("選擇情境")
scenario = st.selectbox("情境", ["optimistic", "base", "conservative"], label_visibility="collapsed")

st.subheader("基本輸入")

col1, col2, col3 = st.columns(3)

with col1:
    power_kw = st.number_input("PCS 功率 (kW)", value=500.0)
    capacity_kwh = st.number_input("電池容量 (kWh)", value=1044.0)
    dod = st.number_input("DoD", value=0.9)
    efficiency = st.number_input("效率", value=0.86)
    soh = st.number_input("SOH", value=1.0)
    soc_window_ratio = st.number_input("SOC usable window", value=0.85)

with col2:
    summer_spread = st.number_input("夏季價差", value=2.5)
    non_summer_spread = st.number_input("非夏季價差", value=1.8)
    summer_cycles_per_day = st.number_input("夏季 cycles/day", value=1.0)
    non_summer_cycles_per_day = st.number_input("非夏季 cycles/day", value=0.8)

    dr_capacity_kw = st.number_input("DR 容量 (kW)", value=250.0)
    dr_hours = st.number_input("DR 時數", value=4.0)
    dr_rate = st.number_input("DR 費率", value=1.84)
    dr_execution_rate = st.number_input("DR 執行率", value=0.9)

with col3:
    sr_capacity_kw = st.number_input("SR 容量 (kW)", value=350.0)
    sr_price = st.number_input("SR 價格", value=400.0)
    sr_hours_per_day = st.number_input("SR 每日時數", value=2.0)
    sr_execution_rate = st.number_input("SR 執行率", value=0.9)

    aggregator_share_ratio = st.number_input("聚合商分潤", value=0.2)
    aggregator_fixed_fee = st.number_input("聚合商固定費 (/MW/年)", value=400000.0)
    ems_subscription_fee = st.number_input("EMS 年費", value=70992.0)
    insurance_cost = st.number_input("保險", value=120060.0)
    om_cost = st.number_input("O&M", value=204102.0)
    deposit_amount = st.number_input("保證金", value=153300.0)
    deposit_cost_rate = st.number_input("保證金資金成本率", value=0.05)

if st.button("跑審計", type="primary"):
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

    x = apply_scenario(x, scenario)
    result = calculate_audited_revenue_breakdown(x)

    baseline = result["baseline_revenue"]
    audited = result["audited_total_revenue"]
    owner_net = result["owner_net_revenue"]

    st.divider()
    st.subheader("審計結果")

    c1, c2, c3 = st.columns(3)
    c1.metric("業務版收入", f"{baseline:,.0f}")
    c2.metric("審計後收入", f"{audited:,.0f}")
    c3.metric("業主淨收入", f"{owner_net:,.0f}")

    if owner_net > 0 and audited / baseline > 0.7:
        rating = "A"
        st.success("評級：A｜健康案")
    elif owner_net > 0:
        rating = "B"
        st.warning("評級：B｜可做但需留意")
    elif owner_net > -0.1 * baseline:
        rating = "C"
        st.warning("評級：C｜邊緣案")
    else:
        rating = "D"
        st.error("評級：D｜高風險或不成立")

    st.write(f"目前評級：**{rating}**")

    st.subheader("分項結果")
    a1, a2, a3 = st.columns(3)
    a1.markdown(f"**套利毛收入**  \n{result['gross']['arbitrage']['gross_total_revenue']:,.0f}")
    a1.markdown(f"**套利審計後**  \n{result['audited_arbitrage_revenue']:,.0f}")

    a2.markdown(f"**DR 毛收入**  \n{result['gross']['dr']['gross_total_revenue']:,.0f}")
    a2.markdown(f"**DR 審計後**  \n{result['audited_dr_revenue']:,.0f}")

    a3.markdown(f"**SR 毛收入**  \n{result['gross']['sr']['gross_total_revenue']:,.0f}")
    a3.markdown(f"**SR 審計後**  \n{result['audited_sr_revenue']:,.0f}")

    st.subheader("扣費明細")
    st.json(result["deductions"])
