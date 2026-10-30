
from emissions import (
    calculate_travel_emissions,
    calculate_electricity_emissions,
    calculate_ac_emissions
)

print("TEST 1: BUS TRAVEL")
print(calculate_travel_emissions("bus", 12))

print("\nTEST 2: ELECTRICITY")
print(calculate_electricity_emissions(4))

print("\nTEST 3: AC USAGE")
print(calculate_ac_emissions(4, 1.5))
