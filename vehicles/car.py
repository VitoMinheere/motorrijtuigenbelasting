from vehicles import Vehicle, EnergySource
from .constants import INFLATION, WEIGHT_TAX_BRACKETS, EXCESS_RATES

BENZINE_CUTOFF = 900
LPG_CUTOFF = 800


class Car(Vehicle):
    def __init__(
        self,
        weight: int,
        energy_source: EnergySource,
        manufacturing_year: int = None,
        co2_emissions: bool = False,
    ):
        super().__init__(weight, energy_source, manufacturing_year)
        self.co2_emissions = co2_emissions

    def calculate_base_tax(
        self,
        energy_source: EnergySource = EnergySource.BENZINE,
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
        tax_brackets = WEIGHT_TAX_BRACKETS[energy_source.value]
        excess_rate = EXCESS_RATES[energy_source.value]

        # Apply excess rate for weights above the cutoff
        if self.rounded_weight >= cutoff:
            if self.rounded_weight >= 3300:
                return 424.29 + (10.48 * (self.calculate_multiplier(cut_off=3300) - 1))

            multiplier = self.calculate_multiplier(cutoff)
            base_rate = tax_brackets[-1][1]  # Use the last bracket's rate as the base
            return base_rate + (multiplier * excess_rate)

        for max_weight, rate in tax_brackets:
            if self.rounded_weight <= max_weight:
                return rate

        return 0.0

    def calculate_fuel_tax(self, base_tax: float) -> float:
        """Calculate extra fuel tax based on energy source."""
        if (
            self.energy_source == EnergySource.LPG_G3
            and self.rounded_weight > LPG_CUTOFF
        ):
            return 16.64 * self.calculate_multiplier(cut_off=LPG_CUTOFF)

        if self.energy_source == EnergySource.DIESEL and self.co2_emissions:
            # Fijnstoftoeslag
            return (
                1.19
                * (base_tax + self.calculate_base_tax(energy_source=self.energy_source))
                - base_tax
            )

        if self.energy_source not in [
            EnergySource.BENZINE,
            EnergySource.ELEKTRICITEIT,
        ]:
            return self.calculate_base_tax(energy_source=self.energy_source)

        # elif self.energy_source in [EnergySource.LPG, EnergySource.OVERIGE]:
        #     return self.calculate_base_tax(energy_source="overige")
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
            base_tax = round(base_tax * (1 + INFLATION[year]), 2)

        # Provincial opcenten tax
        opcenten = round(self.calculate_opcenten(province, year), 2)

        total_tax = base_tax + opcenten
        # Apply discounts
        total_tax = self.apply_kwarttarief_discount(total_tax)
        total_tax = self.apply_historic_tax_discount(total_tax)
        total_tax = self.apply_electric_tax_discount(total_tax)

        # Belastingdienst always rounds down to a whole number
        # https://www.cbs.nl/nl-nl/nieuws/2019/50/bijna-6-1-miljard-euro-aan-wegenbelasting-in-2020/afronding-motorrijtuigenbelasting
        return int(total_tax)
