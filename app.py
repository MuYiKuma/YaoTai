from dataclasses import replace
from storage_site_input import StorageSiteInput
from calculator import calculate_gross_total_revenue_breakdown


SCENARIO_PRESETS = {
    "optimistic": {
        "bid_ratio": 0.85,
        "arb_allocation_ratio": 0.50,
        "dr_allocation_ratio": 0.10,
        "sr_allocation_ratio": 0.50,
        "arb_realization_ratio": 0.90,
        "dr_realization_ratio": 0.70,
        "sr_realization_ratio": 0.80,
    },
    "base": {
        "bid_ratio": 0.70,
        "arb_allocation_ratio": 0.40,
        "dr_allocation_ratio": 0.10,
        "sr_allocation_ratio": 0.50,
        "arb_realization_ratio": 0.85,
        "dr_realization_ratio": 0.60,
        "sr_realization_ratio": 0.75,
    },
    "conservative": {
        "bid_ratio": 0.60,
        "arb_allocation_ratio": 0.20,
        "dr_allocation_ratio": 0.10,
        "sr_allocation_ratio": 0.70,
        "arb_realization_ratio": 0.80,
        "dr_realization_ratio": 0.50,
        "sr_realization_ratio": 0.60,
    },
}


def apply_bid_adjustment(amount: float, ratio: float) -> float:
    return amount * ratio


def apply_allocation_adjustment(amount: float, ratio: float) -> float:
    return amount * ratio


def apply_realization_adjustment(amount: float, ratio: float) -> float:
    return amount * ratio


def apply_scenario(input_data: StorageSiteInput, scenario: str) -> StorageSiteInput:
    if scenario not in SCENARIO_PRESETS:
        raise ValueError(f"未知情境 {scenario}")
    return replace(input_data, **SCENARIO_PRESETS[scenario])


def calculate_deposit_cost(input_data: StorageSiteInput) -> float:
    return input_data.deposit_amount * input_data.deposit_cost_rate


def calculate_effective_aggregator_fixed_fee(input_data: StorageSiteInput) -> float:
    return input_data.aggregator_fixed_fee * (input_data.power_kw / 1000.0)


def calculate_owner_fee_deductions(
    total_realized_revenue: float,
    input_data: StorageSiteInput,
) -> dict:
    aggregator_share_fee = total_realized_revenue * input_data.aggregator_share_ratio
    aggregator_fixed_fee = calculate_effective_aggregator_fixed_fee(input_data)
    deposit_cost = calculate_deposit_cost(input_data)

    total_deductions = (
        aggregator_share_fee
        + aggregator_fixed_fee
        + input_data.ems_subscription_fee
        + input_data.insurance_cost
        + input_data.om_cost
        + deposit_cost
    )

    return {
        "aggregator_share_fee": aggregator_share_fee,
        "aggregator_fixed_fee": aggregator_fixed_fee,
        "ems_subscription_fee": input_data.ems_subscription_fee,
        "insurance_cost": input_data.insurance_cost,
        "om_cost": input_data.om_cost,
        "deposit_cost": deposit_cost,
        "total_deductions": total_deductions,
    }


def calculate_company_revenue(deductions: dict) -> dict:
    """
    公司端目前先定義為：
    - 聚合商分潤
    - 聚合商固定費

    若之後你們公司自己還有內部成本，可再擴充 company_costs / company_net_profit
    """
    company_revenue = (
        deductions["aggregator_share_fee"]
        + deductions["aggregator_fixed_fee"]
    )

    return {
        "company_share_revenue": deductions["aggregator_share_fee"],
        "company_fixed_fee_revenue": deductions["aggregator_fixed_fee"],
        "company_revenue": company_revenue,
        "company_gross_profit": company_revenue,
    }


def calculate_audited_revenue_breakdown(input_data: StorageSiteInput) -> dict:
    gross = calculate_gross_total_revenue_breakdown(input_data)

    gross_arb = gross["arbitrage"]["gross_total_revenue"]
    gross_dr = gross["dr"]["gross_total_revenue"]
    gross_sr = gross["sr"]["gross_total_revenue"]

    baseline_total_revenue = gross["gross_total_revenue"]

    # 套利不吃 bid_ratio
    allocated_arb = apply_allocation_adjustment(
        gross_arb,
        input_data.arb_allocation_ratio,
    )
    realized_arb = apply_realization_adjustment(
        allocated_arb,
        input_data.arb_realization_ratio,
    )

    # DR / SR 吃 bid_ratio
    bid_adjusted_dr = apply_bid_adjustment(gross_dr, input_data.bid_ratio)
    bid_adjusted_sr = apply_bid_adjustment(gross_sr, input_data.bid_ratio)

    allocated_dr = apply_allocation_adjustment(
        bid_adjusted_dr,
        input_data.dr_allocation_ratio,
    )
    allocated_sr = apply_allocation_adjustment(
        bid_adjusted_sr,
        input_data.sr_allocation_ratio,
    )

    realized_dr = apply_realization_adjustment(
        allocated_dr,
        input_data.dr_realization_ratio,
    )
    realized_sr = apply_realization_adjustment(
        allocated_sr,
        input_data.sr_realization_ratio,
    )

    audited_total_revenue = realized_arb + realized_dr + realized_sr

    deductions = calculate_owner_fee_deductions(
        audited_total_revenue,
        input_data,
    )
    owner_net_revenue = audited_total_revenue - deductions["total_deductions"]

    company = calculate_company_revenue(deductions)

    return {
        "baseline_revenue": baseline_total_revenue,
        "gross": gross,
        "audited_arbitrage_revenue": realized_arb,
        "audited_dr_revenue": realized_dr,
        "audited_sr_revenue": realized_sr,
        "audited_total_revenue": audited_total_revenue,
        "deductions": deductions,
        "owner_net_revenue": owner_net_revenue,
        "company": company,
    }
    result = calculate_audited_revenue_breakdown(x)
    baseline = result["baseline_revenue"]
    audited = result["audited_total_revenue"]
    owner_net = result["owner_net_revenue"]
    company_revenue = result["company"]["company_revenue"]
    company_gross_profit = result["company"]["company_gross_profit"]
    
    st.subheader("📊 審計結果")
    st.markdown("### 業主端")
    c1, c2, c3 = st.columns(3)
    c1.metric("業務收入", f"{baseline:,.0f}")
    c2.metric("審計收入", f"{audited:,.0f}")
    c3.metric("業主淨收益", f"{owner_net:,.0f}")
    
    st.markdown("### 公司端")
    d1, d2 = st.columns(2)
    d1.metric("公司收入", f"{company_revenue:,.0f}")
    d2.metric("公司毛利", f"{company_gross_profit:,.0f}")
    
    st.subheader("💸 業主扣費明細")
    st.write(f"聚合商分潤：{result['deductions']['aggregator_share_fee']:,.0f}")
    st.write(f"聚合商固定費：{result['deductions']['aggregator_fixed_fee']:,.0f}")
    st.write(f"EMS 年費：{result['deductions']['ems_subscription_fee']:,.0f}")
    st.write(f"保險費：{result['deductions']['insurance_cost']:,.0f}")
    st.write(f"O&M 維運費：{result['deductions']['om_cost']:,.0f}")
    st.write(f"保證金資金成本：{result['deductions']['deposit_cost']:,.0f}")
    st.write(f"總扣費：{result['deductions']['total_deductions']:,.0f}")
    
    st.subheader("🏢 公司收入拆解")
    st.write(f"分潤收入：{result['company']['company_share_revenue']:,.0f}")
    st.write(f"固定費收入：{result['company']['company_fixed_fee_revenue']:,.0f}")
