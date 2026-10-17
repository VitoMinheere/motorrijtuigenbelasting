"""Look up vehicle details by kenteken in the RDW open data.

Uses the public datasets "Gekentekende voertuigen" (m9d7-ebf2) and
"Gekentekende voertuigen brandstof" (8ys7-d773). No API key is needed.
"""

import datetime
import json
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass

from .vehicles.base import Vehicle
from .vehicles.car import Car
from .vehicles.energy_source import EnergySource
from .vehicles.motorcycle import Motorcycle

VEHICLES_URL = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"
FUELS_URL = "https://opendata.rdw.nl/resource/8ys7-d773.json"

# Wet MRB 1994 art. 23 lid 4: fijnstoftoeslag above 5 mg/km (light) or 10 mg/kWh (heavy)
PARTICLE_LIMIT_MG_PER_KM = 5
PARTICLE_LIMIT_MG_PER_KWH = 10
# Art. 23b: low emission discount for more than 0 and at most 50 g/km
LOW_CO2_LIMIT = 50

# CO2 fields in order of preference, weighted values are the ones for plug-in hybrids.
# Art. 23b lid 3: cars first admitted before 2021 use the NEDC values (the BPM rules
# of 30 June 2020), later cars the WLTP values.
WLTP_FROM = datetime.date(2021, 1, 1)
NEDC_CO2_FIELDS = ("co2_uitstoot_gewogen", "co2_uitstoot_gecombineerd")
WLTP_CO2_FIELDS = (
    "emis_co2_gewogen_gecombineerd_wltp",
    "emissie_co2_gecombineerd_wltp",
)

Fetch = Callable[[str, dict], list]


def fetch_json(url: str, params: dict) -> list:
    request = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(params)}",
        headers={"User-Agent": "motorrijtuigenbelasting"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def normalise_kenteken(kenteken: str) -> str:
    return "".join(c for c in kenteken if c.isalnum()).upper()


def energy_source(fuels: set[str]) -> EnergySource:
    """Map the RDW fuel descriptions of a vehicle to an EnergySource.

    An electric motor next to a combustion engine is ignored (art. 23 lid 2, last
    sentence), so a benzine plug-in hybrid counts as benzine.
    """
    if fuels == {"Elektriciteit"}:
        return EnergySource.ELEKTRICITEIT
    if "Waterstof" in fuels and fuels <= {"Waterstof", "Elektriciteit"}:
        return EnergySource.WATERSTOF
    if "Diesel" in fuels:
        return EnergySource.DIESEL
    # Art. 23 lid 3: CNG and LNG pay the same surcharge as LPG with a G3 installation
    if fuels & {"CNG", "LNG"}:
        return EnergySource.LPG_G3
    # The open data does not say whether an LPG installation is G3, so assume it is not
    if "LPG" in fuels:
        return EnergySource.LPG
    if fuels <= {"Benzine", "Elektriciteit"}:
        return EnergySource.BENZINE
    return EnergySource.OVERIGE


def _number(record: dict, field: str) -> float | None:
    value = record.get(field)
    return float(value) if value not in (None, "") else None


def co2_emission(
    fuel_records: list[dict], first_admission: datetime.date
) -> float | None:
    if first_admission < WLTP_FROM:
        fields = NEDC_CO2_FIELDS + WLTP_CO2_FIELDS
    else:
        fields = WLTP_CO2_FIELDS + NEDC_CO2_FIELDS
    for field in fields:
        for record in fuel_records:
            value = _number(record, field)
            if value is not None:
                return value
    return None


def has_diesel_particles(fuel_records: list[dict]) -> bool:
    """Art. 23 lid 4 and 5: above the Euro 5 limit, or presumed above it when no
    particle emission is registered."""
    for record in fuel_records:
        if record.get("brandstof_omschrijving") != "Diesel":
            continue
        light = _number(record, "uitstoot_deeltjes_licht")  # g/km
        if light is not None:
            return light * 1000 > PARTICLE_LIMIT_MG_PER_KM
        wltp = _number(record, "emis_deeltjes_type1_wltp")  # mg/km
        if wltp is not None:
            return wltp > PARTICLE_LIMIT_MG_PER_KM
        heavy = _number(record, "uitstoot_deeltjes_zwaar")  # g/kWh
        if heavy is not None:
            return heavy * 1000 > PARTICLE_LIMIT_MG_PER_KWH
        return True
    return False


@dataclass(frozen=True)
class RdwVehicle:
    """The details of a registered vehicle that matter for the tax."""

    kenteken: str
    voertuigsoort: str
    inrichting: str | None
    massa_rijklaar: int | None
    first_admission: datetime.date
    fuels: frozenset[str]
    co2_emission: float | None
    diesel_particles: bool

    @property
    def energy_source(self) -> EnergySource:
        return energy_source(set(self.fuels))

    @property
    def low_co2(self) -> bool:
        return self.co2_emission is not None and 0 < self.co2_emission <= LOW_CO2_LIMIT

    def to_vehicle(self) -> Vehicle:
        if self.voertuigsoort == "Personenauto":
            if self.inrichting == "kampeerwagen":
                raise NotImplementedError("Kampeerauto's are not supported yet")
            if self.massa_rijklaar is None:
                raise ValueError(f"No massa rijklaar registered for {self.kenteken}")
            return Car(
                weight=self.massa_rijklaar,
                energy_source=self.energy_source,
                manufacturing_year=self.first_admission,
                co2_emissions=self.low_co2,
                diesel_particles=self.diesel_particles,
            )
        if self.voertuigsoort == "Motorfiets":
            return Motorcycle(
                weight=self.massa_rijklaar or 0,
                energy_source=self.energy_source,
                manufacturing_year=self.first_admission,
            )
        raise NotImplementedError(f"{self.voertuigsoort} is not supported yet")


def lookup(kenteken: str, fetch: Fetch = fetch_json) -> RdwVehicle:
    """Fetch the details of a kenteken from the RDW open data."""
    kenteken = normalise_kenteken(kenteken)
    vehicles = fetch(VEHICLES_URL, {"kenteken": kenteken})
    if not vehicles:
        raise ValueError(f"Kenteken {kenteken} not found in the RDW open data")
    vehicle = vehicles[0]
    fuel_records = fetch(FUELS_URL, {"kenteken": kenteken})
    massa_rijklaar = _number(vehicle, "massa_rijklaar")
    first_admission = datetime.datetime.strptime(
        vehicle["datum_eerste_toelating"], "%Y%m%d"
    ).date()
    return RdwVehicle(
        kenteken=kenteken,
        voertuigsoort=vehicle.get("voertuigsoort", ""),
        inrichting=vehicle.get("inrichting"),
        massa_rijklaar=int(massa_rijklaar) if massa_rijklaar is not None else None,
        first_admission=first_admission,
        fuels=frozenset(r["brandstof_omschrijving"] for r in fuel_records),
        co2_emission=co2_emission(fuel_records, first_admission),
        diesel_particles=has_diesel_particles(fuel_records),
    )


def from_kenteken(kenteken: str, fetch: Fetch = fetch_json) -> Vehicle:
    """A Car or Motorcycle with the details of a kenteken from the RDW open data."""
    return lookup(kenteken, fetch).to_vehicle()
