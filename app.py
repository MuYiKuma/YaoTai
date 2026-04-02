import streamlit as st
from storage_site_input import StorageSiteInput
from audit_layer import calculate_audited_revenue_breakdown, apply_scenario

st.title("儲能案場審計工具")

scenario = st.selectbox("選擇情境", ["optimistic", "base", "conservative"])

if st.button("跑審計"):
    x = StorageSiteInput()
    x = apply_scenario(x, scenario)

    result = calculate_audited_revenue_breakdown(x)

    st.subheader("結果")
    st.write("Baseline Revenue:", result["baseline_revenue"])
    st.write("Audited Revenue:", result["audited_total_revenue"])
    st.write("Owner Net Revenue:", result["owner_net_revenue"])
