"""Sanity checks for data/tax_data.json, to catch typos when adding a year."""

import unittest

from motorrijtuigenbelasting.tax_data import PER_100KG_PREFIX, TAX_DATA

# Tabelcorrectiefactor: the yearly indexation of all amounts in the law, from the
# "Belangrijkste wijzigingen belastingen <year>" overview of the Rijksoverheid.
TABELCORRECTIEFACTOR = {
    2024: 0.099,
    2025: 0.012,
    2026: 0.029,
}

PROVINCES = {
    "drenthe",
    "flevoland",
    "friesland",
    "gelderland",
    "groningen",
    "limburg",
    "noord-brabant",
    "noord-holland",
    "overijssel",
    "utrecht",
    "zeeland",
    "zuid-holland",
}
FUEL_SURCHARGES = {"diesel", "overige", "lpg_g3"}
# Rates are stated in cents, so a ratio between two years can be off by rounding
RATIO_TOLERANCE = 0.002


def weight_tables(year_data: dict) -> dict:
    """All weight tables of a year by name, e.g. "base" or "fuel_surcharge.diesel"."""
    car = year_data["car"]
    tables = {"base": car["base"]}
    for fuel, table in car["fuel_surcharge"].items():
        tables[f"fuel_surcharge.{fuel}"] = table
    return tables


def fixed_amounts(table: dict) -> dict:
    return {
        int(key): value
        for key, value in table.items()
        if not key.startswith(PER_100KG_PREFIX)
    }


class TestTaxDataSchema(unittest.TestCase):
    def test_every_year_has_all_keys(self):
        for year, data in TAX_DATA.items():
            with self.subTest(year=year):
                self.assertEqual(set(data["opcenten"]), PROVINCES)
                self.assertEqual(set(data["car"]["fuel_surcharge"]), FUEL_SURCHARGES)
                for key in (
                    "zero_emission_factor",
                    "low_emission_factor",
                    "fijnstoftoeslag",
                ):
                    self.assertIn(key, data["car"])
                for key in ("value", "zero_emission_factor"):
                    self.assertIn(key, data["motorcycle"])
                self.assertIn("value", data["kwarttarief"])

    def test_weight_tables_have_the_same_brackets_every_year(self):
        first = weight_tables(next(iter(TAX_DATA.values())))
        for year, data in TAX_DATA.items():
            for name, table in weight_tables(data).items():
                with self.subTest(year=year, table=name):
                    self.assertEqual(set(table), set(first[name]))

    def test_weight_tables_do_not_decrease(self):
        for year, data in TAX_DATA.items():
            for name, table in weight_tables(data).items():
                with self.subTest(year=year, table=name):
                    amounts = [v for _, v in sorted(fixed_amounts(table).items())]
                    self.assertEqual(amounts, sorted(amounts))

    def test_factors_are_fractions(self):
        for year, data in TAX_DATA.items():
            for category, key in (
                ("car", "zero_emission_factor"),
                ("car", "low_emission_factor"),
                ("car", "fijnstoftoeslag"),
                ("motorcycle", "zero_emission_factor"),
            ):
                with self.subTest(year=year, key=f"{category}.{key}"):
                    self.assertGreaterEqual(data[category][key], 0)
                    self.assertLessEqual(data[category][key], 1)


class TestTabelcorrectiefactor(unittest.TestCase):
    """Every amount should grow by the tabelcorrectiefactor compared to last year."""

    def assert_indexed(self, previous: float, current: float, factor: float):
        if previous == 0:
            self.assertEqual(current, 0)
        else:
            self.assertAlmostEqual(
                current / previous, 1 + factor, delta=RATIO_TOLERANCE
            )

    def test_amounts_follow_tabelcorrectiefactor(self):
        for year, factor in TABELCORRECTIEFACTOR.items():
            previous, current = TAX_DATA[str(year - 1)], TAX_DATA[str(year)]
            for name, table in weight_tables(current).items():
                previous_table = weight_tables(previous)[name]
                for key, value in table.items():
                    with self.subTest(year=year, table=name, weight=key):
                        self.assert_indexed(previous_table[key], value, factor)
            with self.subTest(year=year, table="motorcycle"):
                self.assert_indexed(
                    previous["motorcycle"]["value"],
                    current["motorcycle"]["value"],
                    factor,
                )

    def test_kwarttarief_maximum_follows_tabelcorrectiefactor(self):
        """The maximum is rounded to whole euros"""
        for year, factor in TABELCORRECTIEFACTOR.items():
            with self.subTest(year=year):
                previous = TAX_DATA[str(year - 1)]["kwarttarief"]["value"]
                current = TAX_DATA[str(year)]["kwarttarief"]["value"]
                self.assertAlmostEqual(current, previous * (1 + factor), delta=1)
