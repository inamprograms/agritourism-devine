# data/schemas/carbon_schema.py

def carbon_input_schema(data: dict) -> dict:
    """
    Validates and normalizes carbon estimation input.
    Updated to match new IPCC-based calculation parameters.
    """

    # Required fields
    if "land_area_hectares" not in data:
        raise ValueError("land_area_hectares is required")
    
    if "tree_density" not in data:
        raise ValueError("tree_density is required")
    
    if "tree_age_years" not in data:
        raise ValueError("tree_age_years is required")
    
    if "management_practice" not in data:
        raise ValueError("management_practice is required")

    # Validate tree_density
    valid_densities = ["low", "medium", "high"]
    if data["tree_density"] not in valid_densities:
        raise ValueError(f"tree_density must be one of {valid_densities}")

    # Validate tree_age_years
    tree_age = int(data["tree_age_years"])
    if tree_age < 0:
        raise ValueError("tree_age_years cannot be negative")
    if tree_age > 200:
        raise ValueError("tree_age_years seems unrealistic (> 200)")

    # Build validated input
    validated = {
        "land_area_hectares": float(data["land_area_hectares"]),
        "tree_density": data["tree_density"],
        "tree_age_years": tree_age,
        "management_practice": data["management_practice"],
    }

    # Optional fields with defaults
    if "climate_zone" in data:
        valid_zones = ["tropical", "temperate", "boreal"]
        if data["climate_zone"] in valid_zones:
            validated["climate_zone"] = data["climate_zone"]
    
    if "tree_species" in data:
        valid_species = ["deciduous", "coniferous", "mixed"]
        if data["tree_species"] in valid_species:
            validated["tree_species"] = data["tree_species"]
    
    if "soil_type" in data:
        valid_soils = ["sandy", "loamy", "clay", "high_activity_clay"]
        if data["soil_type"] in valid_soils:
            validated["soil_type"] = data["soil_type"]

    return validated


def carbon_output_schema(result: dict) -> dict:
    """
    Formats carbon estimation output.
    Updated to include IPCC methodology details.
    """

    credits = result.get("credits", {})
    
    output = {
        "status": result.get("status"),
        "calculation_method": result.get("calculation_method"),
        "annual_tco2e": credits.get("annual_tco2e"),
        "five_year_tco2e": credits.get("five_year_tco2e"),
        "ten_year_tco2e": credits.get("ten_year_tco2e"),
        "methodology": credits.get("methodology")
    }

    # Include breakdown if available
    if "breakdown" in credits:
        output["breakdown"] = credits["breakdown"]

    return output