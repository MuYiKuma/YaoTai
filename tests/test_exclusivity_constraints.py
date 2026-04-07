import unittest

from exclusivity_constraints import apply_exclusivity_constraints


class ApplyExclusivityConstraintsTests(unittest.TestCase):
    def test_dr_and_sr_reduce_capacity_without_double_counting(self):
        adjusted, constraint_log = apply_exclusivity_constraints(
            {
                "capacity_kwh": 100,
                "dod": 0.9,
                "soh": 0.95,
                "dr_enabled": True,
                "sr_enabled": True,
                "arbitrage_cycles": 1.2,
                "arbitrage_energy_kwh_per_cycle": 30,
                "dr_energy_kwh": 50,
            }
        )

        self.assertLessEqual(adjusted["total_energy_used_kwh"], adjusted["max_energy_allowed_kwh"])
        self.assertGreater(adjusted["sr_reserved_kwh"], 0)
        self.assertTrue(any(item["rule"] == "resolve_double_count" for item in constraint_log))

    def test_arbitrage_is_scaled_when_capacity_is_exceeded(self):
        adjusted, constraint_log = apply_exclusivity_constraints(
            {
                "capacity_kwh": 50,
                "dod": 1.0,
                "soh": 1.0,
                "dr_enabled": False,
                "sr_enabled": False,
                "arbitrage_cycles": 3,
                "arbitrage_energy_kwh_per_cycle": 20,
                "dr_energy_kwh": 0,
            }
        )

        self.assertAlmostEqual(adjusted["arbitrage_cycles"], 2.5)
        self.assertTrue(any(item["rule"] == "arbitrage_limited_by_capacity" for item in constraint_log))


if __name__ == "__main__":
    unittest.main()
