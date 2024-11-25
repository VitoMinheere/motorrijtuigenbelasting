import unittest
from taxes import (
    calculate_base_tax, 
    calculate_tax,
    calc_opcenten, 
    calc_multiplier
)
from vehicle_types import EnergySource
from opcenten import OPCENTEN

class TestVehicleTaxCalculations(unittest.TestCase):
    
    def test_calc_multiplier(self):
        # Test cases for calc_multiplier
        self.assertEqual(calc_multiplier(950), 0, "Weight below cutoff should return 0")
        self.assertEqual(calc_multiplier(1000), 1, "Exact cutoff + 100 should return 1")
        self.assertEqual(calc_multiplier(1250), 3, "Cutoff + 350 should return 3")
        self.assertEqual(calc_multiplier(900), 0, "Exact cutoff should return 0")
        self.assertEqual(calc_multiplier(3300, cut_off=3300), 0, "Custom cutoff matches weight")
    
    def test_calc_opcenten(self):
        # Test cases for calc_opcenten
        province = "Noord-Holland"
        weight = 1200
        year = 2023
        OPCENTEN[province] = {2023: 123.45}  # Example rate for the province/year
        expected = 45.81 + (11.68 * (calc_multiplier(weight) - 1))
        expected *= (OPCENTEN[province][year] / 100)
        self.assertAlmostEqual(calc_opcenten(weight, province, year), expected, places=2)

        # Edge case: Non-existent province
        with self.assertRaises(KeyError):
            calc_opcenten(weight, "Non-existent", year)
    
    def test_calculate_total_tax(self):
        # Test data
        weight = 1200
        province = "Noord-Holland"
        year = 2023
        energy_source = EnergySource.BENZINE

        # Mock OPCENTEN for testing
        OPCENTEN[province] = {2023: 123.45}  # Mocked opcenten percentage (1.2345 multiplier)

        # Calculate expected values based on known rules
        rounded_weight = 100 * round(weight / 100)
        
        # Base tax calculation
        base_tax = calculate_base_tax(rounded_weight)

        # Mock expected values based on calculations
        base_tax = 56.13 + (15.09 * calc_multiplier(weight))
        inflation = base_tax * (1 + 0.063)  # 6.3% inflation in 2023
        opcenten = calc_opcenten(weight, province, year)
        # Expected total tax
        expected_tax = int(inflation + opcenten)  # No fuel tax for benzine

        # Assert the calculate_total_tax function matches expected result
        calculated_tax = calculate_tax(energy_source, weight, province, year)
        self.assertEqual(calculated_tax, expected_tax)

if __name__ == "__main__":
    unittest.main()
