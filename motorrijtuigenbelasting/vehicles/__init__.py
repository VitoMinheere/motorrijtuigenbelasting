import datetime
import json
import math
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

with open(Path(__file__).parent.parent / "data" / "tax_data.json", "r") as f:
    TAX_DATA = json.load(f)


def get_tax_value(year: int, category: str, key: str):
    return TAX_DATA[str(year)][category][key]


def round_down(amount: float) -> int:
    """Round down to whole euros, after rounding to cents so 35.9999... counts as 36."""
    return math.floor(round(amount, 2))


class EnergySource(Enum):
    BENZINE = "benzine"
    DIESEL = "diesel"
    LPG = "overige"
    LPG_G3 = "lpg_g3"
    ELEKTRICITEIT = "elektriciteit"
    OVERIGE = "overige"


class Vehicle(ABC):
    """
    Abstract base class representing a generic vehicle.

    All amounts are per tijdvak of three months, which is how the law states them.

    Attributes:
        rounded_weight (int): Eigen massa of the vehicle, rounded to the nearest hundred kilograms.
        energy_source (EnergySource): The type of energy source used by the vehicle (e.g., benzine, diesel, electric).
        manufacturing_year (int, optional): The year the vehicle was first taken into use.

    Args:
        weight (int): Eigen massa of the vehicle in kilograms.
        energy_source (EnergySource): An instance of the `EnergySource` enum representing the vehicle's fuel type.
        manufacturing_year (int, optional): The year the vehicle was first taken into use.
    """

    def __init__(
        self,
        weight: int,
        energy_source: EnergySource,
        manufacturing_year: int = datetime.date.today().year,
    ):
        # Wet MRB 1994 art. 22 lid 1b: round to the nearest 100 kg, exactly 50 kg rounds down
        self.rounded_weight = 100 * ((weight + 49) // 100)
        self.energy_source = energy_source
        self.manufacturing_year = manufacturing_year
        self.calculation_year = datetime.date.today().year

    def set_calculation_year(self, year: int):
        self.calculation_year = year

    @abstractmethod
    def calculate_base_tax(self, year: int) -> float:
        """Hoofdsom: the tax according to the tariff of the given year, before discounts."""

    @abstractmethod
    def calculate_opcenten(self, province: str, year: int) -> float:
        """Provincial opcenten for the given province and year."""

    def emission_factor(self, year: int) -> float:
        """Share of the tax that is due after zero/low emission discounts."""
        return 1.0

    def calculate_quarterly_tax(self, tariff_year: int, province: str) -> float:
        """Hoofdsom of `tariff_year` plus opcenten of the calculation year, after discounts."""
        tax = self.calculate_base_tax(tariff_year) + self.calculate_opcenten(
            province, self.calculation_year
        )
        return tax * self.emission_factor(tariff_year)

    def calculate_total_tax(self, year: int, province: str) -> int:
        """
        Calculate the tax due per three months, rounded down to whole euros.

        Args:
            year (int): Year for which tax is calculated.
            province (str): Province where the vehicle is registered.

        Returns:
            int: Total tax amount.
        """
        self.set_calculation_year(year)

        if self.is_historic():
            return 0

        # Belastingdienst always rounds down to a whole number (Wet MRB 1994 art. 82)
        if self.is_kwarttarief():
            # Wet MRB 1994 art. 84a: paid once per year, using the quarterly tariff of
            # the previous year including opcenten, up to a maximum. Returned per three
            # months so it can be compared with the other results.
            yearly_tax = min(
                self.calculate_quarterly_tax(year - 1, province),
                get_tax_value(year, "kwarttarief", "value"),
            )
            return round_down(yearly_tax) // 4

        return round_down(self.calculate_quarterly_tax(year, province))

    def is_historic(self) -> bool:
        """Oldtimer ruling applies when vehicle was taken into use 40 or more years ago"""
        return self.calculation_year - self.manufacturing_year >= 40

    def is_kwarttarief(self) -> bool:
        """Kwarttarief applies when a vehicle is taken into use before 1988 and is not yet 40 years old"""
        return self.manufacturing_year < 1988 and not self.is_historic()

    def is_electric(self) -> bool:
        return self.energy_source == EnergySource.ELEKTRICITEIT

    def calculate_multiplier(self, cut_off: int = 900, step: int = 100) -> int:
        """Calculate the amount of weight steps above the cut off

        Args:
            cut_off (int, optional): amount of weight from where to start counting. Defaults to 900.
            step (int, optional): Steps to divide by. Defaults to 100.

        Returns:
            int: Amount of times the extra tax will be added
        """
        if self.rounded_weight > cut_off:
            return (self.rounded_weight - cut_off) // step
        return 0

    def rate_for_weight(self, table: dict) -> float:
        """Look up the rate for the rounded weight in a weight table from the law.

        Tables have fixed amounts per weight (e.g. "500": up to and including 500 kg).
        A "per_100kg_above_X" key means the amount at X kg is increased by that rate for
        every 100 kg above X. The highest applicable X is used, e.g. 900 or 3300.
        """
        steps = [
            int(key.removeprefix("per_100kg_above_"))
            for key in table
            if key.startswith("per_100kg_above_")
        ]
        for cut_off in sorted(steps, reverse=True):
            if self.rounded_weight >= cut_off:
                return table[str(cut_off)] + table[
                    f"per_100kg_above_{cut_off}"
                ] * self.calculate_multiplier(cut_off=cut_off)
        return table[str(max(self.rounded_weight, 500))]
