from enum import Enum


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


"""
Oldtimer rules:

kwart tarief: 27 to 40 years old. Only for benzine cars, not others. Max 120 euro per year
"""
