from load_constraints import apply_load_constraints


def test_apply_load_constraints_limits_power_and_energy():
    adjusted, log_rows = apply_load_constraints(
        [
            {
                "power_kw": 50.0,
                "energy_kwh": 100.0,
                "contract_capacity_kw": 80.0,
                "avg_load_kw": 40.0,
                "is_dr_period": False,
            }
        ]
    )

    assert adjusted[0]["available_charge_kw"] == 40.0
    assert adjusted[0]["power_kw"] == 40.0
    assert adjusted[0]["energy_kwh"] == 80.0
    assert log_rows[0]["constraint_sources"] == ["contract_capacity", "energy_reduced"]


def test_apply_load_constraints_reduces_dr_capacity_when_needed():
    adjusted, log_rows = apply_load_constraints(
        [
            {
                "power_kw": 60.0,
                "energy_kwh": 120.0,
                "contract_capacity_kw": 100.0,
                "avg_load_kw": 20.0,
                "current_load_kw": 70.0,
                "is_dr_period": True,
                "dr_capacity_kw": 50.0,
            }
        ]
    )

    assert adjusted[0]["available_dr_capacity_kw"] == 30.0
    assert adjusted[0]["power_kw"] == 30.0
    assert adjusted[0]["energy_kwh"] == 60.0
    assert adjusted[0]["dr_capacity_kw"] == 30.0
    assert set(log_rows[0]["constraint_sources"]) == {
        "dr_capacity",
        "dr_capacity_reduced",
        "energy_reduced",
    }
