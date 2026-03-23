from report_generator import generate_analysis_report


def test_flags_optimistic_model_and_reassessment():
    report = generate_analysis_report(
        {
            "proposal_revenue": 150,
            "standard_revenue": 100,
            "conservative_revenue": 60,
        }
    )

    assert report["conclusion"] == "模型偏樂觀；需重新評估"
    assert "proposal 與 standard 差距過大" in report["key_issues"]
    assert "情境差距超過 30%" in report["key_issues"]


def test_flags_stable_model_when_standard_close_to_conservative():
    report = generate_analysis_report(
        {
            "proposal_revenue": 108,
            "standard_revenue": 100,
            "conservative_revenue": 95,
            "key_issues": ["樣本量有限"],
        }
    )

    assert report["conclusion"] == "模型穩健"
    assert report["key_issues"] == ["樣本量有限"]


def test_defaults_to_reasonable_range_when_no_rule_matches():
    report = generate_analysis_report(
        {
            "proposal_revenue": 120,
            "standard_revenue": 100,
            "conservative_revenue": 75,
        }
    )

    assert report["conclusion"] == "模型落在合理區間"
    assert report["key_issues"] == []
