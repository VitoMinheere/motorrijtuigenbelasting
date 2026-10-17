"""Add or check a year in tax_data.json, from the law text and the CBS opcenten.

Usage:
    python scripts/add_year.py 2027            # print the parsed year
    python scripts/add_year.py 2027 --write    # add it to tax_data.json
    python scripts/add_year.py --check 2026    # compare a year already in the file

Tariffs come from the version of the Wet MRB 1994 that applies on 1 January of the
year (https://wetten.overheid.nl/BWBR0006324/<year>-01-01): art. 23, 23b, 25, 31 and
84a. Opcenten come from CBS StatLine table 80889ned. Always review the result and
run the tests, the law text can change its wording.
"""

import argparse
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_opcenten import cbs_opcenten

TAX_DATA_PATH = (
    Path(__file__).parent.parent / "motorrijtuigenbelasting" / "data" / "tax_data.json"
)
LAW_URL = "https://wetten.overheid.nl/BWBR0006324/{year}-01-01"

AMOUNT = r"(\d{1,3}(?:\.\d{3})*,\d{2})"
SMALL = ["500", "600", "700", "800", "900", "per_100kg_above_900"]
BASE = SMALL + ["3300", "per_100kg_above_3300"]
FRACTIONS = {"nihil": 0.0, "een kwart": 0.25, "de helft": 0.5, "driekwart": 0.75}


def law_text(year: int) -> str:
    request = urllib.request.Request(
        LAW_URL.format(year=year), headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        text = response.read().decode("utf-8")
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.DOTALL)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return re.sub(r"\s+", " ", text)


def article(text: str, number: str) -> str:
    """The longest match, which skips the table of contents."""
    best = ""
    for match in re.finditer(rf"Artikel {re.escape(number)} ", text):
        rest = text[match.start() + 12 :]
        end = re.search(r"Artikel \d+[a-z]* ", rest)
        body = text[match.start() : match.start() + 12 + (end.start() if end else 4000)]
        if len(body) > len(best):
            best = body
    if not best:
        raise ValueError(f"Artikel {number} not found")
    return best


def amounts(text: str) -> list[float]:
    return [
        float(a.replace(".", "").replace(",", ".")) for a in re.findall(AMOUNT, text)
    ]


def between(text: str, start: str, end: str) -> str:
    i = text.index(start)
    return text[i : text.index(end, i + len(start))]


def table(values: list[float], keys: list[str]) -> dict:
    if len(values) != len(keys):
        raise ValueError(f"Expected {len(keys)} amounts, found {values}")
    return dict(zip(keys, values))


def fraction(text: str) -> float:
    for word, value in FRACTIONS.items():
        if text.strip().startswith(word):
            return value
    raise ValueError(f"Unknown fraction: {text[:80]!r}")


def emission_factors(a23b: str, year: int) -> tuple[float, float]:
    """Zero and low (at most 50 g/km) emission factors for personenauto's."""
    percentage = re.search(rf"voor het jaar {year}: (\d+)%", a23b)
    if percentage:
        # Since 2026 only zero emission has a discount
        return int(percentage.group(1)) / 100, 1.0
    zero = re.search(r"CO 2 -uitstoot van 0 gram per kilometer: ([^,;.]+)", a23b)
    low = re.search(r"niet meer dan 50 gram per kilometer: ([^,;.]+)", a23b)
    if zero and low:
        return fraction(zero.group(1)), fraction(low.group(1))
    # Up to 2015: "niet hoger is dan 50 gram per kilometer ... nihil" for both
    if re.search(r"niet hoger is dan 50 gram per kilometer.*nihil", a23b):
        return 0.0, 0.0
    raise ValueError("Could not read art. 23b")


def motorcycle_zero_emission_factor(text: str) -> float:
    """Art. 31 gave the zero emission discount for motorcycles until 2025."""
    try:
        a31 = article(text, "31")
    except ValueError:
        return 1.0
    if "Vervallen" in a31[:300]:
        return 1.0
    match = re.search(
        r"bedraagt de belasting (nihil|een kwart|de helft|driekwart)", a31
    )
    if not match:
        raise ValueError("Could not read art. 31")
    return fraction(match.group(1))


def parse_year(year: int) -> dict:
    text = law_text(year)
    a23 = article(text, "23")
    lid1 = between(a23, " 1 Voor een personenauto", " 2 De belasting")
    lid3 = a23[a23.index(" 3 In afwijking") :]
    lid3 = lid3[: lid3.index("is opgenomen")]
    fijnstof = re.search(r"fijnstoftoeslag van (\d+) percent", a23)
    zero, low = emission_factors(article(text, "23b"), year)
    maximum = re.search(r"ten hoogste\s*\S\s*(\d+(?:,\d{2})?)", article(text, "84a"))
    if not maximum:
        raise ValueError("Could not read the kwarttarief maximum in art. 84a")
    kwarttarief = float(maximum.group(1).replace(",", "."))
    opcenten = cbs_opcenten().get(str(year))
    if not opcenten:
        raise ValueError(f"CBS has no opcenten for {year} yet")

    return {
        "car": {
            "base": table(amounts(lid1), BASE),
            "fuel_surcharge": {
                "diesel": table(amounts(between(a23, " a. ", " b. ")), SMALL),
                "overige": table(
                    amounts(between(a23, " b. ", " 3 In afwijking")), SMALL
                ),
                "lpg_g3": table([0, 0, 0, 0, *amounts(lid3)], SMALL),
            },
            "zero_emission_factor": zero,
            "low_emission_factor": low,
            "fijnstoftoeslag": int(fijnstof.group(1)) / 100 if fijnstof else 0.0,
        },
        "motorcycle": {
            "value": amounts(article(text, "25"))[0],
            "zero_emission_factor": motorcycle_zero_emission_factor(text),
        },
        "kwarttarief": {
            "value": int(kwarttarief) if kwarttarief.is_integer() else kwarttarief
        },
        "opcenten": {province: opcenten[province] for province in sorted(opcenten)},
    }


def inline(values: dict) -> str:
    return "{" + ", ".join(f'"{k}": {json.dumps(v)}' for k, v in values.items()) + "}"


def dump_year(data: dict) -> str:
    car, motorcycle = data["car"], data["motorcycle"]
    fuel = ",\n".join(
        f'                "{name}": {inline(values)}'
        for name, values in car["fuel_surcharge"].items()
    )
    opcenten = ",\n".join(
        f'            "{p}": {json.dumps(v)}' for p, v in data["opcenten"].items()
    )
    return f"""{{
        "car": {{
            "base": {inline(car["base"])},
            "fuel_surcharge": {{
{fuel}
            }},
            "zero_emission_factor": {json.dumps(car["zero_emission_factor"])},
            "low_emission_factor": {json.dumps(car["low_emission_factor"])},
            "fijnstoftoeslag": {json.dumps(car["fijnstoftoeslag"])}
        }},
        "motorcycle": {{
            "value": {json.dumps(motorcycle["value"])},
            "zero_emission_factor": {json.dumps(motorcycle["zero_emission_factor"])}
        }},
        "kwarttarief": {{
            "value": {json.dumps(data["kwarttarief"]["value"])}
        }},
        "opcenten": {{
{opcenten}
        }}
    }}"""


def dump(tax_data: dict) -> str:
    years = ",\n".join(f'    "{y}": {dump_year(tax_data[y])}' for y in sorted(tax_data))
    return "{\n" + years + "\n}\n"


def differences(expected, actual, path="") -> list[str]:
    if isinstance(expected, dict):
        found = []
        for key in expected.keys() | actual.keys():
            if key not in expected or key not in actual:
                found.append(f"{path}/{key}: only in one of them")
            else:
                found += differences(expected[key], actual[key], f"{path}/{key}")
        return found
    return [] if expected == actual else [f"{path}: file {expected}, law {actual}"]


def main() -> int:
    arguments = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    arguments.add_argument("years", type=int, nargs="+")
    arguments.add_argument("--write", action="store_true", help="update tax_data.json")
    arguments.add_argument("--check", action="store_true", help="compare with the file")
    args = arguments.parse_args()

    tax_data = json.loads(TAX_DATA_PATH.read_text(encoding="utf-8"))
    found = 0
    for year in args.years:
        parsed = parse_year(year)
        if args.check:
            year_differences = differences(tax_data[str(year)], parsed)
            found += len(year_differences)
            print(f"{year}: {len(year_differences)} differences")
            for difference in sorted(year_differences):
                print(f"  {difference}")
        elif args.write:
            tax_data[str(year)] = parsed
        else:
            print(json.dumps({str(year): parsed}, indent=4))

    if args.write:
        TAX_DATA_PATH.write_text(dump(tax_data), encoding="utf-8", newline="\n")
        print(f"Wrote {', '.join(map(str, args.years))} to {TAX_DATA_PATH}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
