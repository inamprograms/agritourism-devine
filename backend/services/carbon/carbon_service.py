"""
carbon_service.py

Purpose:
Service layer for carbon credit estimation.
Pure rule-based calculation using IPCC methodology.
No external API dependencies.
"""

from services.carbon.carbon_rules import calculate_carbon_credits


class CarbonService:
    """
    Carbon credit estimation service.
    Uses IPCC-based calculation rules only.
    """
    
    @staticmethod
    def calculate(
        land_area_hectares: float,
        tree_density: str,
        tree_age_years: int,
        management_practice: str,
        climate_zone: str = "temperate",
        tree_species: str = "mixed",
        soil_type: str = "loamy"
    ) -> dict:
        """
        Calculate carbon credits using IPCC methodology.
        
        Args:
            land_area_hectares: Size of land in hectares
            tree_density: "low", "medium", or "high"
            tree_age_years: Age of trees in years
            management_practice: "conventional", "sustainable", "regenerative", etc.
            climate_zone: "tropical", "temperate", or "boreal" (default: temperate)
            tree_species: "deciduous", "coniferous", or "mixed" (default: mixed)
            soil_type: "sandy", "loamy", "clay", "high_activity_clay" (default: loamy)
        
        Returns:
            Dictionary containing:
                - credits: Full calculation results
                - status: "success" or "failed"
                - error: Error message (if failed)
        """
        
        try:
            # Calculate using IPCC-based rules
            credits = calculate_carbon_credits(
                land_area_hectares=land_area_hectares,
                tree_density=tree_density,
                tree_age_years=tree_age_years,
                management_practice=management_practice,
                climate_zone=climate_zone,
                tree_species=tree_species,
                soil_type=soil_type
            )
            
            return {
                "credits": credits,
                "status": "success",
                "calculation_method": "IPCC 2019 Guidelines"
            }
            
        except Exception as e:
            return {
                "credits": None,
                "status": "failed",
                "error": str(e)
            }
    
    
    @staticmethod
    def calculate_simple(
        land_area_hectares: float,
        tree_density: str,
        tree_age_years: int,
        management_practice: str
    ) -> dict:
        """
        Simplified calculation with default parameters.
        Uses temperate climate, mixed species, loamy soil.
        
        Args:
            land_area_hectares: Size of land in hectares
            tree_density: "low", "medium", or "high"
            tree_age_years: Age of trees in years
            management_practice: Farm management type
        
        Returns:
            Dictionary with calculation results
        """
        
        return CarbonService.calculate(
            land_area_hectares=land_area_hectares,
            tree_density=tree_density,
            tree_age_years=tree_age_years,
            management_practice=management_practice,
            climate_zone="temperate",
            tree_species="mixed",
            soil_type="loamy"
        )
    
    
    @staticmethod
    def get_available_options() -> dict:
        """
        Return all available input options for the calculator.
        Useful for API documentation and form validation.
        """
        
        return {
            "tree_density": ["low", "medium", "high"],
            "climate_zone": ["tropical", "temperate", "boreal"],
            "tree_species": ["deciduous", "coniferous", "mixed"],
            "soil_type": ["sandy", "loamy", "clay", "high_activity_clay"],
            "management_practice": [
                "conventional",
                "sustainable",
                "regenerative",
                "organic",
                "intensive",
                "minimal",
                "moderate",
                "advanced"
            ]
        }
    
    
    @staticmethod
    def validate_inputs(
        land_area_hectares: float,
        tree_density: str,
        tree_age_years: int,
        management_practice: str,
        climate_zone: str = None,
        tree_species: str = None,
        soil_type: str = None
    ) -> dict:
        """
        Validate user inputs before calculation.
        
        Returns:
            Dictionary with 'valid' boolean and 'errors' list
        """
        
        errors = []
        
        # Validate land area
        if land_area_hectares <= 0:
            errors.append("Land area must be greater than 0")
        if land_area_hectares > 100000:
            errors.append("Land area seems unrealistically large (> 100,000 ha)")
        
        # Validate tree density
        if tree_density not in ["low", "medium", "high"]:
            errors.append(f"Invalid tree_density: {tree_density}")
        
        # Validate tree age
        if tree_age_years < 0:
            errors.append("Tree age cannot be negative")
        if tree_age_years > 200:
            errors.append("Tree age seems unrealistic (> 200 years)")
        
        # Validate optional parameters
        if climate_zone and climate_zone not in ["tropical", "temperate", "boreal"]:
            errors.append(f"Invalid climate_zone: {climate_zone}")
        
        if tree_species and tree_species not in ["deciduous", "coniferous", "mixed"]:
            errors.append(f"Invalid tree_species: {tree_species}")
        
        if soil_type and soil_type not in ["sandy", "loamy", "clay", "high_activity_clay"]:
            errors.append(f"Invalid soil_type: {soil_type}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


# -------------------------------------------------
# TEST RUN
# -------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("CARBON SERVICE - TEST")
    print("=" * 60)
    print()
    
    # Test 1: Simple calculation
    print("Test 1: Simple calculation")
    print("-" * 60)
    result1 = CarbonService.calculate_simple(
        land_area_hectares=10,
        tree_density="high",
        tree_age_years=12,
        management_practice="regenerative"
    )
    
    if result1["status"] == "success":
        credits = result1["credits"]
        print(f"✅ Status: {result1['status']}")
        print(f"Annual Credits: {credits['annual_tco2e']} tCO2e")
        print(f"5-Year Credits: {credits['five_year_tco2e']} tCO2e")
        print(f"10-Year Credits: {credits['ten_year_tco2e']} tCO2e")
    else:
        print(f"❌ Error: {result1['error']}")
    print()
    
    # Test 2: Full calculation with all parameters
    print("Test 2: Full calculation (tropical)")
    print("-" * 60)
    result2 = CarbonService.calculate(
        land_area_hectares=25,
        tree_density="high",
        tree_age_years=8,
        management_practice="organic",
        climate_zone="tropical",
        tree_species="deciduous",
        soil_type="clay"
    )
    
    if result2["status"] == "success":
        credits = result2["credits"]
        print(f"✅ Method: {result2['calculation_method']}")
        print(f"Annual Credits: {credits['annual_tco2e']} tCO2e")
        print(f"Methodology: {credits['methodology']}")
    print()
    
    # Test 3: Input validation
    print("Test 3: Input validation")
    print("-" * 60)
    validation = CarbonService.validate_inputs(
        land_area_hectares=10,
        tree_density="medium",
        tree_age_years=15,
        management_practice="sustainable"
    )
    print(f"Valid: {validation['valid']}")
    if not validation['valid']:
        print(f"Errors: {validation['errors']}")
    else:
        print("✅ All inputs are valid")
    print()
    
    # Test 4: Get available options
    print("Test 4: Available options")
    print("-" * 60)
    options = CarbonService.get_available_options()
    for key, values in options.items():
        print(f"{key}: {', '.join(values)}")