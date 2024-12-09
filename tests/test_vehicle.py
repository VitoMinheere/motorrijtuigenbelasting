import unittest

from motorrijtuigenbelasting.vehicles import EnergySource
from motorrijtuigenbelasting.vehicles.car import Car


class TestCalculateMultiplier(unittest.TestCase):

    def test_calculate_multiplier(self):
        # Create test cases with different weights
        vehicle1 = Car(weight=950, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(
            vehicle1.calculate_multiplier(), 0, "Weight below cutoff should return 0"
        )

        vehicle2 = Car(weight=1000, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(
            vehicle2.calculate_multiplier(),
            1,
            "Weight at exact cutoff + 100 should return 1",
        )

        vehicle3 = Car(weight=1250, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(
            vehicle3.calculate_multiplier(), 3, "Weight at cutoff + 350 should return 3"
        )

        vehicle4 = Car(weight=900, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(
            vehicle4.calculate_multiplier(), 0, "Exact cutoff should return 0"
        )

        vehicle5 = Car(weight=3300, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(
            vehicle5.calculate_multiplier(cut_off=3300),
            0,
            "Custom cutoff matches weight should return 0",
        )
