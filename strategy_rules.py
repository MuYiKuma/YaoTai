# strategy_rules.py（修正版）
def apply_strategy_constraints(x):
    notes = []

    # =========================
    # 1️⃣ SR vs 套利（用 capacity 表達）
    # =========================
    if x.sr_capacity_kw > 0:
        # 降低套利循環次數，而不是 ratio
        original = x.non_summer_cycles_per_day
        x.non_summer_cycles_per_day *= 0.7

        notes.append(
            f"SR 與套利競爭資源，非夏月循環由 {original} → {x.non_summer_cycles_per_day:.2f}"
        )

    # =========================
    # 2️⃣ SR 不可超過 PCS
    # =========================
    if x.sr_capacity_kw > x.power_kw:
        original = x.sr_capacity_kw
        x.sr_capacity_kw = x.power_kw

        notes.append(
            f"SR 容量超過 PCS，已由 {original} → {x.sr_capacity_kw}"
        )

    # =========================
    # 3️⃣ DR 不可超過 PCS
    # =========================
    if x.dr_capacity_kw > x.power_kw:
        original = x.dr_capacity_kw
        x.dr_capacity_kw = x.power_kw

        notes.append(
            f"DR 容量超過 PCS，已由 {original} → {x.dr_capacity_kw}"
        )

    return x, notes


def generate_strategy_warnings(x):
    warnings = []

    if x.sr_capacity_kw > 0 and x.non_summer_cycles_per_day > 1.5:
        warnings.append("SR + 高頻套利同時存在，可能不符合實務調度")

    if x.efficiency < 0.85:
        warnings.append("效率偏低，可能高估收益")

    if x.dod > 0.95:
        warnings.append("DoD 假設過高，可能影響電池壽命")

    return warnings
