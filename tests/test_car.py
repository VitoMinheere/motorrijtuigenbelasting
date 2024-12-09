import unittest

from motorrijtuigenbelasting.vehicles.car import Car
from motorrijtuigenbelasting.vehicles import EnergySource

PROVINCE = "noord-holland"


class TestCarTaxCalculations2023(unittest.TestCase):
    YEAR = 2023

    def test_calc_opcenten(self):
        # Test cases for calc_opcenten
        car = Car(weight=1200, energy_source=EnergySource.BENZINE)
        result = 46  # Checked with tool

        self.assertEqual(int(car.calculate_opcenten(PROVINCE, self.YEAR)), result)

        # Edge case: Non-existent PROVINCE
        with self.assertRaises(KeyError):
            car.calculate_opcenten("Non-existent", self.YEAR)

    def test_calculate_tax_benzine_without_excess_weight(self):
        car = Car(weight=720, energy_source=EnergySource.BENZINE)
        result = 48

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

        # Edge case: Electric car before 2025
        electric_car = Car(weight=720, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(electric_car.calculate_total_tax(self.YEAR, PROVINCE), 0)

    def test_calculate_tax_with_excess_weight(self):
        car = Car(weight=1200, energy_source=EnergySource.BENZINE)
        result = 154

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

        # Edge case: Electric car before 2025
        electric_car = Car(weight=1200, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(electric_car.calculate_total_tax(self.YEAR, PROVINCE), 0)


class TestCarTaxCalculations2024(unittest.TestCase):
    YEAR = 2024

    def test_calc_opcenten(self):
        car = Car(weight=1200, energy_source=EnergySource.BENZINE)
        result = 53  # Checked with tool

        self.assertEqual(int(car.calculate_opcenten(PROVINCE, self.YEAR)), result)

        # Edge case: Non-existent PROVINCE
        with self.assertRaises(KeyError):
            car.calculate_opcenten("Non-existent", self.YEAR)

    def test_calculate_tax_benzine_without_excess_weight(self):
        car = Car(weight=720, energy_source=EnergySource.BENZINE)
        result = 51

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

        # Edge case: Electric car before 2025
        electric_car = Car(weight=720, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(electric_car.calculate_total_tax(self.YEAR, PROVINCE), 0)

    def test_calculate_tax_benzine_with_excess_weight(self):
        car = Car(weight=1200, energy_source=EnergySource.BENZINE)
        result = 164

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_benzine_with_heavy(self):
        car = Car(weight=3500, energy_source=EnergySource.BENZINE)
        result = 739

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_lpg_g3(self):
        car = Car(weight=1200, energy_source=EnergySource.LPG_G3)
        result = 238

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_lpg(self):
        car = Car(weight=720, energy_source=EnergySource.LPG)
        result = 183

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_other_fuel(self):
        car = Car(weight=720, energy_source=EnergySource.OVERIGE)
        result = 183

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_diesel(self):
        car = Car(weight=720, energy_source=EnergySource.DIESEL)
        result = 161

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_diesel_with_emission_tax(self):
        car = Car(weight=720, energy_source=EnergySource.DIESEL, diesel_particles=True)
        result = 189

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_diesel_with_excess_weight(self):
        car = Car(weight=1200, energy_source=EnergySource.DIESEL)
        result = 359

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_diesel_with_excess_weight_and_emission_tax(self):
        car = Car(weight=1200, energy_source=EnergySource.DIESEL, diesel_particles=True)
        result = 417

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_benzine_oldtimer(self):
        car = Car(
            weight=720, energy_source=EnergySource.BENZINE, manufacturing_year=1980
        )
        result = 0

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_diesel_oldtimer(self):
        car = Car(
            weight=720, energy_source=EnergySource.DIESEL, manufacturing_year=1980
        )
        result = 0

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_benzine_kwarttarief(self):
        """Kwarttarief ruling is only for benzine"""
        car = Car(
            weight=720, energy_source=EnergySource.BENZINE, manufacturing_year=1987
        )
        result = 12

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_diesel_kwarttarief(self):
        """Kwarttarief ruling is only for benzine"""
        car = Car(
            weight=720, energy_source=EnergySource.DIESEL, manufacturing_year=1987
        )
        result = 161

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_benzine_hybrid_without_excess_weight(self):
        car = Car(weight=720, energy_source=EnergySource.BENZINE, co2_emissions=True)
        result = 25

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)

    def test_calculate_tax_benzine_hybrid_with_excess_weight(self):
        car = Car(weight=1200, energy_source=EnergySource.BENZINE, co2_emissions=True)
        result = 82

        self.assertEqual(car.calculate_total_tax(self.YEAR, PROVINCE), result)
