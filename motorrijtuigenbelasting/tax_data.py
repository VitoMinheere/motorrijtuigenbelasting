"""Year-dependent rates from data/tax_data.json and helpers to read them.

Amounts that are fixed by law live in vehicles/constants.py.
"""

import json
import math
from pathlib import Path

with open(Path(__file__).parent / "data" / "tax_data.json", encoding="utf-8") as f:
    TAX_DATA = json.load(f)

SUPPORTED_YEARS = sorted(int(year) for year in TAX_DATA)
PROVINCES = sorted(TAX_DATA[str(SUPPORTED_YEARS[-1])]["opcenten"])

PER_100KG_PREFIX = "per_100kg_above_"


def _year_data(year: int) -> dict:
    try:
        return TAX_DATA[str(year)]
    except KeyError:
        raise KeyError(
            f"No tax data for {year}, supported years are {SUPPORTED_YEARS}"
        ) from None


def get_tax_value(year: int, category: str, key: str):
    return _year_data(year)[category][key]


def opcenten_percentage(year: int, province: str) -> float:
    """Opcenten percentage of a province, e.g. "Noord-Holland" or "noord-holland"."""
    key = province.strip().lower().replace(" ", "-")
    try:
        return _year_data(year)["opcenten"][key]
    except KeyError:
        raise KeyError(
            f"Unknown province {province!r}, expected one of {PROVINCES}"
        ) from None


def round_down(amount: float) -> int:
    """Round down to whole euros, after rounding to cents so 35.9999... counts as 36."""
    return math.floor(round(amount, 2))


def round_weight(weight: float) -> int:
    """Wet MRB 1994 art. 22 lid 1b: round to the nearest 100 kg, exactly 50 kg rounds down."""
    return 100 * math.ceil((weight - 50) / 100)


def steps_above(weight: int, cut_off: int, step: int = 100) -> int:
    """Amount of whole steps the weight is above the cut off, 0 when at or below it."""
    return max(weight - cut_off, 0) // step


def rate_for_weight(table: dict, weight: int) -> float:
    """Look up the rate for a rounded weight in a weight table from the law.

    Tables have fixed amounts per weight (e.g. "500": up to and including 500 kg).
    A "per_100kg_above_X" key means the amount at X kg is increased by that rate for
    every 100 kg above X. The highest applicable X is used, e.g. 900 or 3300.
    """
    cut_offs = [
        int(key.removeprefix(PER_100KG_PREFIX))
        for key in table
        if key.startswith(PER_100KG_PREFIX)
    ]
    for cut_off in sorted(cut_offs, reverse=True):
        if weight >= cut_off:
            return table[str(cut_off)] + table[
                f"{PER_100KG_PREFIX}{cut_off}"
            ] * steps_above(weight, cut_off)
    return table[str(max(weight, 500))]
