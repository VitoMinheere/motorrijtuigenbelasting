import unittest

from vehicles import Vehicle, EnergySource

class MockVehicle(Vehicle):
    """A mock subclass of Vehicle for testing the calculate_multiplier method."""
    def calculate_base_tax(self, year: int) -> float:
        return 0.0  # Not needed for this test

    def calculate_total_tax(self, year: int, province: str) -> float:
        return 0.0  # Not needed for this test


class TestCalculateMultiplier(unittest.TestCase):

    def test_calculate_multiplier(self):
        # Create test cases with different weights
        vehicle1 = MockVehicle(weight=950, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(
            vehicle1.calculate_multiplier(), 
            0, 
            "Weight below cutoff should return 0"
        )

        vehicle2 = MockVehicle(weight=1000, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(
            vehicle2.calculate_multiplier(), 
            1, 
            "Weight at exact cutoff + 100 should return 1"
        )

        vehicle3 = MockVehicle(weight=1250, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(
            vehicle3.calculate_multiplier(), 
            3, 
            "Weight at cutoff + 350 should return 3"
        )

        vehicle4 = MockVehicle(weight=900, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(
            vehicle4.calculate_multiplier(), 
            0, 
            "Exact cutoff should return 0"
        )

        vehicle5 = MockVehicle(weight=3300, energy_source=EnergySource.ELEKTRICITEIT)
        self.assertEqual(
            vehicle5.calculate_multiplier(cut_off=3300), 
            0, 
            "Custom cutoff matches weight should return 0"
        )


if __name__ == "__main__":
    unittest.main()
