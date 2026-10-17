from ..tax_data import get_tax_value, rate_for_weight
from .base import Moment, Vehicle
from .constants import MASSA_RIJKLAAR_OFFSET, OPCENTEN_BASE
from .energy_source import EnergySource

# Brandstoftoeslag table per energy source (art. 23 lid 2 and 3). Benzine, electric and
# hydrogen cars pay none, LPG pays the same as other fuels unless it has a G3 installation.
FUEL_SURCHARGE_TABLE = {
    EnergySource.DIESEL: "diesel",
    EnergySource.LPG: "overige",
    EnergySource.LPG_G3: "lpg_g3",
    EnergySource.OVERIGE: "overige",
}


class Car(Vehicle):
    """
    Personenauto.

    Args:
        weight (int): Massa rijklaar in kg, as shown in the RDW kentekenregister.
        energy_source (EnergySource): Fuel type as registered.
        manufacturing_year (int | date, optional): Datum eerste toelating, or only its year.
        co2_emissions (bool, optional): CO2 emission above 0 but at most 50 g/km.
        diesel_particles (bool, optional): Particle emission above the Euro 5 limit.
    """

    TAX_CATEGORY = "car"

    def __init__(
        self,
        weight: int,
        energy_source: EnergySource,
        manufacturing_year: Moment | None = None,
        co2_emissions: bool = False,
        diesel_particles: bool = False,
    ):
        super().__init__(
            weight - MASSA_RIJKLAAR_OFFSET, energy_source, manufacturing_year
        )
        self.low_co2_emissions = co2_emissions
        self.diesel_particles = diesel_particles

    def calculate_base_tax(self, year: int) -> float:
        """
        Hoofdsom: weight based tax plus brandstoftoeslag and fijnstoftoeslag.
        source: https://wetten.overheid.nl/jci1.3:c:BWBR0006324&hoofdstuk=IV&afdeling=2&artikel=23&z=2026-01-01&g=2026-01-01
        """
        tax = self.rate_for_weight(get_tax_value(year, "car", "base"))
        tax += self.calculate_fuel_surcharge(year)

        if self.energy_source == EnergySource.DIESEL and self.diesel_particles:
            # Art. 23 lid 4, a percentage of the tax including brandstoftoeslag
            tax *= 1 + get_tax_value(year, "car", "fijnstoftoeslag")

        return tax

    def calculate_fuel_surcharge(self, year: int) -> float:
        """Brandstoftoeslag (art. 23 lid 2 and 3). Benzine, electric and hydrogen cars pay none."""
        table = FUEL_SURCHARGE_TABLE.get(self.energy_source)
        if table is None:
            return 0.0
        return self.rate_for_weight(get_tax_value(year, "car", "fuel_surcharge")[table])

    def opcenten_base(self) -> float:
        """
        Opcenten are levied over the 1995 tariff. The brandstoftoeslag is left out.
        Source: Provinciewet art. 222 lid 3
        """
        return self.rate_for_weight(OPCENTEN_BASE)

    def emission_factor(self, year: int) -> float:
        """Zero and low emission discount (art. 23b), applies to the opcenten as well."""
        if not self.is_zero_emission() and self.low_co2_emissions:
            return get_tax_value(year, "car", "low_emission_factor")
        return super().emission_factor(year)

    def is_kwarttarief(self, year: Moment) -> bool:
        """Only benzine cars can use the kwarttarief (art. 84a lid 3b)"""
        return self.energy_source == EnergySource.BENZINE and super().is_kwarttarief(
            year
        )

    def rate_for_weight(self, table: dict) -> float:
        return rate_for_weight(table, self.rounded_weight)
