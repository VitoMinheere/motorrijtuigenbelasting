from datetime import date

from ..vehicles import EnergySource, Vehicle, get_tax_value
from .constants import FIJNSTOFTOESLAG, MASSA_RIJKLAAR_OFFSET, OPCENTEN_BASE


class Car(Vehicle):
    """
    Personenauto.

    Args:
        weight (int): Massa rijklaar in kg, as shown in the RDW kentekenregister.
        energy_source (EnergySource): Fuel type as registered.
        manufacturing_year (int, optional): Year the car was first taken into use.
        co2_emissions (bool, optional): CO2 emission above 0 but at most 50 g/km.
        diesel_particles (bool, optional): Particle emission above the Euro 5 limit.
    """

    def __init__(
        self,
        weight: int,
        energy_source: EnergySource,
        manufacturing_year: int = date.today().year,
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
            tax *= 1 + FIJNSTOFTOESLAG

        return tax

    def calculate_fuel_surcharge(self, year: int) -> float:
        """Brandstoftoeslag (art. 23 lid 2 and 3). Benzine and electric cars pay none."""
        surcharges = get_tax_value(year, "car", "fuel_surcharge")
        if self.energy_source.value not in surcharges:
            return 0.0
        return self.rate_for_weight(surcharges[self.energy_source.value])

    def calculate_opcenten(self, province: str, year: int) -> float:
        """
        Provincial opcenten over the 1995 tariff. The brandstoftoeslag is left out.
        Source: Provinciewet art. 222 lid 3
        """
        opcenten = get_tax_value(year, "opcenten", province)
        return self.rate_for_weight(OPCENTEN_BASE) * opcenten / 100

    def emission_factor(self, year: int) -> float:
        """Zero and low emission discount (art. 23b), applies to the opcenten as well."""
        if self.is_electric():
            return get_tax_value(year, "car", "zero_emission_factor")
        if self.low_co2_emissions:
            return get_tax_value(year, "car", "low_emission_factor")
        return 1.0

    def is_kwarttarief(self) -> bool:
        """Only benzine cars can use the kwarttarief (art. 84a lid 3b)"""
        return self.energy_source == EnergySource.BENZINE and super().is_kwarttarief()
