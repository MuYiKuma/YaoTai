from dr_revenue import calculate_dr_revenue


def test_calculate_dr_revenue_success():
    result = calculate_dr_revenue(
        {
            "power_kw": 500,
            "dr_capacity_kw": 100,
            "dr_hours": 2,
            "available_energy": 250,
            "dr_rate": 10,
            "dr_execution_rate": 0.8,
            "dr_discount_ratio": 0.9,
        }
    )

    assert result == {"annual_dr_revenue": 184320.0}


def test_calculate_dr_revenue_power_limit_warning():
    result = calculate_dr_revenue(
        {
            "power_kw": 100,
            "dr_capacity_kw": 120,
            "dr_hours": 2,
            "available_energy": 500,
            "dr_rate": 10,
            "dr_execution_rate": 0.8,
            "dr_discount_ratio": 0.9,
        }
    )

    assert result == {"warning": "dr_capacity_kw 不可大於 power_kw"}


def test_calculate_dr_revenue_energy_limit_warning():
    result = calculate_dr_revenue(
        {
            "power_kw": 500,
            "dr_capacity_kw": 120,
            "dr_hours": 3,
            "available_energy": 300,
            "dr_rate": 10,
            "dr_execution_rate": 0.8,
            "dr_discount_ratio": 0.9,
        }
    )

    assert result == {"warning": "dr_capacity_kw × dr_hours 不可大於可用能量"}
