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

if st.button("跑審計"):
    x = StorageSiteInput(
        power_kw=power_kw,
        capacity_kwh=capacity_kwh,
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("CSV欄位：", list(df.columns))
        st.dataframe(df.head())
        x.annual_load_profile = df

    x = apply_scenario(x, scenario_en)
    x, strategy_notes = apply_strategy_constraints(x)
    strategy_warnings = generate_strategy_warnings(x)

    result = calculate_audited_revenue_breakdown(x)
    st.write(result)
