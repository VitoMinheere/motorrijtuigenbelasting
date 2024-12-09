# Motorrijtuigenbelasting: Dutch Road Tax Calculator  

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen)  

Motorrijtuigenbelasting is a Python library designed to calculate Dutch road taxes (motorrijtuigenbelasting, MRB) for passenger cars, motorcycles, and other vehicle types. It provides tools for determining taxes based on weight, fuel type, and provincial rates between 2015 and 2024. Future years will be added once the inflation numbers are in from the Belastingdienst.

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
3. [Supported Vehicle Types](#supported-vehicle-types)  
4. [Contributing](#contributing)  
5. [License](#license)  

---

## Installation  

### Requirements  
- Python 3.7 or higher.  

```bash
pip install motorrijtuigenbelasting
```

or clone the repository and install dependencies:  

```bash
git clone https://github.com/VitoMinheere/motorrijtuigenbelasting.git  
cd motorrijtuigenbelasting
pip install -r requirements.txt  
```

---

## Usage  

### Example  

Here’s how to use MRB-Py to calculate road tax for a passenger car:  

```python
from motorrijtuigenbelasting import Car, EnergySource

# Define car details
car = Car(weight=1200, energy_source=EnergySource.BENZINE, manufacturing_year=2024)

# Calculate total tax for Noord-Holland province in 2024
province = "noord-holland"
year = 2024
tax = car.calculate_total_tax(province=province, year=year)

print(f"Total tax for your car: €{tax}")
```

---

## Supported Vehicle Types  

### Passenger Cars  
Supports fuel types like benzine, diesel, LPG, LPG G3, and electric vehicles.  

### Oldtimer & kwarttarief ruling
Added the oldtimer & kwarttarief rulings and their maximum amounts.

### Motorcycles
Rules for base tax and opcenten added. Added sources to the information in the docstring.

### Other
Other vehicles types are being worked on in the following order:
- Diesel
- Benzine with low emissions
- Business Van
- Camper
- Trucks

---

## Contributing  

We welcome contributions! Please follow these steps:  

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

