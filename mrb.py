from taxes import EnergySource, calculate_tax

YEAR = 2024

# TODO Add date of creation and co2 levels
car = {
    "weight": 1300,
    "energy_source": EnergySource.BENZINE,
    "province": "friesland",
    "year": YEAR
}


result = calculate_tax(
    car["energy_source"],
    car["weight"],
    car["province"],
    car["year"]
)

print(car)
print(result)