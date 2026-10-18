import datetime
import functools
import inspect
import warnings
from abc import ABC, abstractmethod

from ..breakdown import TaxBreakdown, TaxRule
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
KWARTTARIEF_BEFORE = datetime.date(1988, 1, 1)

ZERO_EMISSION_SOURCES = {EnergySource.ELEKTRICITEIT, EnergySource.WATERSTOF}

# A year means 1 January of that year
Moment = int | datetime.date


def as_date(moment: Moment) -> datetime.date:
    if isinstance(moment, datetime.date):
        return moment
    return datetime.date(moment, 1, 1)


def keyword_only(method):
    """Accept the keyword-only arguments positionally, with a DeprecationWarning.

    The positional order is the order of the keyword-only parameters, which matches
    the old signatures, e.g. calculate_opcenten(province, year).
    """
    names = [
        name
        for name, parameter in inspect.signature(method).parameters.items()
        if parameter.kind == inspect.Parameter.KEYWORD_ONLY
    ]

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if args:
            passed = names[: len(args)]
            warnings.warn(
                f"Pass {', '.join(passed)} to {method.__name__}() as keyword "
                "arguments, positional arguments will stop working in a later release",
                DeprecationWarning,
                stacklevel=2,
            )
            kwargs.update(zip(passed, args))
        return method(self, **kwargs)

    return wrapper


def anniversary(start: datetime.date, years: int) -> datetime.date:
    """The same day `years` later, 29 February moves to 1 March."""
    try:
        return start.replace(year=start.year + years)
    except ValueError:
        return datetime.date(start.year + years, 3, 1)


class Vehicle(ABC):
    """
    Abstract base class representing a generic vehicle.

    All amounts are per tijdvak of three months, which is how the law states them,
    unless the method name says otherwise.

    Attributes:
        rounded_weight (int): Eigen massa of the vehicle, rounded to the nearest hundred kilograms.
        energy_source (EnergySource): The type of energy source used by the vehicle (e.g., benzine, diesel, electric).
        first_admission (date): Datum eerste toelating, when the vehicle was first taken into use.
        manufacturing_year (int): The year of first_admission.

    Args:
        weight (int): Eigen massa of the vehicle in kilograms.
        energy_source (EnergySource): An instance of the `EnergySource` enum representing the vehicle's fuel type.
        manufacturing_year (int | date, optional): Datum eerste toelating, or only its year,
            which counts as 1 January. Defaults to today.

    Methods that take a `year` also accept a date. The tariff of that date's year is
    used, and the date decides whether the oldtimer rule applies.
    """

    # Category in tax_data.json that holds the rates for this vehicle type
    TAX_CATEGORY: str

    def __init__(
        self,
        weight: float,
        energy_source: EnergySource | str,
        manufacturing_year: Moment | None = None,
    ):
        if (
            isinstance(weight, bool)
            or not isinstance(weight, int | float)
            or weight < 0
        ):
            raise ValueError(
                f"weight must be a number of kg of 0 or more, got {weight!r}"
            )
        self.rounded_weight = round_weight(weight)
        # Also accepts the value, e.g. "benzine", and raises ValueError for unknown ones
        self.energy_source = EnergySource(energy_source)
        self.first_admission = (
            as_date(manufacturing_year)
            if manufacturing_year is not None
            else datetime.date.today()
        )

    @property
    def manufacturing_year(self) -> int:
        return self.first_admission.year

    @abstractmethod
    def tax_components(self, year: int) -> dict[str, float]:
        """Parts of the hoofdsom by name, according to the tariff of the given year."""

    def calculate_base_tax(self, year: int) -> float:
        """Hoofdsom: the tax according to the tariff of the given year, before discounts."""
        return sum(self.tax_components(year).values())

    @abstractmethod
    def opcenten_base(self) -> float:
        """Fixed amount the provincial opcenten percentage is applied to."""

    @keyword_only
    def calculate_opcenten(self, *, province: str, year: int) -> float:
        """Provincial opcenten for the given province and year (Provinciewet art. 222)."""
        return self.opcenten_base() * opcenten_percentage(year, province) / 100

    def emission_factor(self, year: int) -> float:
        """Share of the tax that is due after zero emission discounts."""
        if self.is_zero_emission():
            return get_tax_value(year, self.TAX_CATEGORY, "zero_emission_factor")
        return 1.0

    @keyword_only
    def calculate_quarterly_tax(
        self, *, year: int, province: str, tariff_year: int | None = None
    ) -> float:
        """
        Unrounded hoofdsom plus opcenten of `year`, after discounts.

        `tariff_year` selects another year's hoofdsom, which the kwarttarief needs.
        """
        tariff_year = year if tariff_year is None else tariff_year
        tax = self.calculate_base_tax(tariff_year) + self.calculate_opcenten(
            province=province, year=year
        )
        return tax * self.emission_factor(tariff_year)

    @keyword_only
    def calculate_breakdown(self, *, year: Moment, province: str) -> TaxBreakdown:
        """
        Calculate the tax and how it is built up.

        Args:
            year (int | date): Year, or the start of the three months, to calculate.
            province (str): Province where the vehicle is registered.
        """
        tax_year = as_date(year).year
        if self.is_kwarttarief(year):
            rule, tariff_year = TaxRule.KWARTTARIEF, tax_year - 1
        elif self.is_historic(year):
            return TaxBreakdown(
                year=tax_year,
                tariff_year=tax_year,
                rule=TaxRule.OLDTIMER,
                components={},
                opcenten=0.0,
                emission_factor=1.0,
                maximum=None,
                per_three_months=0,
                per_year=0,
            )
        else:
            rule, tariff_year = TaxRule.NORMAL, tax_year

        components = self.tax_components(tariff_year)
        opcenten = self.calculate_opcenten(province=province, year=tax_year)
        factor = self.emission_factor(tariff_year)
        unrounded = (sum(components.values()) + opcenten) * factor

        # Belastingdienst always rounds down to a whole number (Wet MRB 1994 art. 82)
        maximum = None
        if rule == TaxRule.KWARTTARIEF:
            # Art. 84a: with the kwarttarief the tijdvak is a calendar year and the tax
            # is the quarterly tariff as it was on 31 December of the previous year,
            # including this year's opcenten, up to a maximum.
            maximum = get_tax_value(tax_year, "kwarttarief", "value")
            per_year = round_down(min(unrounded, maximum))
            per_three_months = per_year // 4
        else:
            per_three_months = round_down(unrounded)
            per_year = 4 * per_three_months

        return TaxBreakdown(
            year=tax_year,
            tariff_year=tariff_year,
            rule=rule,
            components=components,
            opcenten=opcenten,
            emission_factor=factor,
            maximum=maximum,
            per_three_months=per_three_months,
            per_year=per_year,
        )

    @keyword_only
    def calculate_total_tax(self, *, year: Moment, province: str) -> int:
        """
        Calculate the tax due per three months, rounded down to whole euros.

        The kwarttarief is paid once per year, so for those vehicles this is a quarter
        of `calculate_yearly_tax`, rounded down, to compare it with other vehicles.

        Args:
            year (int | date): Year, or the start of the three months, to calculate.
            province (str): Province where the vehicle is registered.

        Returns:
            int: Total tax amount.
        """
        return self.calculate_breakdown(year=year, province=province).per_three_months

    @keyword_only
    def calculate_yearly_tax(self, *, year: Moment, province: str) -> int:
        """Calculate the tax due for a whole year, rounded down to whole euros."""
        return self.calculate_breakdown(year=year, province=province).per_year

    def is_historic(self, year: Moment) -> bool:
        """Oldtimer ruling applies when vehicle was taken into use 40 or more years ago"""
        return as_date(year) >= anniversary(self.first_admission, OLDTIMER_AGE)

    def is_kwarttarief(self, year: Moment) -> bool:
        """Kwarttarief applies when a vehicle is taken into use before 1988 and is not yet 40 years old"""
        return self.first_admission < KWARTTARIEF_BEFORE and not self.is_historic(year)

    def is_electric(self) -> bool:
        return self.energy_source == EnergySource.ELEKTRICITEIT

    def is_zero_emission(self) -> bool:
        """Driven only by electricity or hydrogen (art. 23b lid 1, before 2026 art. 31)"""
        return self.energy_source in ZERO_EMISSION_SOURCES

    def calculate_multiplier(self, cut_off: int = 900, step: int = 100) -> int:
        """Calculate the amount of weight steps above the cut off

        Args:
            cut_off (int, optional): amount of weight from where to start counting. Defaults to 900.
            step (int, optional): Steps to divide by. Defaults to 100.

        Returns:
            int: Amount of times the extra tax will be added
        """
        return steps_above(self.rounded_weight, cut_off, step)
