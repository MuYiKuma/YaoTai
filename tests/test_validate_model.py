from validate_model import validate_model


def test_validate_model_no_warnings_for_reasonable_inputs():
    result = validate_model(
        {
            "power_kw": 50,
            "duration": 2,
            "capacity_kwh": 200,
            "dod": 0.8,
            "soh": 0.95,
            "dr_capacity_kw": 20,
            "dr_hours": 2,
            "non_summer_cycles_per_day": 1.5,
            "efficiency": 0.88,
            "price_growth_rate": 0.04,
        }
    )

    assert result["risk_score"] == 0
    assert result["warnings"] == ["模型檢查通過：目前未發現明顯風險或不合理假設。"]


def test_validate_model_flags_multiple_risks():
    result = validate_model(
        {
            "power_kw": 100,
            "duration": 3,
            "capacity_kwh": 250,
            "dod": 0.97,
            "soh": 0.9,
            "dr_capacity_kw": 80,
            "dr_hours": 3,
            "non_summer_cycles_per_day": 2.5,
            "efficiency": 0.92,
            "price_growth_rate": 6,
        }
    )

    assert result["risk_score"] > 0
    assert len(result["warnings"]) == 6
    assert any("能量守恆檢查未通過" in warning for warning in result["warnings"])
    assert any("DR 檢查未通過" in warning for warning in result["warnings"])
    assert any("套利循環風險偏高" in warning for warning in result["warnings"])
    assert any("DoD 警告" in warning for warning in result["warnings"])
    assert any("效率警告" in warning for warning in result["warnings"])
    assert any("電價成長警告" in warning for warning in result["warnings"])
