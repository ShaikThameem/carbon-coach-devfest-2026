
"""
Carbon Coach - Emission Calculation Engine

Emission factors are configurable estimates.
Each result reports its factor and source.
"""

# kg CO2e per passenger-kilometre.
# Illustrative factors for our initial MVP.
TRAVEL_FACTORS = {
    "bus": 0.029,
    "car": 0.20,
    "motorcycle": 0.13
}

# Illustrative Indian grid electricity factor.
ELECTRICITY_FACTOR = 0.710


def calculate_travel_emissions(mode: str, km: float):
    """Calculate emissions from passenger travel."""

    mode = mode.lower().strip()

    if mode not in TRAVEL_FACTORS:
        raise ValueError(
            "Unsupported mode. Choose bus, car or motorcycle."
        )

    if isinstance(km, bool) or not isinstance(km, (int, float)) or km < 0:
        raise ValueError("Distance must be a non-negative number.")

    factor = TRAVEL_FACTORS[mode]
    emissions = km * factor

    return {
        "category": "travel",
        "mode": mode,
        "distance_km": km,
        "emission_factor": factor,
        "emissions_kg_co2e": round(emissions, 4),
        "source": "Initial MVP travel factor configuration"
    }


def calculate_electricity_emissions(kwh: float):
    """Calculate emissions from electricity consumption."""

    if isinstance(kwh, bool) or not isinstance(kwh, (int, float)) or kwh < 0:
        raise ValueError("Electricity must be a non-negative number.")

    emissions = kwh * ELECTRICITY_FACTOR

    return {
        "category": "electricity",
        "consumption_kwh": kwh,
        "emission_factor": ELECTRICITY_FACTOR,
        "emissions_kg_co2e": round(emissions, 4),
        "source": "Initial MVP electricity factor configuration"
    }


def calculate_ac_emissions(hours: float, power_kw: float):
    """Calculate AC emissions when power and usage hours are known."""

    if (
        isinstance(hours, bool)
        or not isinstance(hours, (int, float))
        or hours < 0
    ):
        raise ValueError("Hours must be a non-negative number.")

    if (
        isinstance(power_kw, bool)
        or not isinstance(power_kw, (int, float))
        or power_kw <= 0
    ):
        raise ValueError("Power must be a positive number.")

    kwh = hours * power_kw

    result = calculate_electricity_emissions(kwh)

    result["appliance"] = "air_conditioner"
    result["hours"] = hours
    result["power_kw"] = power_kw

    return result
