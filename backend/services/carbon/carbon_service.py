from app.services.carbon.rules import calculate_carbon_credits
from app.services.carbon.climatiq_client import ClimatiqClient


class CarbonService:
    @staticmethod
    def calculate(
        land_area_hectares: float,
        tree_density: str = "medium",
        tree_age_years: str = "growing",
        management_practice: str = "medium",
        use_api: bool = True
    ) -> dict:
        """
        Calculates carbon credits using rule-based logic
        and optionally Climatiq API.
        """

        # Rule-based calculation (always available)
        rule_based_credits = calculate_carbon_credits(
            land_area_hectares=land_area_hectares,
            tree_density=tree_density,
            tree_age_years=tree_age_years,
            management_practice=management_practice
        )

        api_credits = None
        api_error = None

        # API-based calculation (optional)
        if use_api:
            try:
                api_credits = ClimatiqClient.estimate_agroforestry_carbon(
                    land_area_hectares=land_area_hectares
                )
            except Exception as e:
                api_error = str(e)

        return {
            "rule_based_credits": rule_based_credits,
            "api_based_credits": api_credits,
            "api_error": api_error
        }
