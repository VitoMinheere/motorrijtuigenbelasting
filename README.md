# Motorrijtuigenbelasting: Dutch Road Tax Calculator  

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen)  

Motorrijtuigenbelasting is a Python library designed to calculate Dutch road taxes (motorrijtuigenbelasting, MRB) for passenger cars, motorcycles, and other vehicle types. It provides tools for determining taxes based on weight, fuel type, and provincial rates for 2014 to 2026. Rates are taken from the Wet op de motorrijtuigenbelasting 1994 as it applied on 1 January of each year, and the provincial opcenten from CBS StatLine table [80889ned](https://opendata.cbs.nl/statline/#/CBS/nl/dataset/80889ned/table).

## Features  

- Support for multiple energy sources (benzine, diesel, LPG, electric, etc.)  
- Handles tax calculations based on weight brackets and provincial multipliers.  
- Adjustable tax parameters for future tax years.  
- Lightweight and extensible for different vehicle types like cars and motorcycles.  

---

## Table of Contents  

1. [Installation](#installation)  
2. [Usage](#usage)  
   - [Example](#example)  
   - [Look up a kenteken](#look-up-a-kenteken)  
   - [Command line](#command-line)  
   - [Weight: massa rijklaar](#weight-massa-rijklaar)  
3. [Supported Vehicle Types](#supported-vehicle-types)  
4. [Contributing](#contributing)  
5. [License](#license)  

---

## Installation  

### Requirements  
- Python 3.10 or higher.  

```bash
pip install motorrijtuigenbelasting
```

or clone the repository and install it in editable mode with the development tools:  

```bash
git clone https://github.com/VitoMinheere/motorrijtuigenbelasting.git  
cd motorrijtuigenbelasting
pip install -e .[dev]
```

---

## Usage  

### Example  

Here’s how to use MRB-Py to calculate road tax for a passenger car:  

```python
from motorrijtuigenbelasting import Car, EnergySource

# Define car details, weight is the massa rijklaar from the RDW kentekenregister
car = Car(weight=1300, energy_source=EnergySource.BENZINE, manufacturing_year=2024)

# Calculate the tax per three months for Noord-Holland province in 2026
province = "noord-holland"
year = 2026
tax = car.calculate_total_tax(province=province, year=year)

print(f"Tax per three months for your car: €{tax}")
```

Provinces can be given as `Province.NOORD_HOLLAND`, `"noord-holland"`, `"Noord-Holland"` or `"Noord Holland"`. The supported years and provinces are available as `motorrijtuigenbelasting.SUPPORTED_YEARS` and `motorrijtuigenbelasting.PROVINCES`.

`manufacturing_year` and `year` also accept a `datetime.date`. Pass the datum eerste toelating from the kentekenregister to get the oldtimer rule right: a car first admitted on 15 November 1986 is tax free from 15 November 2026, not from 1 January 2026. A plain year counts as 1 January.

To see how the amount is built up, use `calculate_breakdown`:

```python
breakdown = car.calculate_breakdown(year=2026, province="noord-holland")
breakdown.components      # {"base": 116.05, "fuel_surcharge": 0.0}
breakdown.opcenten        # 56.79
breakdown.rule            # TaxRule.NORMAL, KWARTTARIEF or OLDTIMER
breakdown.per_three_months, breakdown.per_year
```

Use `calculate_yearly_tax` for the amount per year. For most vehicles that is four times the amount per three months. With the kwarttarief you pay once per year, so `calculate_total_tax` returns a quarter of the yearly amount, rounded down.

### Look up a kenteken  

`from_kenteken` reads the weight, fuel, first admission date, CO2 emission and particle emission from the [RDW open data](https://opendata.rdw.nl) (no API key needed) and returns a `Car` or `Motorcycle`:

```python
from motorrijtuigenbelasting import from_kenteken

car = from_kenteken("P-803-KL")
car.calculate_total_tax(year=2025, province="utrecht")
```

Plug-in hybrids count as their combustion fuel, and CO2 decides the low emission discount. The open data does not show whether an LPG installation is G3, so LPG cars are calculated without G3. Vans, trucks and campers raise `NotImplementedError` for now.

### Command line  

After installing, the `mrb` command (or `python -m motorrijtuigenbelasting`) calculates the tax without writing code:

```bash
mrb --weight 1300 --fuel benzine --province noord-holland --year 2026
# € 172 per three months

mrb --weight 820 --fuel diesel --diesel-particles --province utrecht --breakdown --yearly
mrb --vehicle motorcycle --province gelderland --first-use 1987 --yearly
mrb --kenteken P-803-KL --province utrecht
```

Run `mrb --help` for all options.

### Weight: massa rijklaar  

`Car(weight=...)` expects the **massa rijklaar** in kg, as shown in the RDW kentekenregister and asked for by the Belastingdienst calculator.

Since 1 July 2026 the law states its weight brackets in massa rijklaar. Before that it used eigen massa (massa ledig voertuig). The RDW sets massa rijklaar at eigen massa + 100 kg, so the tax for the same car did not change, only the weights in the tables moved up by 100 kg. This library stores the tables in eigen massa and subtracts 100 kg from the weight you pass in, so you can use massa rijklaar for every year.

The weight is rounded to the nearest 100 kg, where exactly 50 kg rounds down (art. 22 Wet MRB 1994).

If you only know the eigen massa, add 100 kg before passing it in.

---

## Supported Vehicle Types  

### Passenger Cars  
Supports fuel types like benzine, diesel, LPG, LPG G3, electric and hydrogen (waterstof) vehicles.  

### Oldtimer & kwarttarief ruling
Vehicles taken into use 40 or more years ago pay no tax. Vehicles taken into use before 1988 that are not yet 40 years old can use the kwarttarief (art. 84a): once per year the quarterly tariff of the previous year including opcenten, up to a maximum. For cars this only applies to benzine.

### Motorcycles
Rules for base tax and opcenten added. Added sources to the information in the docstring.

### Trailers and caravans (not taxed)
Aanhangwagens, opleggers and caravans do not pay motorrijtuigenbelasting. Art. 1 lid 1 Wet MRB 1994 only taxes a personenauto, bestelauto, motorrijwiel, vrachtauto or autobus. A trailer only matters for a vrachtauto: art. 25a has a higher tariff for trucks with a koppelinrichting (tow coupling). Heavy trucks of 12,000 kg or more also pay the separate belasting zware motorrijtuigen (Eurovignet), which is out of scope for this library.

### Upcoming changes
- **2027 tariffs** are added once the law version of 1 January 2027 is on wetten.overheid.nl and CBS has the 2027 opcenten (see [CONTRIBUTING.md](CONTRIBUTING.md)). Art. 23b already sets the share that zero emission cars pay: 70% in 2027 and 2028, 75% in 2029.
- **Betalen naar gebruik** (a per-kilometre charge) is planned around 2030 and may replace the motorrijtuigenbelasting for some or all vehicles. It is out of scope for this library until the law is final.

### Other
Other vehicles types are being worked on in the following order:
- Business Van
- Camper
- Trucks

---

## Contributing  

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for the development setup and how to add a new tax year. In short:  

1. Fork the repository.  
2. Create a new branch for your feature or bugfix.  
3. Write clear code and include tests.  
4. Submit a pull request with a detailed description of your changes.  

### Issues and Feature Requests

Found a bug or have an idea for a new feature? We’d love to hear from you!

    - Go to the Issues tab of the repository.
    - Click New Issue.
    - Provide a detailed description, including steps to reproduce the issue or a clear explanation of your feature idea.

### Running Tests  

Use `unittest` to run tests:  

```bash
python -m unittest discover -s tests
```

---

## License  

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.  

---

## Contact  

Feel free to reach out for support or feedback:  
- [VitoMinheere.com](https://vitominheere.com)
- [GitHub Profile](https://github.com/VitoMinheere)  
- [LinkedIn Profile](https://linkedin.com/in/vitominheere)  

