from enum import Enum


class EnergySource(Enum):
    """Fuel type as registered with the RDW.

    Every member has its own value, so EnergySource.LPG and EnergySource.OVERIGE are
    different members even though cars using them pay the same brandstoftoeslag.
    """

    BENZINE = "benzine"
    DIESEL = "diesel"
    LPG = "lpg"
    LPG_G3 = "lpg_g3"
    ELEKTRICITEIT = "elektriciteit"
    OVERIGE = "overige"
