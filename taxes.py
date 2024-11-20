from enum import Enum

from vehicle_types import EnergySource
from opcenten import OPCENTEN

INFLATION = {
    2024: 0.099
}

# Tax consists of 
# MOTORRIJTUIG + BRANDSTOF for Benzine
# MOTORRIJTUIG + BRANDSTOF_LPG for LPG
# MOTORRIJTUIG + BRANDSTOF + FIJNSTOF for Diesel
class TaxTypes(Enum):
    MOTORRIJTUIG = 'Motorrijtuigenbelasting'
    BRANDSTOF_BENZINE = 'Brandstoftoeslag'
    BRANDSTOF_LPG = 'Brandstoftoeslag'
    BRANDSTOF_DIESEL = 'Brandstoftoeslag'
    FIJNSTOF = 'Fijnstoftoeslag'



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

def vehicle_tax(weight: int) -> float:
    """Calculate base tax for weight class
    source: https://wetten.overheid.nl/jci1.3:c:BWBR0006324&hoofdstuk=IV&afdeling=2&artikel=23&z=2023-01-01&g=2023-01-01
    """
    if weight <= 500: 
        return 18.75
    elif weight <= 600: 
        return 25.44
    elif weight <= 700: 
        return 32.33
    elif weight <= 800: 
        return 42.20
    # From here excess weight is calculated per 100kg
    elif weight >= 900 and weight < 3300:
        return 56.13 + (15.09 * calc_multiplier(weight))
    elif weight >= 3300:
        return 424.29 + (10.48 * calc_multiplier(weight, cut_off=3300))

def calc_opcenten(weight: int, province: str, year: int) -> float:
    """Calculate the provincional added taxes

    Args:
        weight (int): Rounded weight of vehicle
        province (str): Name of the province
        year (int): Year of calculation

    Returns:
        float: Amount of tax added
    """

    base = 0
    if weight <= 500: 
        base = 14.5
    elif weight <= 600: 
        base = 17.33
    elif weight <= 700: 
        base = 20.40
    elif weight <= 800: 
        base =  26.98
    elif weight <= 900:
        base = 34.12
    # From here excess weight is calculated per 100kg
    elif weight > 900 and weight < 3300:
        base = 45.81 + (11.68 * (calc_multiplier(weight) - 1))
    
    print(f"opcenten base: {base}")
    return base * (OPCENTEN[province][year] / 100)

def calc_fuel_tax(energy_source: EnergySource, weight: int) -> float:
    """Calculate extra fuel tax
    Only for Diesel, LPG and other fuel types not Benzine.
    Will also count for electric cars from 2026

    Args:
        energy_source (EnergySource): Energy source that primarily powers the vehicle
        weight (int): Rounded weight of vehicle

    Returns:
        float: Amount of tax added
    """

    if energy_source == EnergySource.DIESEL:
        tax = 0.0
        if weight <= 500: 
            tax = 73.75
        if weight <= 600:
            tax = 87.02
        if weight <= 700: 
            tax = 100.51
        if weight <= 800: 
            tax = 114.25
        # From here excess weight is calculated per 100kg
        if weight >= 900:
            tax = 133.69 + (14.48 * (calc_multiplier(weight) - 1))

        return fijnstof_tax(tax)


    elif energy_source == EnergySource.LPG_G3:
        if weight <= 800: return 0.0
        # From here excess weight is calculated per 100kg
        else:
            return 16.64 + abs((16.64 * calc_multiplier(weight)))
    
    elif energy_source == EnergySource.OVERIGE:
        if weight <= 500: return 86.25
        if weight <= 600: return 103.39
        if weight <= 700: return 120.54
        if weight <= 800: return 137.65
        # From here excess weight is calculated per 100kg
        if weight >= 900:
            return 150.36 + (15.92 * calc_multiplier(weight))

    else:
        return 0.0

def fijnstof_tax(tax: float) -> float:
    """Extra tax added for small particule matters in diesel

    Args:
        tax (float): Tax rate before this surcharge

    Returns:
        float: Tax amount after surcharge, rounded to 2 decimals
    """
    return round(tax * 1.19, 2)


def tax_reduction_co2(tax: float, co2_level: int) -> float:
    """Calculate reduction in taxes if co2 levels are low enough
    Only for Diesel engines
    source: https://wetten.overheid.nl/BWBR0006324/2023-01-01/#HoofdstukIV_Afdeling2_Artikel23b

    Returns:
        float: Amount of tax
    """
    if co2_level == 0:
        tax = 0.0
    elif co2_level <= 50:
        tax = round(tax / 2, 2)

    return tax


def calculate_tax(energy_source: EnergySource, weight: int, province: str, year: int) -> int:
    """Run through all tax calculations for a vehicle

    Args:
        energy_source (EnergySource): Energy source that primarily powers the vehicle
        weight (int): Rounded weight of vehicle
        province (str): Name of the province
        year (int): Year of calculation

    Returns:
        int: Total tax amount, with decimals dropped
    """
    rounded_weight = 100 * round(weight/100)

    if energy_source == EnergySource.ELEKTRICITEIT:
        if year < 2025:
            return 0.0
        elif year == 2025:
            return round(vehicle_tax(rounded_weight) * 0.25)
        elif year >= 2026 and year <= 2029:
            return round(vehicle_tax(rounded_weight) * 0.75)
        else:
            return vehicle_tax(rounded_weight)

    base_tax = vehicle_tax(rounded_weight)
    if year in INFLATION:
        base_tax = round(base_tax * (1 + INFLATION[year]))

    print(f"mrb :           {base_tax}")
    fuel_tax = calc_fuel_tax(energy_source, rounded_weight)
    print(f"toeslag :       {fuel_tax}")
    opcenten = calc_opcenten(rounded_weight, province, year)
    print(f"opcenten :      {opcenten}")

    
    return int(base_tax + fuel_tax + opcenten)
