import unittest

from motorrijtuigenbelasting import EnergySource, Motorcycle

B = EnergySource.BENZINE
E = EnergySource.ELEKTRICITEIT

# (province, energy source, manufacturing year, expected tax per three months)
# Provinces are picked because their totals round to different amounts.
TOTAL_TAX = {
    2024: [
        ("noord-holland", B, None, 36),
        ("noord-holland", E, None, 0),  # Art. 31: nihil
        ("gelderland", B, None, 37),
        ("gelderland", E, None, 0),
        ("gelderland", B, 1980, 0),
        ("gelderland", B, 1987, 8),
    ],
    2025: [
        ("noord-holland", B, None, 36),
        ("noord-holland", E, None, 9),  # Art. 31: een kwart
        ("gelderland", B, None, 38),
        ("gelderland", E, None, 9),
        ("gelderland", B, 1980, 0),
        ("gelderland", B, 1987, 9),
    ],
    2026: [
        ("noord-holland", B, None, 37),
        # Art. 31 was removed and art. 23b only covers personenauto's, so they pay in full
        ("noord-holland", E, None, 37),
        ("gelderland", B, None, 38),
        ("gelderland", E, None, 38),
        ("gelderland", B, 1980, 0),
        ("gelderland", B, 1987, 9),
    ],
}

# Kwarttarief per year for a 1987 motorcycle in gelderland (Wet MRB 1994 art. 84a):
# the quarterly tariff of the previous year plus this year's opcenten, paid once.
KWARTTARIEF_YEARLY = {2024: 34, 2025: 37, 2026: 37}

# Opcenten in noord-holland. Checked with tool.
OPCENTEN = {2024: 6.04, 2025: 6.04, 2026: 6.4}


class TestMotorcycleTax(unittest.TestCase):
    def test_total_tax(self):
        for year, cases in TOTAL_TAX.items():
            for province, energy_source, manufacturing_year, expected in cases:
                with self.subTest(
                    year=year,
                    province=province,
                    energy_source=energy_source,
                    manufacturing_year=manufacturing_year,
                ):
                    motor = Motorcycle(
                        weight=0,
                        energy_source=energy_source,
                        manufacturing_year=manufacturing_year,
                    )
                    self.assertEqual(
                        motor.calculate_total_tax(year, province), expected
                    )

    def test_kwarttarief_yearly(self):
        motor = Motorcycle(weight=0, energy_source=B, manufacturing_year=1987)
        for year, expected in KWARTTARIEF_YEARLY.items():
            with self.subTest(year=year):
                self.assertEqual(
                    motor.calculate_yearly_tax(year, "gelderland"), expected
                )

    def test_opcenten(self):
        motor = Motorcycle(weight=1200, energy_source=B)
        for year, expected in OPCENTEN.items():
            with self.subTest(year=year):
                self.assertEqual(
                    round(motor.calculate_opcenten("noord-holland", year), 2), expected
                )

    def test_unknown_province(self):
        motor = Motorcycle(weight=0, energy_source=B)
        with self.assertRaises(KeyError):
            motor.calculate_opcenten("Non-existent", 2026)

    def test_weight_does_not_matter(self):
        light = Motorcycle(weight=0, energy_source=B)
        heavy = Motorcycle(weight=720, energy_source=B)
        self.assertEqual(
            light.calculate_total_tax(2026, "gelderland"),
            heavy.calculate_total_tax(2026, "gelderland"),
        )
