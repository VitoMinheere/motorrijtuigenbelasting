# constants.py
from typing import Dict, List, Tuple

INFLATION = {
    2015: 0.009,
    2016: 0.005,
    2017: 0.003,
    2018: 0.008,
    2019: 0.012,
    2020: 0.016,
    2021: 0.016,
    2022: 0.013,
    2023: 0.063,
    2024: 0.099
}

# Define weight tax brackets per energy source
WEIGHT_TAX_BRACKETS: Dict[str, List[Tuple[int, float]]] = {
    "benzine": [  # Used for most sources
        (500, 18.75),
        (600, 25.44),
        (700, 32.33),
        (800, 42.20),
        (900, 56.13),
    ],
    "overige": [  # For EnergySource.OVERIGE
        (500, 20.00),
        (600, 27.50),
        (700, 35.00),
        (800, 45.00),
        (900, 60.00),
    ],
    "diesel": [  # For EnergySource.DIESEL
        (500, 22.50),
        (600, 30.00),
        (700, 37.50),
        (800, 47.50),
        (900, 62.50),
    ],
}

OPCENTEN_BRACKETS: Dict = {

}

EXCESS_RATES: Dict[str, float] = {
    "benzine": 15.09,
    "overige": 16.50,
    "diesel": 18.00,
}
