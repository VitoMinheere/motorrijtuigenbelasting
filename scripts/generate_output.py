"""Write the tax per three months for every province, weight and supported year to JSON.

Usage: python scripts/generate_output.py [energy_source] [output_file]
e.g.   python scripts/generate_output.py benzine output/benzine.json
"""

import json
import sys
from pathlib import Path

from motorrijtuigenbelasting import PROVINCES, SUPPORTED_YEARS, Car, EnergySource

# Massa rijklaar
CAR_WEIGHTS = range(600, 3400, 100)


def generate(energy_source: EnergySource) -> dict:
    return {
        province: {
            str(weight): {
                str(year): Car(weight, energy_source).calculate_total_tax(
                    year=year, province=province
                )
                for year in SUPPORTED_YEARS
            }
            for weight in CAR_WEIGHTS
        }
        for province in PROVINCES
    }


if __name__ == "__main__":
    energy_source = EnergySource(sys.argv[1] if len(sys.argv) > 1 else "benzine")
    output = Path(
        sys.argv[2] if len(sys.argv) > 2 else f"output/{energy_source.value}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(generate(energy_source), indent=4))
