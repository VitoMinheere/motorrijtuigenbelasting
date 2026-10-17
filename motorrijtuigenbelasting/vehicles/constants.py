"""Amounts that are fixed by law and do not change per year.

Year-dependent rates live in data/tax_data.json.
"""

# Provincial opcenten are calculated over a fixed tariff (the motorrijtuigenbelasting
# tariff of 1 April 1995), not over the current tariff.
# Source: Provinciewet art. 222 lid 3. Since 1 July 2026 the law states this table in massa
# rijklaar, which is eigen massa + 100 kg; the weights below are in eigen massa.
OPCENTEN_BASE = {
    "500": 14.50,
    "600": 17.33,
    "700": 20.40,
    "800": 26.98,
    "900": 34.12,
    "1000": 45.81,
    "per_100kg_above_1000": 11.68,
}

# 1995 motorcycle tariff, corrected with the 2007 change (Provinciewet art. 222 lid 3a)
# Source: https://zoek.officielebekendmakingen.nl/blg-1106771.pdf
MOTORCYCLE_OPCENTEN_BASE = 7.80

# The RDW sets massa rijklaar at eigen massa + 100 kg. Since 1 July 2026 the law uses massa
# rijklaar, before that eigen massa. The weight tables in this package are in eigen massa.
MASSA_RIJKLAAR_OFFSET = 100
