from vehicle_types import EnergySource
from constants import (
    WEIGHT_TAX_BRACKETS,
    EXCESS_RATES,
    INFLATION,
    OPCENTEN_BRACKETS,
    OPCENTEN,
)


def calc_multiplier(weight: int, cut_off: int = 900, step: int = 100) -> int:
    """Calculate the added tax based on weight of vehicle

    Args:
        weight (int): Rounded weight of vehicle
        cut_off (int, optional): amount of weight from where to start counting. Defaults to 900.
        step (int, optional): Steps to divide by. Defaults to 100.

    Returns:
        int: Amount of times the extra tax will be added
    """
    if weight > cut_off:
        return round((weight - cut_off) // step)
    return 0


def calc_fuel_tax(energy_source: EnergySource, weight: int) -> float:
    """Calculate extra fuel tax based on energy source."""
    if energy_source == EnergySource.DIESEL:
        return calculate_base_tax(weight, energy_source="diesel")
    elif energy_source == EnergySource.LPG_G3 and weight > 800:
        return round(16.64 * calc_multiplier(weight, cut_off=800))
    elif energy_source in [EnergySource.LPG, EnergySource.OVERIGE]:
        return calculate_base_tax(weight, energy_source="overige")
    return 0.0


def calculate_base_tax(
    weight: int, energy_source: str = "benzine", cutoff: int = 900
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
    tax_brackets = WEIGHT_TAX_BRACKETS[energy_source]
    excess_rate = EXCESS_RATES[energy_source]

    # Apply excess rate for weights above the cutoff
    if weight >= cutoff:
        multiplier = calc_multiplier(weight, cutoff)
        base_rate = tax_brackets[-1][1]  # Use the last bracket's rate as the base
        return base_rate + (multiplier * excess_rate)
        # TODO won't work for BENZINE > 3300
        # return 424.29 + (10.48 * calc_multiplier(weight, cut_off=3300))
    else:
        for max_weight, rate in tax_brackets:
            if weight <= max_weight:
                return rate

    return 0.0


def calc_opcenten(weight: int, province: str, year: int) -> float:
    """Calculate the provincional added taxes

    Args:
        weight (int): Rounded weight of vehicle
        province (str): Name of the province
        year (int): Year of calculation

    Returns:
        float: Amount of tax added
    """
    opcenten_brackets = OPCENTEN_BRACKETS
    excess_rate = EXCESS_RATES["opcenten"]
    cutoff = 900
    base_rate = 0

    # Apply excess rate for weights above the cutoff
    if weight >= cutoff:
        multiplier = calc_multiplier(weight, cutoff) - 1
        rate = opcenten_brackets[-1][1]  # Use the last bracket's rate as the base
        base_rate = rate + (multiplier * excess_rate)
    else:
        for max_weight, rate in opcenten_brackets:
            if weight <= max_weight:
                base_rate = rate
                break

    return int(base_rate * (OPCENTEN[province][year] / 100))


def calculate_tax(
    energy_source: EnergySource, weight: int, province: str, year: int
) -> float:
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
    rounded_weight = 100 * round(weight / 100)

    base_tax = calculate_base_tax(rounded_weight)

    # Step 3: Handle energy-specific adjustments
    if energy_source == EnergySource.ELEKTRICITEIT:
        if year < 2025:
            return 0  # No tax for electric cars before 2025
        elif year == 2025:
            base_tax *= 0.25  # 25% of base tax
        elif 2026 <= year <= 2029:
            base_tax *= 0.75  # 75% of base tax
        else:
            base_tax *= 1.0  # 100% of base tax

    # Fuel-specific tax
    fuel_tax = calc_fuel_tax(energy_source, rounded_weight)
    base_tax += fuel_tax

    # Apply inflation adjustment if applicable
    if year in INFLATION:
        base_tax *= 1 + INFLATION[year]

    # Provincial opcenten tax
    opcenten = calc_opcenten(rounded_weight, province, year)

    return round(base_tax + opcenten)
