# app.py
import streamlit as st
import pandas as pd
from storage_site_input import StorageSiteInput
from audit_layer import calculate_audited_revenue_breakdown, apply_scenario
from strategy_rules import apply_strategy_constraints, generate_strategy_warnings

# ⚠️ 一定要在所有 Streamlit 元件之前呼叫
st.set_page_config(page_title="儲能案場審計工具", layout="wide")
# 情境選擇
scenario = st.selectbox("選擇情境", ["樂觀情境", "基準情境", "保守情境"])
scenario_map = {
    "樂觀情境": "optimistic",
    "基準情境": "base",
    "保守情境": "conservative"
}
scenario_en = scenario_map[scenario]

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("CSV欄位：", list(df.columns))
        st.dataframe(df.head())

        # 嘗試自動標準化欄位名稱
        rename_map = {}

        for col in df.columns:
            col_lower = str(col).strip().lower()

            if col_lower in ["month", "月份"]:
                rename_map[col] = "month"
            elif col_lower in ["load_kwh", "kwh", "用電量", "用電度數", "電量"]:
                rename_map[col] = "load_kwh"
            elif col_lower in ["date", "日期", "timestamp", "time"]:
                rename_map[col] = "date"

        df = df.rename(columns=rename_map)

        # 如果沒有 month，但有 date，就從 date 推出 month
        if "month" not in df.columns and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df["month"] = df["date"].dt.month

        # 檢查必要欄位
        required_cols = {"month", "load_kwh"}
        missing = required_cols - set(df.columns)
        if missing:
            st.error(f"CSV 缺少必要欄位：{missing}")
            st.stop()

        x.annual_load_profile = df
        st.success("已成功讀取全年負載資料")

    except Exception as e:
        st.error(f"CSV 解析失敗: {e}")
        st.stop()
