import unittest

from storage_site_input import StorageSiteInput


class StorageSiteInputTest(unittest.TestCase):
    def test_defaults_are_valid(self) -> None:
        data = StorageSiteInput()
        self.assertEqual(data.tariff_type, "three_period")
        self.assertEqual(data.voltage_type, "high_voltage")

    def test_invalid_ratio_raises(self) -> None:
        with self.assertRaises(ValueError):
            StorageSiteInput(dod=1.2)

    def test_invalid_enum_raises(self) -> None:
        with self.assertRaises(ValueError):
            StorageSiteInput(voltage_type="low_voltage")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
