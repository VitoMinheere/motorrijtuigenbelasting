"""Compare the opcenten in tax_data.json with CBS StatLine table 80889ned.

Usage: python scripts/check_opcenten.py
Exits with status 1 when a value differs or is missing at CBS.
"""

import functools
import json
import sys
import urllib.request

from motorrijtuigenbelasting.tax_data import TAX_DATA

CBS_URL = "https://opendata.cbs.nl/ODataApi/odata/80889ned/{}"
# CBS uses the Frisian name
CBS_NAMES = {"fryslân": "friesland"}


def fetch(resource: str) -> list:
    request = urllib.request.Request(
        CBS_URL.format(resource), headers={"User-Agent": "motorrijtuigenbelasting"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["value"]


def province_key(title: str) -> str:
    name = title.replace("(PV)", "").strip().lower().replace(" ", "-")
    return CBS_NAMES.get(name, name)


@functools.cache
def cbs_opcenten() -> dict:
    regions = {row["Key"]: row["Title"] for row in fetch("RegioS")}
    opcenten = {}
    for row in fetch("TypedDataSet"):
        year = row["Perioden"][:4]
        province = province_key(regions[row["RegioS"]])
        opcenten.setdefault(year, {})[province] = row[
            "TariefOpcentenMotorrijtuigenbelasting_1"
        ]
    return opcenten


def main() -> int:
    cbs = cbs_opcenten()
    differences = 0
    for year, data in TAX_DATA.items():
        for province, value in data["opcenten"].items():
            expected = cbs.get(year, {}).get(province)
            if expected != value:
                differences += 1
                print(f"{year} {province}: tax_data.json {value}, CBS {expected}")
    print(f"{differences} differences")
    return 1 if differences else 0


if __name__ == "__main__":
    sys.exit(main())
