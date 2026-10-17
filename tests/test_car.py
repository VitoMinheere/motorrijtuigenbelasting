import unittest

from motorrijtuigenbelasting import Car, EnergySource

PROVINCE = "noord-holland"
# Massa rijklaar, which is eigen massa + 100 kg
LIGHT_WEIGHT = 820
HEAVY_WEIGHT = 1300

B = EnergySource.BENZINE
D = EnergySource.DIESEL
E = EnergySource.ELEKTRICITEIT
LPG = EnergySource.LPG
G3 = EnergySource.LPG_G3
OV = EnergySource.OVERIGE

# (weight, energy source, extra Car arguments, expected tax per three months)
# Oldtimers (1980) pay nothing, the kwarttarief (1987) only applies to benzine.
TOTAL_TAX = {
    # 2014-2022: computed from the law text, not checked with the calculator. The
    # fijnstoftoeslag only exists since 2020.
    2014: [
        (LIGHT_WEIGHT, B, {}, 42),
        (HEAVY_WEIGHT, B, {}, 137),
        (LIGHT_WEIGHT, D, {}, 129),
        (LIGHT_WEIGHT, D, {"diesel_particles": True}, 129),
        (LIGHT_WEIGHT, E, {}, 0),
    ],
    2016: [
        (LIGHT_WEIGHT, B, {}, 43),
        (HEAVY_WEIGHT, B, {}, 138),
        (LIGHT_WEIGHT, D, {}, 131),
        (LIGHT_WEIGHT, D, {"diesel_particles": True}, 131),
        (LIGHT_WEIGHT, E, {}, 0),
    ],
    2017: [
        (LIGHT_WEIGHT, B, {}, 42),
        (HEAVY_WEIGHT, B, {}, 136),
        (LIGHT_WEIGHT, D, {}, 131),
        (LIGHT_WEIGHT, D, {"diesel_particles": True}, 131),
        (LIGHT_WEIGHT, E, {}, 0),
    ],
    2018: [
        (LIGHT_WEIGHT, B, {}, 42),
        (HEAVY_WEIGHT, B, {}, 137),
        (LIGHT_WEIGHT, D, {}, 131),
        (LIGHT_WEIGHT, D, {"diesel_particles": True}, 131),
        (LIGHT_WEIGHT, E, {}, 0),
    ],
    2019: [
        (LIGHT_WEIGHT, B, {}, 42),
        (HEAVY_WEIGHT, B, {}, 138),
        (LIGHT_WEIGHT, D, {}, 133),
        (LIGHT_WEIGHT, D, {"diesel_particles": True}, 133),
        (LIGHT_WEIGHT, E, {}, 0),
    ],
    2020: [
        (LIGHT_WEIGHT, B, {}, 43),
        (HEAVY_WEIGHT, B, {}, 139),
        (LIGHT_WEIGHT, D, {}, 135),
        (LIGHT_WEIGHT, D, {"diesel_particles": True}, 158),
        (LIGHT_WEIGHT, E, {}, 0),
    ],
    2021: [
        (LIGHT_WEIGHT, B, {}, 43),
        (HEAVY_WEIGHT, B, {}, 141),
        (LIGHT_WEIGHT, D, {}, 137),
        (LIGHT_WEIGHT, D, {"diesel_particles": True}, 160),
        (LIGHT_WEIGHT, E, {}, 0),
    ],
    2022: [
        (LIGHT_WEIGHT, B, {}, 44),
        (HEAVY_WEIGHT, B, {}, 142),
        (LIGHT_WEIGHT, D, {}, 138),
        (LIGHT_WEIGHT, D, {"diesel_particles": True}, 162),
        (LIGHT_WEIGHT, E, {}, 0),
    ],
    2023: [
        (LIGHT_WEIGHT, B, {}, 46),
        (LIGHT_WEIGHT, E, {}, 0),
        (HEAVY_WEIGHT, B, {}, 148),
        (HEAVY_WEIGHT, E, {}, 0),
    ],
    2024: [
        (LIGHT_WEIGHT, B, {}, 51),
        (LIGHT_WEIGHT, E, {}, 0),
        (HEAVY_WEIGHT, B, {}, 164),
        (3600, B, {}, 739),
        (HEAVY_WEIGHT, G3, {}, 238),
        (LIGHT_WEIGHT, LPG, {}, 183),
        (LIGHT_WEIGHT, OV, {}, 183),
        (LIGHT_WEIGHT, D, {}, 161),
        (LIGHT_WEIGHT, D, {"diesel_particles": True}, 189),
        (HEAVY_WEIGHT, D, {}, 359),
        (HEAVY_WEIGHT, D, {"diesel_particles": True}, 417),
        (LIGHT_WEIGHT, B, {"manufacturing_year": 1980}, 0),
        (LIGHT_WEIGHT, D, {"manufacturing_year": 1980}, 0),
        (LIGHT_WEIGHT, B, {"manufacturing_year": 1987}, 12),
        (LIGHT_WEIGHT, D, {"manufacturing_year": 1987}, 161),
        (LIGHT_WEIGHT, B, {"co2_emissions": True}, 25),
        (HEAVY_WEIGHT, B, {"co2_emissions": True}, 82),
    ],
    2025: [
        (LIGHT_WEIGHT, B, {}, 51),
        (LIGHT_WEIGHT, E, {}, 12),
        (HEAVY_WEIGHT, B, {}, 166),
        (3600, B, {}, 745),
        (HEAVY_WEIGHT, G3, {}, 240),
        (LIGHT_WEIGHT, LPG, {}, 185),
        (LIGHT_WEIGHT, OV, {}, 185),
        (LIGHT_WEIGHT, D, {}, 163),
        (LIGHT_WEIGHT, D, {"diesel_particles": True}, 191),
        (HEAVY_WEIGHT, D, {}, 363),
        (HEAVY_WEIGHT, D, {"diesel_particles": True}, 422),
        (LIGHT_WEIGHT, B, {"manufacturing_year": 1980}, 0),
        (LIGHT_WEIGHT, D, {"manufacturing_year": 1980}, 0),
        (LIGHT_WEIGHT, B, {"manufacturing_year": 1987}, 12),
        (LIGHT_WEIGHT, D, {"manufacturing_year": 1987}, 163),
        (LIGHT_WEIGHT, B, {"co2_emissions": True}, 38),
        (HEAVY_WEIGHT, B, {"co2_emissions": True}, 124),
    ],
    2026: [
        (LIGHT_WEIGHT, B, {}, 53),
        (LIGHT_WEIGHT, E, {}, 37),
        (HEAVY_WEIGHT, B, {}, 172),
        (3600, B, {}, 775),
        (LIGHT_WEIGHT, G3, {}, 53),
        (HEAVY_WEIGHT, G3, {}, 249),
        (LIGHT_WEIGHT, LPG, {}, 191),
        (720, LPG, {}, 161),  # Checked with the Belastingdienst calculator
        (LIGHT_WEIGHT, OV, {}, 191),
        (LIGHT_WEIGHT, D, {}, 168),
        (LIGHT_WEIGHT, D, {"diesel_particles": True}, 197),
        (HEAVY_WEIGHT, D, {}, 375),
        (HEAVY_WEIGHT, D, {"diesel_particles": True}, 436),
        (LIGHT_WEIGHT, B, {"manufacturing_year": 1980}, 0),
        (LIGHT_WEIGHT, D, {"manufacturing_year": 1980}, 0),
        (LIGHT_WEIGHT, B, {"manufacturing_year": 1987}, 13),
        (LIGHT_WEIGHT, D, {"manufacturing_year": 1987}, 168),
        # The low emission discount ended in 2026
        (LIGHT_WEIGHT, B, {"co2_emissions": True}, 53),
        (HEAVY_WEIGHT, B, {"co2_emissions": True}, 172),
    ],
}

# Opcenten for a HEAVY_WEIGHT car in PROVINCE, rounded down. Checked with tool.
OPCENTEN = {2023: 46, 2024: 53, 2025: 53, 2026: 56}


class TestCarTotalTax(unittest.TestCase):
    def test_total_tax(self):
        for year, cases in TOTAL_TAX.items():
            for weight, energy_source, kwargs, expected in cases:
                with self.subTest(
                    year=year, weight=weight, energy_source=energy_source, **kwargs
                ):
                    car = Car(weight=weight, energy_source=energy_source, **kwargs)
                    self.assertEqual(car.calculate_total_tax(year, PROVINCE), expected)

    def test_opcenten(self):
        car = Car(weight=HEAVY_WEIGHT, energy_source=B)
        for year, expected in OPCENTEN.items():
            with self.subTest(year=year):
                self.assertEqual(int(car.calculate_opcenten(PROVINCE, year)), expected)

    def test_unknown_province(self):
        car = Car(weight=HEAVY_WEIGHT, energy_source=B)
        with self.assertRaises(KeyError):
            car.calculate_opcenten("Non-existent", 2026)

    def test_province_name_is_normalised(self):
        car = Car(weight=HEAVY_WEIGHT, energy_source=B)
        self.assertEqual(
            car.calculate_total_tax(2026, "Noord Holland"),
            car.calculate_total_tax(2026, "noord-holland"),
        )

    def test_unsupported_year(self):
        car = Car(weight=HEAVY_WEIGHT, energy_source=B)
        with self.assertRaisesRegex(KeyError, "supported years"):
            car.calculate_total_tax(2010, PROVINCE)

    def test_no_fijnstoftoeslag_before_2020(self):
        """Wet MRB 1994 art. 23 lid 4 was added on 1 January 2020"""
        clean = Car(weight=LIGHT_WEIGHT, energy_source=D)
        dirty = Car(weight=LIGHT_WEIGHT, energy_source=D, diesel_particles=True)
        self.assertEqual(
            dirty.calculate_total_tax(2015, PROVINCE),
            clean.calculate_total_tax(2015, PROVINCE),
        )

    def test_hydrogen_is_taxed_like_electric(self):
        """Art. 23 lid 2: no brandstoftoeslag, art. 23b (before 2025 art. 31): zero emission"""
        for year in TOTAL_TAX:
            for weight in (LIGHT_WEIGHT, HEAVY_WEIGHT):
                with self.subTest(year=year, weight=weight):
                    hydrogen = Car(weight=weight, energy_source=EnergySource.WATERSTOF)
                    electric = Car(weight=weight, energy_source=E)
                    self.assertEqual(
                        hydrogen.calculate_total_tax(year, PROVINCE),
                        electric.calculate_total_tax(year, PROVINCE),
                    )

    def test_lpg_is_not_an_alias_of_overige(self):
        self.assertIsNot(EnergySource.LPG, EnergySource.OVERIGE)


class TestCarYearlyTax(unittest.TestCase):
    def test_regular_car_pays_four_quarters(self):
        car = Car(weight=LIGHT_WEIGHT, energy_source=B)
        self.assertEqual(car.calculate_yearly_tax(2026, PROVINCE), 4 * 53)

    def test_kwarttarief_uses_previous_year_tariff(self):
        """Wet MRB 1994 art. 84a: one quarter of last year's tariff, paid per year"""
        car = Car(weight=LIGHT_WEIGHT, energy_source=B, manufacturing_year=1987)
        for year, expected in {
            2015: 42,
            2023: 44,
            2024: 48,
            2025: 51,
            2026: 52,
        }.items():
            with self.subTest(year=year):
                self.assertEqual(car.calculate_yearly_tax(year, PROVINCE), expected)

    def test_kwarttarief_maximum(self):
        car = Car(weight=3600, energy_source=B, manufacturing_year=1987)
        self.assertEqual(car.calculate_yearly_tax(2026, PROVINCE), 158)
        self.assertEqual(car.calculate_total_tax(2026, PROVINCE), 158 // 4)
