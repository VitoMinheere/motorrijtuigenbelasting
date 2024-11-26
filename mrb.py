from taxes import EnergySource, calculate_tax
from taxes import calculate_tax as calculate_tax_refactor

YEAR = 2024

# TODO Add date of creation and co2 levels
car = {
    "weight": 1200,
    "energy_source": EnergySource.BENZINE,
    "province": "noord-holland",
    "year": YEAR,
}


result = calculate_tax(
    car["energy_source"], car["weight"], car["province"], car["year"]
)
print(f"Old = {result}")

result_new = calculate_tax_refactor(
    energy_source=EnergySource.BENZINE, weight=1200, province="noord-holland", year=YEAR
)

print(f"Refactor = {result_new}")
