from risk_score import calculate_risk_score


def test_calculate_risk_score_low():
    result = calculate_risk_score({})

    assert result == {"score": 0, "level": "low", "reasons": []}


def test_calculate_risk_score_medium():
    result = calculate_risk_score(
        {
            "dod": 0.96,
            "efficiency": 0.91,
            "dr_capacity": 100,
            "power_kw": 100,
        }
    )

    assert result["score"] == 26
    assert result["level"] == "medium"
    assert result["reasons"] == [
        "dod > 0.95",
        "efficiency > 0.9",
        "dr_capacity == power_kw",
    ]


def test_calculate_risk_score_high():
    result = calculate_risk_score(
        {
            "dod": 0.96,
            "efficiency": 0.91,
            "dr_capacity": 100,
            "power_kw": 100,
            "sr_execution_rate": 0.95,
            "cycles_per_day": 1.6,
            "electricity_growth": 0.06,
            "no_load_constraint": True,
            "energy_double_count": True,
        }
    )

    assert result["score"] == 89
    assert result["level"] == "high"
    assert len(result["reasons"]) == 8
