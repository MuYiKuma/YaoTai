import unittest

from storage_site_input import StorageSiteInput


class StorageSiteInputTest(unittest.TestCase):
    def test_defaults_are_valid(self) -> None:
        data = StorageSiteInput()
        self.assertEqual(data.contract_capacity_kw, 499.0)
        self.assertEqual(data.power_kw, 500.0)
        self.assertEqual(data.capacity_kwh, 1000.0)

    def test_unit_metadata_is_available(self) -> None:
        self.assertEqual(
            StorageSiteInput.__dataclass_fields__["summer_spread"].metadata["unit"],
            "NTD/kWh",
        )
        self.assertEqual(
            StorageSiteInput.__dataclass_fields__["dr_hours"].metadata["unit"],
            "hour/event",
        )


if __name__ == "__main__":
    unittest.main()
