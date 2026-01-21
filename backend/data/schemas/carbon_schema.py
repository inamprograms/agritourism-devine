# data/schemas/carbon_schema.py

def carbon_input_schema(data: dict) -> dict:
    """
    Validates and normalizes carbon estimation input.
    """

    if "land_size_hectares" not in data:
        raise ValueError("land_size_hectares is required")

    return {
        "land_size_hectares": float(data["land_size_hectares"]),
        "tree_density": data.get("tree_density", "medium"),
        "tree_age": data.get("tree_age", "growing"),
        "activity_level": data.get("activity_level", "medium"),
    }


def carbon_output_schema(result: dict) -> dict:
    """
    Formats carbon estimation output.
    """

    return {
        "annual_tco2e": result.get("annual_tco2e"),
        "five_year_tco2e": result.get("five_year_tco2e"),
        "ten_year_tco2e": result.get("ten_year_tco2e"),
    }
