from ..vehicles import Vehicle, get_tax_value
from .constants import MOTORCYCLE_OPCENTEN_BASE


class Motorcycle(Vehicle):
    """
    Represents a motorcycle for road tax calculations.

    Motorcycles have a fixed base tax per quarter, with additional opcenten
    based on the province.

    Args:
        weight (int): Weight of the motorcycle (not used in tax calculation).
        energy_source (EnergySource): The type of energy source (e.g., gasoline, electric).
        manufacturing_year (int, optional): Year the motorcycle was manufactured.
    """

    def calculate_base_tax(self, year: int) -> float:
        """
        Calculates the fixed base tax for motorcycles.
        Source: https://wetten.overheid.nl/jci1.3:c:BWBR0006324&hoofdstuk=IV&afdeling=4&z=2026-01-01&g=2026-01-01
        """
        return get_tax_value(year, "motorcycle", "value")

    def calculate_opcenten(self, province: str, year: int) -> float:
        """
        Calculates the provincial opcenten tax for motorcycles. This is a percentage
        of a fixed amount.
        Source: https://zoek.officielebekendmakingen.nl/blg-1106771.pdf
        """
        opcenten = get_tax_value(year, "opcenten", province)
        return MOTORCYCLE_OPCENTEN_BASE * opcenten / 100

    def emission_factor(self, year: int) -> float:
        # Not verified against the law text: art. 23b only covers personenauto's.
        if self.is_electric():
            if year < 2025:
                return 0.0  # No tax for electric motorcycles before 2025
            if year == 2025:
                return 0.25
        return 1.0
