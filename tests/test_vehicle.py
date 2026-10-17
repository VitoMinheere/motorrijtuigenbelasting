import unittest

from motorrijtuigenbelasting import Car, EnergySource
from motorrijtuigenbelasting.tax_data import rate_for_weight, round_weight

TABLE = {
    "500": 10.0,
    "600": 20.0,
    "900": 50.0,
    "per_100kg_above_900": 5.0,
    "3300": 400.0,
    "per_100kg_above_3300": 2.0,
}


class TestCalculateMultiplier(unittest.TestCase):
    def test_calculate_multiplier(self):
        # Weights are massa rijklaar, the multiplier counts steps of eigen massa (100 kg less)
        cases = [
            (1050, {}, 0, "Weight below cutoff should return 0"),
            (1100, {}, 1, "Weight at exact cutoff + 100 should return 1"),
            (1350, {}, 3, "Weight at cutoff + 350 should return 3"),
            (1000, {}, 0, "Exact cutoff should return 0"),
            (
                3400,
                {"cut_off": 3300},
                0,
                "Custom cutoff matches weight should return 0",
            ),
        ]
        for weight, kwargs, expected, message in cases:
            with self.subTest(weight=weight, **kwargs):
                car = Car(weight=weight, energy_source=EnergySource.ELEKTRICITEIT)
                self.assertEqual(car.calculate_multiplier(**kwargs), expected, message)


class TestWeight(unittest.TestCase):
    def test_round_weight(self):
        """Wet MRB 1994 art. 22 lid 1b: exactly 50 kg rounds down"""
        cases = {1049: 1000, 1050: 1000, 1051: 1100, 1100: 1100, 1149: 1100}
        for weight, expected in cases.items():
            with self.subTest(weight=weight):
                self.assertEqual(round_weight(weight), expected)

    def test_car_weight_is_massa_rijklaar(self):
        car = Car(weight=1150, energy_source=EnergySource.BENZINE)
        self.assertEqual(car.rounded_weight, 1000)

    def test_rate_for_weight(self):
        cases = {
            300: 10.0,  # Below the lowest bracket
            500: 10.0,
            600: 20.0,
            900: 50.0,
            1000: 55.0,
            3200: 165.0,
            3300: 400.0,  # Second tier starts from its own amount
            3500: 404.0,
        }
        for weight, expected in cases.items():
            with self.subTest(weight=weight):
                self.assertEqual(rate_for_weight(TABLE, weight), expected)
