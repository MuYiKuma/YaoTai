# app.py
from storage_site_input import StorageSiteInput
from audit_layer import calculate_audited_revenue_breakdown, apply_scenario
from strategy_rules import apply_strategy_constraints, generate_strategy_warnings

st.set_page_config(page_title="儲能案場審計工具", layout="wide")
st.title("儲能案場審計工具")

# 情境選擇
scenario = st.selectbox("選擇情境", ["樂觀情境", "基準情境", "保守情境"])
scenario_map = {
    "樂觀情境": "optimistic",
    "基準情境": "base",
    "保守情境": "conservative"
}
scenario_en = scenario_map[scenario]

# CSV 上傳
uploaded_file = st.file_uploader("上傳全年負載 CSV", type=["csv"])

# 手動輸入欄位
# 省略，跟前面示範一樣

if st.button("跑審計", type="primary"):
    x = StorageSiteInput(
        # 全部欄位從輸入取值
    )

    # 套情境
    x = apply_scenario(x, scenario_en)

    # CSV 上傳
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        x.annual_load_profile = df
        st.dataframe(df)

    # 策略規則
    x, strategy_notes = apply_strategy_constraints(x)
    strategy_warnings = generate_strategy_warnings(x)

    # 計算審計
    result = calculate_audited_revenue_breakdown(x)
    baseline = result["baseline_revenue"]
    audited = result["audited_total_revenue"]
    owner_net = result["owner_net_revenue"]

    # 顯示結果
    c1, c2, c3 = st.columns(3)
    c1.metric("業務收入", f"{baseline:,.0f}")
    c2.metric("審計收入", f"{audited:,.0f}")
    c3.metric("淨收益", f"{owner_net:,.0f}")

    for note in strategy_notes:
        st.info(note)
    for w in strategy_warnings:
        st.warning(w)
