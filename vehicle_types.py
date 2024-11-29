from abc import ABC, abstractmethod
from enum import Enum

import datetime

class EnergySource(Enum):
    BENZINE = "Benzine"
    DIESEL = "Diesel"
    LPG = "LPG"
    LPG_G3 = "LPG G3"
    ELEKTRICITEIT = "Elektrisch"
    OVERIGE = "Overige"


class Vehicle(Enum):
    PERSONEN_AUTO = "Personen auto"


class VehicleTaxClass(Enum):
    VOLLEDIG = "Volledig"
    # From 1987 until 40 years old
    KWART_TARIEF = "Kwart tarief"
    # After 40 years
    OLDTIMER = "Oldtimer"

class Vehicle(ABC):
    def __init__(self, weight: int, energy_source: EnergySource, 
                 manufacturing_year: int = None):
        self.weight = weight
        self.energy_source = energy_source
        self.manufacturing_year = manufacturing_year

    def set_calculation_year(self, year: int):
        self.calculation_year = year

    @abstractmethod
    def calculate_base_tax(self, year: int) -> float:
        """Abstract method to calculate base tax."""
        pass

    @abstractmethod
    def calculate_total_tax(self, year: int, province: str) -> float:
        """Abstract method to calculate the total tax, optionally using province."""
        pass

    def is_historic(self) -> bool:
        """Oldtimer ruling applies when vehicle is registered 40 years ago"""
        oldtimer_deadline = datetime.date.today().year - 40
        if self.manufacturing_year:
            return self.manufacturing_year <= oldtimer_deadline
        return False

    def apply_historic_tax_discount(self, tax: float) -> float:
        return 0 if self.is_historic() else tax

    def is_youngtimer(self) -> bool:
        """kwarttarief ruling applies when a vehicle is registered before 1988 up until it is 40 years old"""
        if self.manufacturing_year:
            return self.manufacturing_year < 1988
        return False

    def apply_youngtimer_discount(self, tax: float) -> float:
        return tax * 0.25 if self.is_youngtimer() else tax

    def is_electric(self) -> bool:
        return self.energy_source == EnergySource.ELEKTRICITEIT

    def apply_electric_tax_discount(self, tax: float) -> float:
        if self.is_electric():
            if self.calculation_year < 2025:
                return 0  # No tax for electric cars before 2025
            elif self.calculation_year == 2025:
                tax *= 0.25  # 25% of base tax
            elif 2026 <= self.calculation_year <= 2029:
                tax *= 0.75  # 75% of base tax

        return tax

class Car(Vehicle):
    def __init__(self, co2_emissions: int = None):
        self.co2_emissions = co2_emissions
        super.__init__


            




"""
Oldtimer rules:

kwart tarief: 27 to 40 years old. Only for benzine cars, not others. Max 120 euro per year
"""
