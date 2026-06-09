from datetime import date

from ..vehicles import Vehicle, EnergySource, get_tax_value
from .constants import INFLATION, WEIGHT_TAX_BRACKETS, EXCESS_RATES

BENZINE_CUTOFF = 900
LPG_CUTOFF = 900


class Car(Vehicle):
    def __init__(
        self,
        weight: int,
        energy_source: EnergySource,
        manufacturing_year: int = date.today().year,
        co2_emissions: bool = False,
        diesel_particles: bool = False,
    ):
        super().__init__(weight, energy_source, manufacturing_year)
        self.low_co2_emissions = co2_emissions
        self.diesel_particles = diesel_particles

    def calculate_base_tax(
        self,
        cutoff: int = BENZINE_CUTOFF,
    ) -> float:
        """
        Generalized base tax calculator based on weight and energy source.
        source: https://wetten.overheid.nl/jci1.3:c:BWBR0006324&hoofdstuk=IV&afdeling=2&artikel=23&z=2023-01-01&g=2023-01-01

        Args:
            weight (int): Rounded weight of the vehicle.
            energy_source (str): The energy source category (default, diesel, overige).
            cutoff (int): Weight threshold for applying excess rates.

        Returns:
            float: The base tax for the given weight and energy source.
        """
        tax_brackets = get_tax_value(self.calculation_year, "weight_tax", self.energy_source.value) 
        excess_rate = get_tax_value(self.calculation_year, "excess_rates_<3300", self.energy_source.value)

        # Apply excess rate for weights above the cutoff
        if self.rounded_weight >= cutoff:
            base_rate = tax_brackets[str(cutoff)]
            if self.rounded_weight >= 3300:
                base_rate = list(tax_brackets.items())[-1][1]  # Use the last bracket's rate as the base
                excess_rate = get_tax_value(self.calculation_year, "excess_rates_>3300", self.energy_source.value)
                return base_rate + (excess_rate * (self.calculate_multiplier(cut_off=3300)))

            multiplier = self.calculate_multiplier(cutoff)
            if self.energy_source == EnergySource.LPG_G3:
                multiplier += 1  # LPG has a different cutoff, so we need to add 1 to the multiplier
            return base_rate + int(multiplier * excess_rate)

        for max_weight, rate in tax_brackets.items():
            if self.rounded_weight <= int(max_weight):
                return rate

        return 0.0

    def calculate_fuel_tax(self, base_tax: float) -> float:
        """Calculate extra fuel tax based on energy source."""
        if self.energy_source == EnergySource.DIESEL and self.diesel_particles:
            # Fijnstoftoeslag
            return (0.19 * base_tax)

        return 0.0

    def calculate_total_tax(self, year: int, province: str) -> float:
        """
        Calculate the total tax for a vehicle based on various components.

        Args:
            energy_source (EnergySource): The energy source type of the vehicle.
            weight (int): Weight of the vehicle in kg.
            province (str): Province where the vehicle is registered.
            year (int): Year for which tax is calculated.

        Returns:
            float: Total tax amount.
        """
        self.set_calculation_year(year)
        base_tax = round(self.calculate_base_tax(), 2)

        # Fuel-specific tax
        fuel_tax = round(self.calculate_fuel_tax(base_tax), 2)
        base_tax += fuel_tax

        # Apply inflation adjustment if applicable
        if year in INFLATION:
            inflation = get_tax_value(self.calculation_year, "inflation", "value")
            base_tax = round(base_tax * (1 + inflation), 2)

        # Provincial opcenten tax
        opcenten = round(self.calculate_opcenten(province, year), 2)

        total_tax = base_tax + opcenten
        # Apply discounts
        total_tax = self.apply_kwarttarief_discount(total_tax)
        total_tax = self.apply_historic_tax_discount(total_tax)
        total_tax = self.apply_low_emission_tax_discount(
            total_tax, self.low_co2_emissions
        )
        total_tax = self.apply_electric_tax_discount(total_tax)

        # Belastingdienst always rounds down to a whole number
        # https://www.cbs.nl/nl-nl/nieuws/2019/50/bijna-6-1-miljard-euro-aan-wegenbelasting-in-2020/afronding-motorrijtuigenbelasting
        return int(total_tax)
