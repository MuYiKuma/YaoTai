from report import generate_report


def test_generate_report_with_medium_risk() -> None:
    report = generate_report(100, 50, 25, [{"message": "watch spread", "risk_score": 40}])

    assert report == {
        "total_revenue": 175,
        "breakdown": {
            "arbitrage": 100,
            "dr": 50,
            "sr": 25,
        },
        "warnings": [{"message": "watch spread", "risk_score": 40}],
        "risk_level": "medium",
    }


def test_generate_report_with_high_risk_from_multiple_warning_scores() -> None:
    report = generate_report(10, 20, 30, [35, {"risk_score": 40}, "note only"])

    assert report["risk_level"] == "high"
    assert report["total_revenue"] == 60


def test_generate_report_with_low_risk_and_no_warnings() -> None:
    report = generate_report(1, 2, 3, None)

    assert report["warnings"] == []
    assert report["risk_level"] == "low"
