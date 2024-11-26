import unittest
from taxes import calculate_tax, calc_opcenten, calc_multiplier
from vehicle_types import EnergySource
from constants import OPCENTEN


class TestCalcMultiplier(unittest.TestCase):
    def test_calc_multiplier(self):
        # Test cases for calc_multiplier
        self.assertEqual(calc_multiplier(950), 0, "Weight below cutoff should return 0")
        self.assertEqual(calc_multiplier(1000), 1, "Exact cutoff + 100 should return 1")
        self.assertEqual(calc_multiplier(1250), 3, "Cutoff + 350 should return 3")
        self.assertEqual(calc_multiplier(900), 0, "Exact cutoff should return 0")
        self.assertEqual(
            calc_multiplier(3300, cut_off=3300), 0, "Custom cutoff matches weight"
        )


"""Tests validated for 2024 with the Motorrijtuigenbelasting tool from the Belastingdienst

Returns:
    _type_: _description_
"""


class TestVehicleTaxCalculations2023(unittest.TestCase):
    YEAR = 2023

    def test_calc_opcenten(self):
        # Test cases for calc_opcenten
        province = "noord-holland"
        weight = 1200
        result = 46  # Checked with tool

        self.assertEqual(calc_opcenten(weight, province, self.YEAR), result)

        # Edge case: Non-existent province
        with self.assertRaises(KeyError):
            calc_opcenten(weight, "Non-existent", self.YEAR)

    def test_calculate_tax(self):
        # Test cases for calculate_tax
        weight = 1200
        province = "noord-holland"
        self.YEAR = 2023
        energy_source = EnergySource.BENZINE
        result = 153

        self.assertEqual(
            calculate_tax(energy_source, weight, province, self.YEAR), result
        )

        # Edge case: Electric car before 2025
        energy_source = EnergySource.ELEKTRICITEIT
        self.assertEqual(calculate_tax(energy_source, weight, province, self.YEAR), 0)


class TestVehicleTaxCalculations2024(unittest.TestCase):
    YEAR = 2024

    def test_calc_opcenten(self):
        # Test cases for calc_opcenten
        province = "noord-holland"
        weight = 1200
        result = 53  # Checked with tool

        self.assertEqual(calc_opcenten(weight, province, self.YEAR), result)

        # Edge case: Non-existent province
        with self.assertRaises(KeyError):
            calc_opcenten(weight, "Non-existent", self.YEAR)

    def test_calculate_tax(self):
        # Test cases for calculate_tax
        weight = 1200
        province = "noord-holland"
        energy_source = EnergySource.BENZINE
        result = 164

        self.assertEqual(
            calculate_tax(energy_source, weight, province, self.YEAR), result
        )

        # Edge case: Electric car before 2025
        energy_source = EnergySource.ELEKTRICITEIT
        self.assertEqual(calculate_tax(energy_source, weight, province, self.YEAR), 0)


if __name__ == "__main__":
    unittest.main()
