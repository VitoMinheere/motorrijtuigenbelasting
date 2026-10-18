from dataclasses import dataclass
from enum import Enum


class TaxRule(str, Enum):
    NORMAL = "normal"
    # Wet MRB 1994 art. 84a: paid once per year, using last year's tariff
    KWARTTARIEF = "kwarttarief"
    # Wet MRB 1994 art. 72 lid 1b: 40 years or older, no tax
    OLDTIMER = "oldtimer"


@dataclass(frozen=True)
class TaxBreakdown:
    """
    How the tax for one vehicle, year and province is built up.

    Attributes:
        year (int): Year the tax is due for.
        tariff_year (int): Year of the tariff used, the previous year for the kwarttarief.
        rule (TaxRule): Which rule applies.
        components (dict): Parts of the hoofdsom per three months, before discounts,
            e.g. {"base": ..., "fuel_surcharge": ..., "fijnstoftoeslag": ...}.
        opcenten (float): Provincial opcenten per three months, before discounts.
        emission_factor (float): Share that is due after zero/low emission discounts.
        maximum (float | None): Maximum per year for the kwarttarief.
        per_three_months (int): Same as `calculate_total_tax`.
        per_year (int): Same as `calculate_yearly_tax`.
    """

    year: int
    tariff_year: int
    rule: TaxRule
    components: dict
    opcenten: float
    emission_factor: float
    maximum: float | None
    per_three_months: int
    per_year: int

    @property
    def hoofdsom(self) -> float:
        return sum(self.components.values())

    @property
    def unrounded(self) -> float:
        """Hoofdsom plus opcenten after discounts, before the maximum and rounding."""
        return (self.hoofdsom + self.opcenten) * self.emission_factor
