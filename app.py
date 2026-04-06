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
    try:
        df = pd.read_csv(uploaded_file)

        st.write("CSV 欄位：", list(df.columns))
        st.dataframe(df.head())

        # ===== 依你現在的 RawData 格式做標準化 =====
        # 原始欄位：
        # Time, Power(kW)

        if "Time" in df.columns and "Power(kW)" in df.columns:
            df["date"] = pd.to_datetime(df["Time"], errors="coerce")
            df["month"] = df["date"].dt.month

            # 15 分鐘功率(kW) → 當筆電量(kWh)
            df["load_kwh"] = df["Power(kW)"] * 0.25

        # 檢查必要欄位
        required_cols = {"month", "load_kwh"}
        missing = required_cols - set(df.columns)
        if missing:
            st.error(f"CSV 缺少必要欄位：{missing}")
            st.stop()

        x.annual_load_profile = df
        st.success("已成功讀取全年負載資料")

        st.subheader("標準化後資料")
        st.dataframe(df[["date", "month", "Power(kW)", "load_kwh"]].head())

    except Exception as e:
        st.error(f"CSV 解析失敗: {e}")
        st.stop()
