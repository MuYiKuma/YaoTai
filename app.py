import streamlit as st
from storage_site_input import StorageSiteInput
from audit_layer import calculate_audited_revenue_breakdown

st.title("儲能案場審計工具")

file = st.file_uploader("上傳 Excel")

scenario = st.selectbox("選擇情境", ["optimistic", "base", "conservative"])

if st.button("跑審計"):
    x = StorageSiteInput()  # 先簡化

    x = apply_scenario(x, scenario)

    result = calculate_audited_revenue_breakdown(x)

    st.subheader("結果")

    st.write("Baseline:", result["baseline_revenue"])
    st.write("Audited:", result["audited_total_revenue"])
    st.write("Owner Net:", result["owner_net_revenue"])

    if result["owner_net_revenue"] > 0:
        st.success("A / B")
    else:
        st.error("C / D")
