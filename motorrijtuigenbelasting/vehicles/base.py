import datetime
from abc import ABC, abstractmethod

from ..tax_data import (
    get_tax_value,
    opcenten_percentage,
    round_down,
    round_weight,
    steps_above,
)
from .energy_source import EnergySource

# Wet MRB 1994 art. 72 lid 1b
OLDTIMER_AGE = 40
# Wet MRB 1994 art. 84a lid 3a
KWARTTARIEF_BEFORE_YEAR = 1988


class Vehicle(ABC):
    """
    Abstract base class representing a generic vehicle.

    All amounts are per tijdvak of three months, which is how the law states them,
    unless the method name says otherwise.

    Attributes:
        rounded_weight (int): Eigen massa of the vehicle, rounded to the nearest hundred kilograms.
        energy_source (EnergySource): The type of energy source used by the vehicle (e.g., benzine, diesel, electric).
        manufacturing_year (int): The year the vehicle was first taken into use.

    Args:
        weight (int): Eigen massa of the vehicle in kilograms.
        energy_source (EnergySource): An instance of the `EnergySource` enum representing the vehicle's fuel type.
        manufacturing_year (int, optional): The year the vehicle was first taken into use. Defaults to this year.
    """

    # Category in tax_data.json that holds the rates for this vehicle type
    TAX_CATEGORY: str

    def __init__(
        self,
        weight: int,
        energy_source: EnergySource,
        manufacturing_year: int | None = None,
    ):
        self.rounded_weight = round_weight(weight)
        self.energy_source = energy_source
        self.manufacturing_year = (
            manufacturing_year
            if manufacturing_year is not None
            else datetime.date.today().year
        )

    @abstractmethod
    def calculate_base_tax(self, year: int) -> float:
        """Hoofdsom: the tax according to the tariff of the given year, before discounts."""

    @abstractmethod
    def opcenten_base(self) -> float:
        """Fixed amount the provincial opcenten percentage is applied to."""

    def calculate_opcenten(self, province: str, year: int) -> float:
        """Provincial opcenten for the given province and year (Provinciewet art. 222)."""
        return self.opcenten_base() * opcenten_percentage(year, province) / 100

    def emission_factor(self, year: int) -> float:
        """Share of the tax that is due after zero emission discounts."""
        if self.is_electric():
            return get_tax_value(year, self.TAX_CATEGORY, "zero_emission_factor")
        return 1.0

    def calculate_quarterly_tax(
        self, year: int, province: str, tariff_year: int | None = None
    ) -> float:
        """
        Unrounded hoofdsom plus opcenten of `year`, after discounts.

        `tariff_year` selects another year's hoofdsom, which the kwarttarief needs.
        """
        tariff_year = year if tariff_year is None else tariff_year
        tax = self.calculate_base_tax(tariff_year) + self.calculate_opcenten(
            province, year
        )
        return tax * self.emission_factor(tariff_year)

    def calculate_total_tax(self, year: int, province: str) -> int:
        """
        Calculate the tax due per three months, rounded down to whole euros.

        The kwarttarief is paid once per year, so for those vehicles this is a quarter
        of `calculate_yearly_tax`, rounded down, to compare it with other vehicles.

        Args:
            year (int): Year for which tax is calculated.
            province (str): Province where the vehicle is registered.

        Returns:
            int: Total tax amount.
        """
        if self.is_kwarttarief(year):
            return self.calculate_yearly_tax(year, province) // 4
        if self.is_historic(year):
            return 0

        # Belastingdienst always rounds down to a whole number (Wet MRB 1994 art. 82)
        return round_down(self.calculate_quarterly_tax(year, province))

    def calculate_yearly_tax(self, year: int, province: str) -> int:
        """
        Calculate the tax due for a whole year, rounded down to whole euros.

        Wet MRB 1994 art. 84a: with the kwarttarief the tijdvak is a calendar year and
        the tax is the quarterly tariff as it was on 31 December of the previous year,
        including this year's opcenten, up to a maximum.
        """
        if self.is_kwarttarief(year):
            return round_down(
                min(
                    self.calculate_quarterly_tax(year, province, tariff_year=year - 1),
                    get_tax_value(year, "kwarttarief", "value"),
                )
            )
        return 4 * self.calculate_total_tax(year, province)

    def is_historic(self, year: int) -> bool:
        """Oldtimer ruling applies when vehicle was taken into use 40 or more years ago"""
        return year - self.manufacturing_year >= OLDTIMER_AGE

    def is_kwarttarief(self, year: int) -> bool:
        """Kwarttarief applies when a vehicle is taken into use before 1988 and is not yet 40 years old"""
        return (
            self.manufacturing_year < KWARTTARIEF_BEFORE_YEAR
            and not self.is_historic(year)
        )

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
        return steps_above(self.rounded_weight, cut_off, step)
