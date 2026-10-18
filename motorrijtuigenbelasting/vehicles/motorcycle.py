from ..tax_data import get_tax_value
from .base import Vehicle
from .constants import MOTORCYCLE_OPCENTEN_BASE


class Motorcycle(Vehicle):
    """
    Represents a motorcycle for road tax calculations.

    Motorcycles have a fixed base tax per quarter, with additional opcenten
    based on the province.

    Zero emission motorcycles (motorcycle.zero_emission_factor in tax_data.json):
    up to 2024 the tax was nihil and in 2025 a quarter, both under art. 31. Art. 31
    was removed on 1 January 2026 and art. 23b only covers personenauto's, so from
    2026 they pay the full amount.

    Args:
        weight (int): Weight of the motorcycle (not used in tax calculation).
        energy_source (EnergySource): The type of energy source (e.g., gasoline, electric).
        manufacturing_year (int, optional): Year the motorcycle was manufactured.
    """

    TAX_CATEGORY = "motorcycle"

    def tax_components(self, year: int) -> dict[str, float]:
        """
        Fixed base tax for motorcycles (art. 25).
        Source: https://wetten.overheid.nl/jci1.3:c:BWBR0006324&hoofdstuk=IV&afdeling=4&z=2026-01-01&g=2026-01-01
        """
        return {"base": get_tax_value(year, "motorcycle", "value")}

    def opcenten_base(self) -> float:
        """
        Opcenten for motorcycles are a percentage of a fixed amount.
        Source: https://zoek.officielebekendmakingen.nl/blg-1106771.pdf
        """
        return MOTORCYCLE_OPCENTEN_BASE
