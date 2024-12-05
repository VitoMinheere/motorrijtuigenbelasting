from vehicles import Vehicle, EnergySource
from .constants import OPCENTEN


class Motorcycle(Vehicle):
    """Motorcycles have a fixed price per quarter with added opcenten

    Args:
        Vehicle (_type_): _description_
    """

    def __init__(self, weight: int, energy_source: EnergySource, manufacturing_year: int = None):
        super().__init__(weight, energy_source, manufacturing_year)

    def calculate_base_tax(self, year: int) -> float:
        """Motorcycles, or any verhicle with less than four wheels are taxed the same rate without any inflation
        https://wetten.overheid.nl/jci1.3:c:BWBR0006324&hoofdstuk=IV&afdeling=4&z=2024-01-01&g=2024-01-01
        """
        return 29.96

    def calculate_opcenten(self, province: str, year: int) -> float:
        """Calculate the provincional added taxes
        For motorcycle is it set to a single amount
        https://zoek.officielebekendmakingen.nl/blg-1106771.pdf

        Args:
            weight (int): Rounded weight of vehicle
            province (str): Name of the province
            year (int): Year of calculation

        Returns:
            float: Amount of tax added
        """
        return 7.80 * (OPCENTEN[province][year] / 100)

    def calculate_total_tax(self, province: str, year: int) -> float:
        """Abstract method to calculate the total tax, optionally using province."""
        self.set_calculation_year(year)
        base_tax = self.calculate_base_tax(year)

        # Provincial opcenten tax
        opcenten = round(self.calculate_opcenten(province, year), 2)

        total_tax = base_tax + opcenten
        # Apply discounts
        total_tax = self.apply_electric_tax_discount(total_tax)
        total_tax = self.apply_historic_tax_discount(total_tax)
        
        return int(total_tax)
