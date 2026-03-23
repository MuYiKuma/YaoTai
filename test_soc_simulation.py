import unittest

from soc_simulation import simulate_soc


class SimulateSocTests(unittest.TestCase):
    def test_charge_then_discharge_and_clamp(self):
        result = simulate_soc(
            {
                "capacity_kwh": 100,
                "days": [
                    {
                        "off_peak_charge_kwh": 30,
                        "events": [
                            {"type": "arbitrage", "discharge_kwh": 20},
                            {"type": "dr", "discharge_kwh": 40},
                        ],
                    },
                    {
                        "off_peak_charge_kwh": 80,
                        "events": [
                            {"type": "sr", "discharge_kwh": 50},
                        ],
                    },
                ],
            }
        )

        self.assertEqual(result["soc_history"], [40.0, 50.0])
        self.assertEqual(result["valid_cycles"], 3)

    def test_skips_event_when_soc_is_insufficient(self):
        result = simulate_soc(
            {
                "capacity_kwh": 50,
                "days": [
                    {
                        "off_peak_charge_kwh": 0,
                        "events": [
                            {"type": "arbitrage", "discharge_kwh": 30},
                            {"type": "dr", "discharge_kwh": 25},
                        ],
                    }
                ],
            }
        )

        self.assertEqual(result["soc_history"], [20.0])
        self.assertEqual(result["valid_cycles"], 1)

    def test_invalid_event_type_raises(self):
        with self.assertRaises(ValueError):
            simulate_soc(
                {
                    "capacity_kwh": 100,
                    "days": [
                        {
                            "off_peak_charge_kwh": 0,
                            "events": [{"type": "foo", "discharge_kwh": 10}],
                        }
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
