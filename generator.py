import json
from collections import defaultdict

from taxes import EnergySource, calculate_tax

YEARS = range(2015, 2025)

FUEL_TYPE = EnergySource.BENZINE
CAR_WEIGHTS = range(500, 3300, 100)
PROVINCES = [
    "drenthe",
    "flevoland",
    "friesland", 
    "gelderland", 
    "groningen", 
    "limburg",
    "noord-brabant", 
    "noord-holland", 
    "overijssel",
    "utrecht", 
    "zeeland", 
    "zuid-holland"
    ]

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

results = AutoVivification()
    # {
    # "drenthe": {
    #     500: {
    #         2023: 0
    #         }
    #     }
    # }
    # )

for province in PROVINCES:
    for weight_class in CAR_WEIGHTS:
        for year in YEARS:
            tax = calculate_tax(
                FUEL_TYPE,
                weight_class,
                province,
                year
            )
            results[province][str(weight_class)][str(year)] = tax

with open('output/benzine.json', 'w') as convert_file: 
     convert_file.write(json.dumps(results))