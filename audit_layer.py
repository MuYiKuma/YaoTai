# audit_layer.py
from dataclasses import replace
from storage_site_input import StorageSiteInput

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

def apply_scenario(input_data: StorageSiteInput, scenario: str) -> StorageSiteInput:
    if scenario not in SCENARIO_PRESETS:
        raise ValueError(f"未知情境 {scenario}")
    return replace(input_data, **SCENARIO_PRESETS[scenario])

# 其他 calculate_audited_revenue_breakdown 函式保留你原本版本
# 會使用 calculate_gross_total_revenue_breakdown + 費用扣除 + owner_net
