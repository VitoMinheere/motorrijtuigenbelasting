import unittest

from vehicles.motorcycle import Motorcycle
from vehicles import EnergySource


class TestMotorcycleTaxCalculations2024(unittest.TestCase):
    YEAR = 2024

    def test_calc_opcenten(self):
        # Test cases for calc_opcenten
        province = "noord-holland"
        motor = Motorcycle(weight=1200, energy_source=EnergySource.BENZINE)
        result = 6.04  # Checked with tool

        self.assertEqual(
            round(motor.calculate_opcenten(province, self.YEAR), 2), result
        )

        # Edge case: Non-existent province
        with self.assertRaises(KeyError):
            motor.calculate_opcenten("Non-existent", self.YEAR)

    def test_calculate_tax_noord_holland(self):
        province = "noord-holland"
        motor = Motorcycle(weight=0, energy_source=EnergySource.BENZINE)
        result = 36

        self.assertEqual(motor.calculate_total_tax(province, self.YEAR), result)

        # Edge case: Electric motor before 2025
        electric_motor = Motorcycle(weight=0, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(electric_motor.calculate_total_tax(province, self.YEAR), 0)

    def test_calculate_tax_gelderland(self):
        """Test with another province as they vary between 36 and 37"""
        province = "gelderland"
        motor = Motorcycle(weight=0, energy_source=EnergySource.BENZINE)
        result = 37

        self.assertEqual(motor.calculate_total_tax(province, self.YEAR), result)

        # Edge case: Electric motor before 2025
        electric_motor = Motorcycle(
            weight=720, energy_source=EnergySource.ELEKTRICITEIT
        )
        self.assertEqual(electric_motor.calculate_total_tax(province, self.YEAR), 0)

    def test_calculate_tax_oldtimer(self):
        province = "gelderland"
        motor = Motorcycle(weight=0, energy_source=EnergySource.BENZINE, manufacturing_year=1980)
        result = 0

        self.assertEqual(motor.calculate_total_tax(province, self.YEAR), result)
    
    def test_calculate_tax_kwarttarief(self):
        province = "gelderland"
        motor = Motorcycle(weight=0, energy_source=EnergySource.BENZINE, manufacturing_year=1987)
        result = 9

        self.assertEqual(motor.calculate_total_tax(province, self.YEAR), result)