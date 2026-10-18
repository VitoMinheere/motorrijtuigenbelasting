import datetime
import unittest

from motorrijtuigenbelasting import Car, EnergySource, Motorcycle
from motorrijtuigenbelasting.rdw import (
    ADDED_OBJECTS_URL,
    FUELS_URL,
    VEHICLES_URL,
    energy_source,
    from_kenteken,
    lookup,
)

# Shortened responses of the RDW open data, P803KL is a real plug-in hybrid
RESPONSES = {
    (VEHICLES_URL, "P803KL"): [
        {
            "kenteken": "P803KL",
            "voertuigsoort": "Personenauto",
            "inrichting": "stationwagen",
            "massa_ledig_voertuig": "1578",
            "massa_rijklaar": "1678",
            "datum_eerste_toelating": "20201214",
        }
    ],
    (FUELS_URL, "P803KL"): [
        {
            "kenteken": "P803KL",
            "brandstof_volgnummer": "1",
            "brandstof_omschrijving": "Benzine",
            "co2_uitstoot_gewogen": "31.00000",
            "emis_co2_gewogen_gecombineerd_wltp": "35",
        },
        {
            "kenteken": "P803KL",
            "brandstof_volgnummer": "2",
            "brandstof_omschrijving": "Elektriciteit",
        },
    ],
    (VEHICLES_URL, "11ABC1"): [
        {
            "kenteken": "11ABC1",
            "voertuigsoort": "Personenauto",
            "inrichting": "hatchback",
            "massa_rijklaar": "820",
            "datum_eerste_toelating": "20150301",
        }
    ],
    (FUELS_URL, "11ABC1"): [
        {
            "kenteken": "11ABC1",
            "brandstof_omschrijving": "Diesel",
            "uitstoot_deeltjes_licht": "0.00600",
        }
    ],
    (VEHICLES_URL, "MZ12AB"): [
        {
            "kenteken": "MZ12AB",
            "voertuigsoort": "Motorfiets",
            "massa_rijklaar": "220",
            "datum_eerste_toelating": "19870601",
        }
    ],
    (FUELS_URL, "MZ12AB"): [
        {"kenteken": "MZ12AB", "brandstof_omschrijving": "Benzine"}
    ],
    (VEHICLES_URL, "GG111G"): [
        {
            "kenteken": "GG111G",
            "voertuigsoort": "Personenauto",
            "massa_rijklaar": "1300",
            "datum_eerste_toelating": "20100101",
        }
    ],
    (FUELS_URL, "GG111G"): [
        {"kenteken": "GG111G", "brandstof_omschrijving": "Benzine"},
        {"kenteken": "GG111G", "brandstof_omschrijving": "LPG"},
    ],
    (ADDED_OBJECTS_URL, "GG111G"): [
        {
            "kenteken": "GG111G",
            "demontagedatum": "0",
            "soort_toe_te_voegen_object_omschrijving": "LPG Installatie",
            "classificatie_toegevoegd_obj": "G3",
        }
    ],
    (VEHICLES_URL, "GG222G"): [
        {
            "kenteken": "GG222G",
            "voertuigsoort": "Personenauto",
            "massa_rijklaar": "1300",
            "datum_eerste_toelating": "20100101",
        }
    ],
    (FUELS_URL, "GG222G"): [
        {"kenteken": "GG222G", "brandstof_omschrijving": "Benzine"},
        {"kenteken": "GG222G", "brandstof_omschrijving": "LPG"},
    ],
    (ADDED_OBJECTS_URL, "GG222G"): [
        {
            "kenteken": "GG222G",
            "demontagedatum": "0",
            "soort_toe_te_voegen_object_omschrijving": "LPG Installatie",
            "classificatie_toegevoegd_obj": "G2",
        }
    ],
    (VEHICLES_URL, "VB123B"): [
        {
            "kenteken": "VB123B",
            "voertuigsoort": "Bedrijfsauto",
            "massa_rijklaar": "1900",
            "datum_eerste_toelating": "20190101",
        }
    ],
    (FUELS_URL, "VB123B"): [{"kenteken": "VB123B", "brandstof_omschrijving": "Diesel"}],
}


def fake_fetch(url: str, params: dict) -> list:
    return RESPONSES.get((url, params["kenteken"]), [])


class TestLookup(unittest.TestCase):
    def test_plug_in_hybrid(self):
        vehicle = lookup("p-803-kl", fetch=fake_fetch)
        self.assertEqual(vehicle.kenteken, "P803KL")
        self.assertEqual(vehicle.first_admission, datetime.date(2020, 12, 14))
        self.assertEqual(vehicle.energy_source, EnergySource.BENZINE)
        # Admitted before 2021, so the NEDC value is used (art. 23b lid 3)
        self.assertEqual(vehicle.co2_emission, 31.0)
        self.assertTrue(vehicle.low_co2)

        car = vehicle.to_vehicle()
        self.assertIsInstance(car, Car)
        self.assertEqual(car.rounded_weight, 1600)
        self.assertTrue(car.low_co2_emissions)

    def test_diesel_with_particles(self):
        car = from_kenteken("11-ABC-1", fetch=fake_fetch)
        self.assertEqual(car.energy_source, EnergySource.DIESEL)
        # 0.006 g/km is above the Euro 5 limit of 5 mg/km
        self.assertTrue(car.diesel_particles)
        same = Car(weight=820, energy_source=EnergySource.DIESEL, diesel_particles=True)
        self.assertEqual(
            car.calculate_total_tax(year=2026, province="utrecht"),
            same.calculate_total_tax(year=2026, province="utrecht"),
        )

    def test_motorcycle(self):
        motor = from_kenteken("MZ-12-AB", fetch=fake_fetch)
        self.assertIsInstance(motor, Motorcycle)
        self.assertTrue(motor.is_kwarttarief(2026))

    def test_lpg_g3_installation(self):
        """Art. 23 lid 3: G3 installations pay the lower surcharge"""
        self.assertEqual(
            from_kenteken("GG-111-G", fetch=fake_fetch).energy_source,
            EnergySource.LPG_G3,
        )
        self.assertEqual(
            from_kenteken("GG-222-G", fetch=fake_fetch).energy_source,
            EnergySource.LPG,
        )

    def test_energy_source_override(self):
        car = from_kenteken(
            "GG-222-G", fetch=fake_fetch, energy_source=EnergySource.LPG_G3
        )
        self.assertEqual(car.energy_source, EnergySource.LPG_G3)

    def test_added_objects_only_fetched_for_lpg(self):
        urls = []

        def recording_fetch(url, params):
            urls.append(url)
            return fake_fetch(url, params)

        from_kenteken("P-803-KL", fetch=recording_fetch)
        self.assertNotIn(ADDED_OBJECTS_URL, urls)

    def test_unsupported_vehicle_type(self):
        with self.assertRaises(NotImplementedError):
            from_kenteken("VB-123-B", fetch=fake_fetch)

    def test_unknown_kenteken(self):
        with self.assertRaisesRegex(ValueError, "not found"):
            lookup("XX-999-X", fetch=fake_fetch)


class TestEnergySource(unittest.TestCase):
    def test_mapping(self):
        cases = {
            frozenset({"Benzine"}): EnergySource.BENZINE,
            frozenset({"Benzine", "Elektriciteit"}): EnergySource.BENZINE,
            frozenset({"Elektriciteit"}): EnergySource.ELEKTRICITEIT,
            frozenset({"Waterstof", "Elektriciteit"}): EnergySource.WATERSTOF,
            frozenset({"Diesel", "Elektriciteit"}): EnergySource.DIESEL,
            frozenset({"Benzine", "LPG"}): EnergySource.LPG,
            frozenset({"Benzine", "CNG"}): EnergySource.LPG_G3,
            frozenset({"Alcohol"}): EnergySource.OVERIGE,
        }
        for fuels, expected in cases.items():
            with self.subTest(fuels=sorted(fuels)):
                self.assertEqual(energy_source(set(fuels)), expected)
