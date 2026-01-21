"""
carbon_rules.py

Purpose:
Rule-based carbon sequestration estimation for Agroforestry projects.
This file contains ONLY calculation rules.
No Flask, no API calls, no database logic.

Unit:
All outputs are in tCO2e (tonnes of CO2 equivalent)
"""

# -------------------------------------------------
# BASE CARBON SEQUESTRATION (Agroforestry)
# -------------------------------------------------
BASE_TCO2E_PER_HECTARE_PER_YEAR = 5.0


# -------------------------------------------------
# TREE DENSITY MULTIPLIERS
# -------------------------------------------------
TREE_DENSITY_MULTIPLIER = {
    "low": 0.8,
    "medium": 1.0,
    "high": 1.3
}


# -------------------------------------------------
# TREE AGE MULTIPLIERS
# -------------------------------------------------
TREE_AGE_MULTIPLIER = {
    "new": 0.5,
    "growing": 1.0,
    "mature": 1.2
}


# -------------------------------------------------
# FARM MANAGEMENT MULTIPLIERS
# -------------------------------------------------
ACTIVITY_LEVEL_MULTIPLIER = {
    "low": 0.9,
    "medium": 1.0,
    "high": 1.1
}


# -------------------------------------------------
# CORE CALCULATION FUNCTION
# -------------------------------------------------
def estimate_agroforestry_carbon(
    land_area_hectares: float,
    tree_density: str,
    tree_age: str,
    activity_level: str
) -> dict:

    density_factor = TREE_DENSITY_MULTIPLIER.get(tree_density, 1.0)
    age_factor = TREE_AGE_MULTIPLIER.get(tree_age, 1.0)
    activity_factor = ACTIVITY_LEVEL_MULTIPLIER.get(activity_level, 1.0)

    annual_tco2e = (
        land_area_hectares
        * BASE_TCO2E_PER_HECTARE_PER_YEAR
        * density_factor
        * age_factor
        * activity_factor
    )

    return {
        "annual_tco2e": round(annual_tco2e, 2),
        "five_year_tco2e": round(annual_tco2e * 5, 2),
        "ten_year_tco2e": round(annual_tco2e * 10, 2)
    }


# -------------------------------------------------
# TEST RUN
# -------------------------------------------------
if __name__ == "__main__":
    result = estimate_agroforestry_carbon(
        land_area_hectares=10,
        tree_density="medium",
        tree_age="growing",
        activity_level="high"
    )
    print(result)

