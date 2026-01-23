"""
carbon_rules.py

Purpose:
IPCC-based carbon sequestration estimation for Agroforestry projects.
Based on IPCC 2019 Refinement to 2006 Guidelines.

Unit:
All outputs are in tCO2e (tonnes of CO2 equivalent)

References:
- IPCC 2019 Refinement, Volume 4, Chapter 4: Forest Land
- IPCC 2006 Guidelines, Volume 4: AFOLU
"""

# -------------------------------------------------
# IPCC-BASED CONSTANTS
# -------------------------------------------------

# Biomass Growth Rates (tonnes Carbon per hectare per year)
# Source: IPCC 2019, Table 4.9
BIOMASS_GROWTH_RATES = {
    "tropical": {
        "deciduous": 11.0,
        "coniferous": 8.0,
        "mixed": 9.5
    },
    "temperate": {
        "deciduous": 5.6,
        "coniferous": 4.2,
        "mixed": 4.9
    },
    "boreal": {
        "deciduous": 2.1,
        "coniferous": 1.8,
        "mixed": 2.0
    }
}

# Soil Organic Carbon Accumulation Rates (tonnes C/ha/year)
# Source: IPCC 2019, Table 5.5
SOIL_CARBON_RATES = {
    "sandy": 0.25,
    "loamy": 0.48,
    "clay": 0.69,
    "high_activity_clay": 0.80
}

# Root-to-Shoot Ratio (belowground biomass factor)
# Source: IPCC 2006, Table 4.4
ROOT_SHOOT_RATIO = {
    "tropical": 0.24,
    "temperate": 0.29,
    "boreal": 0.32
}

# -------------------------------------------------
# TREE DENSITY MULTIPLIERS (Project-Specific)
# -------------------------------------------------
TREE_DENSITY_MULTIPLIER = {
    "low": 0.7,      # < 100 trees/hectare
    "medium": 1.0,   # 100-400 trees/hectare
    "high": 1.4      # > 400 trees/hectare
}

# -------------------------------------------------
# TREE AGE GROWTH CURVE (Project-Specific)
# -------------------------------------------------
TREE_AGE_MULTIPLIER = {
    "new": 0.4,       # 0-5 years: slow establishment
    "growing": 1.0,   # 5-15 years: rapid growth
    "mature": 0.8     # 15+ years: growth slowing
}

# -------------------------------------------------
# MANAGEMENT PRACTICE MULTIPLIERS (Project-Specific)
# -------------------------------------------------
MANAGEMENT_MULTIPLIER = {
    "conventional": 0.85,
    "sustainable": 1.0,
    "regenerative": 1.15,
    "organic": 1.12,
    "intensive": 0.80,
    "minimal": 0.90,
    "moderate": 1.0,
    "advanced": 1.15
}

# Carbon to CO2 conversion factor
CARBON_TO_CO2E = 44 / 12  # = 3.67


# -------------------------------------------------
# IPCC-BASED CALCULATION FUNCTION
# -------------------------------------------------
def calculate_ipcc_carbon_sequestration(
    land_area_hectares: float,
    climate_zone: str,
    tree_species: str,
    soil_type: str,
    tree_density: str,
    tree_age_years: int,
    management_practice: str
) -> dict:
    """
    Calculate carbon sequestration using IPCC methodology.
    
    Args:
        land_area_hectares: Size of land in hectares
        climate_zone: "tropical", "temperate", or "boreal"
        tree_species: "deciduous", "coniferous", or "mixed"
        soil_type: "sandy", "loamy", "clay", or "high_activity_clay"
        tree_density: "low", "medium", or "high"
        tree_age_years: Age of trees in years
        management_practice: Farm management type
    
    Returns:
        Dictionary with detailed carbon calculations
    """
    
    # Validate inputs
    if climate_zone not in BIOMASS_GROWTH_RATES:
        climate_zone = "temperate"
    if tree_species not in BIOMASS_GROWTH_RATES[climate_zone]:
        tree_species = "mixed"
    if soil_type not in SOIL_CARBON_RATES:
        soil_type = "loamy"
    
    # STEP 1: Calculate Aboveground Biomass Carbon
    biomass_rate = BIOMASS_GROWTH_RATES[climate_zone][tree_species]
    
    # STEP 2: Add Belowground Biomass (Roots)
    root_ratio = ROOT_SHOOT_RATIO[climate_zone]
    total_biomass_rate = biomass_rate * (1 + root_ratio)
    
    # STEP 3: Add Soil Carbon Accumulation
    soil_rate = SOIL_CARBON_RATES[soil_type]
    total_carbon_rate = total_biomass_rate + soil_rate
    
    # STEP 4: Apply Project-Specific Multipliers
    density_factor = TREE_DENSITY_MULTIPLIER.get(tree_density, 1.0)
    
    # Age factor
    if tree_age_years < 5:
        age_factor = TREE_AGE_MULTIPLIER["new"]
    elif tree_age_years < 15:
        age_factor = TREE_AGE_MULTIPLIER["growing"]
    else:
        age_factor = TREE_AGE_MULTIPLIER["mature"]
    
    # Management factor
    management_factor = MANAGEMENT_MULTIPLIER.get(
        management_practice.lower(), 1.0
    )
    
    # STEP 5: Calculate Annual Carbon (tonnes C/year)
    annual_carbon = (
        land_area_hectares
        * total_carbon_rate
        * density_factor
        * age_factor
        * management_factor
    )
    
    # STEP 6: Convert Carbon to CO2e
    annual_tco2e = annual_carbon * CARBON_TO_CO2E
    
    # STEP 7: Calculate Multi-Year Projections
    five_year_tco2e = annual_tco2e * 5
    ten_year_tco2e = annual_tco2e * 10
    
    return {
        "annual_tco2e": round(annual_tco2e, 2),
        "five_year_tco2e": round(five_year_tco2e, 2),
        "ten_year_tco2e": round(ten_year_tco2e, 2),
        "methodology": "IPCC 2019",
        "breakdown": {
            "biomass_carbon_rate": round(total_biomass_rate, 2),
            "soil_carbon_rate": round(soil_rate, 2),
            "total_carbon_rate": round(total_carbon_rate, 2),
            "density_factor": density_factor,
            "age_factor": age_factor,
            "management_factor": management_factor
        }
    }


# -------------------------------------------------
# WRAPPER FUNCTION FOR API COMPATIBILITY
# -------------------------------------------------
def calculate_carbon_credits(
    land_area_hectares: float,
    tree_density: str,
    tree_age_years: int,
    management_practice: str,
    climate_zone: str = "temperate",
    tree_species: str = "mixed",
    soil_type: str = "loamy"
) -> dict:
    """
    Main function for carbon credit calculation.
    Uses IPCC methodology with sensible defaults.
    
    Args:
        land_area_hectares: Size of land in hectares (required)
        tree_density: "low", "medium", or "high" (required)
        tree_age_years: Age of trees in years (required)
        management_practice: Farm management type (required)
        climate_zone: "tropical", "temperate", or "boreal" (optional)
        tree_species: "deciduous", "coniferous", or "mixed" (optional)
        soil_type: "sandy", "loamy", "clay", "high_activity_clay" (optional)
    
    Returns:
        Dictionary with carbon credit estimates
    """
    
    return calculate_ipcc_carbon_sequestration(
        land_area_hectares=land_area_hectares,
        climate_zone=climate_zone,
        tree_species=tree_species,
        soil_type=soil_type,
        tree_density=tree_density,
        tree_age_years=tree_age_years,
        management_practice=management_practice
    )


# -------------------------------------------------
# SIMPLIFIED FUNCTION (Backward Compatible)
# -------------------------------------------------
def estimate_agroforestry_carbon(
    land_area_hectares: float,
    tree_density: str,
    tree_age: str,
    activity_level: str
) -> dict:
    """
    Simplified function for backward compatibility.
    Converts categorical inputs to numeric and calls main function.
    
    DEPRECATED: Use calculate_carbon_credits() for better accuracy
    """
    
    # Convert age category to years
    age_mapping = {
        "new": 3,
        "growing": 10,
        "mature": 20
    }
    tree_age_years = age_mapping.get(tree_age, 10)
    
    # Convert activity level to management practice
    management_mapping = {
        "low": "conventional",
        "medium": "sustainable",
        "high": "regenerative"
    }
    management_practice = management_mapping.get(activity_level, "sustainable")
    
    # Call main function with defaults
    return calculate_carbon_credits(
        land_area_hectares=land_area_hectares,
        tree_density=tree_density,
        tree_age_years=tree_age_years,
        management_practice=management_practice
    )


# -------------------------------------------------
# TEST RUN
# -------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("IPCC-BASED CARBON CREDIT CALCULATOR - TEST")
    print("=" * 60)
    print()
    
    # Test Case 1: Basic calculation
    print("Test 1: Temperate mixed forest, medium density")
    print("-" * 60)
    result1 = calculate_carbon_credits(
        land_area_hectares=10,
        tree_density="medium",
        tree_age_years=8,
        management_practice="sustainable"
    )
    print(f"Annual Credits: {result1['annual_tco2e']} tCO2e")
    print(f"5-Year Credits: {result1['five_year_tco2e']} tCO2e")
    print(f"10-Year Credits: {result1['ten_year_tco2e']} tCO2e")
    print()
    
    # Test Case 2: Tropical with high density
    print("Test 2: Tropical deciduous, high density, regenerative")
    print("-" * 60)
    result2 = calculate_carbon_credits(
        land_area_hectares=10,
        tree_density="high",
        tree_age_years=12,
        management_practice="regenerative",
        climate_zone="tropical",
        tree_species="deciduous",
        soil_type="clay"
    )
    print(f"Annual Credits: {result2['annual_tco2e']} tCO2e")
    print(f"5-Year Credits: {result2['five_year_tco2e']} tCO2e")
    print(f"Methodology: {result2['methodology']}")
    print()
    
    # Test Case 3: Backward compatibility
    print("Test 3: Backward compatible function")
    print("-" * 60)
    result3 = estimate_agroforestry_carbon(
        land_area_hectares=10,
        tree_density="medium",
        tree_age="growing",
        activity_level="high"
    )
    print(f"Annual Credits: {result3['annual_tco2e']} tCO2e")
    print()