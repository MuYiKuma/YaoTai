# strategy_rules.py

def apply_strategy_constraints(x):
    """
    根據制度與策略限制，修正不合理的輸入
    """

    notes = []

    # =========================
    # 1️⃣ 逆送電限制（SR）
    # =========================
    if not getattr(x, "grid_approval", True):
        # 假設未核准 → SR 容量最多 70%
        original = x.sr_capacity_kw
        x.sr_capacity_kw = x.sr_capacity_kw * 0.7

        notes.append(f"未申請逆送電核准，SR容量由 {original} → {x.sr_capacity_kw:.0f}")

    # =========================
    # 2️⃣ 服務互斥（DR vs 抑低）
    # =========================
    if getattr(x, "use_dr", False) and getattr(x, "use_peak_shaving", False):
        x.use_peak_shaving = False
        notes.append("需量反應與需量抑低不可同時啟用，已關閉抑低")

    # =========================
    # 3️⃣ SR + 套利衝突
    # =========================
    if getattr(x, "sr_capacity_kw", 0) > 0:
        # SR 有開 → 套利降載
        x.arb_allocation_ratio *= 0.7
        notes.append("SR 與套利存在資源競爭，套利比例已下修")

    # =========================
    # 4️⃣ 過度使用（滿配檢查）
    # =========================
    total_alloc = (
        getattr(x, "arb_allocation_ratio", 0)
        + getattr(x, "dr_allocation_ratio", 0)
        + getattr(x, "sr_allocation_ratio", 0)
    )

    if total_alloc > 1.2:
        scale = 1.2 / total_alloc
        x.arb_allocation_ratio *= scale
        x.dr_allocation_ratio *= scale
        x.sr_allocation_ratio *= scale

        notes.append("總策略使用超過系統容量，已自動縮放")

    return x, notes


def generate_strategy_warnings(x):
    """
    只產生警示，不改數值
    """

    warnings = []

    # =========================
    # 未申請逆送電
    # =========================
    if not getattr(x, "grid_approval", True):
        warnings.append("未申請台電逆送電核准，投標容量可能受限")

    # =========================
    # DR / SR / 套利同時滿載
    # =========================
    if (
        getattr(x, "arb_allocation_ratio", 0) > 0.8
        and getattr(x, "sr_allocation_ratio", 0) > 0.8
    ):
        warnings.append("套利與輔助服務同時高使用，可能不符合實際運行")

    # =========================
    # 電池年限過長
    # =========================
    if getattr(x, "project_years", 15) >= 15:
        warnings.append("電池使用年限假設偏長，可能高估收益")

    return warnings
