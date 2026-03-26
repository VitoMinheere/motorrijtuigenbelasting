from ..vehicles import Vehicle, get_tax_value
from .constants import OPCENTEN


class Motorcycle(Vehicle):
    """
    Represents a motorcycle for road tax calculations.

    Motorcycles have a fixed base tax per quarter, with additional opcenten
    based on the province. They are not subject to inflation adjustments.

    Args:
        weight (int): Weight of the motorcycle (not used in tax calculation).
        energy_source (EnergySource): The type of energy source (e.g., gasoline, electric).
        manufacturing_year (int, optional): Year the motorcycle was manufactured.
    """

    def calculate_base_tax(self) -> float:
        """
        Calculates the fixed base tax for motorcycles. This rate is fixed and
        does not change based on inflation.
        Source: https://wetten.overheid.nl/jci1.3:c:BWBR0006324&hoofdstuk=IV&afdeling=4&z=2024-01-01&g=2024-01-01

        Args:
            year (int): The year for which the tax is calculated.

        Returns:
            float: The fixed base tax amount.
        """
        return get_tax_value(self.calculation_year, "motorcycle", "value")

    def calculate_opcenten(self, province: str, year: int) -> float:
        """
        Calculates the provincial opcenten tax for motorcycles. This is a percentage
        of a fixed amount.
        Source: https://zoek.officielebekendmakingen.nl/blg-1106771.pdf

        Args:
            province (str): Name of the province.
            year (int): The year for which the tax is calculated.

        Returns:
            float: The calculated opcenten tax amount.
        """
        fixed_opcenten_base = 7.80
        opcenten = get_tax_value(year, "opcenten", province)
        province_rate = opcenten / 100
        return fixed_opcenten_base * province_rate

    def apply_electric_tax_discount(self, tax: float) -> float:
        if self.is_electric():
            if self.calculation_year < 2025:
                return 0  # No tax for electric cars before 2025
            if self.calculation_year == 2025:
                tax *= 0.25  # 25% of base tax
            # Electric discount ends in 2025 for motorcycles

        return tax

    def calculate_total_tax(self, year: int, province: str) -> int:
        """
        Calculates the total tax for the motorcycle, including the base tax
        and provincial opcenten, rounded down to the nearest whole number.

        Args:
            province (str): Name of the province.
            year (int): The year for which the tax is calculated.

        Returns:
            int: The total road tax amount.
        """
        self.set_calculation_year(year)

        base_tax = self.calculate_base_tax()
        opcenten = round(self.calculate_opcenten(province, year), 2)

        total_tax = base_tax + opcenten
        total_tax = self.apply_electric_tax_discount(total_tax)
        total_tax = self.apply_kwarttarief_discount(total_tax)
        total_tax = self.apply_historic_tax_discount(total_tax)

        return int(total_tax)
