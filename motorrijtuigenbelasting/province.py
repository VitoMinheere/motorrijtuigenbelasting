from enum import Enum


class Province(str, Enum):
    """The twelve provinces, for autocomplete. Plain strings like "Noord-Holland" work too."""

    DRENTHE = "drenthe"
    FLEVOLAND = "flevoland"
    FRIESLAND = "friesland"
    GELDERLAND = "gelderland"
    GRONINGEN = "groningen"
    LIMBURG = "limburg"
    NOORD_BRABANT = "noord-brabant"
    NOORD_HOLLAND = "noord-holland"
    OVERIJSSEL = "overijssel"
    UTRECHT = "utrecht"
    ZEELAND = "zeeland"
    ZUID_HOLLAND = "zuid-holland"
