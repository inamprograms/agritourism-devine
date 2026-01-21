from app.services.carbon.rules import calculate_carbon_credits
from app.services.carbon.climatiq_client import ClimatiqClient


class CarbonService:

    @staticmethod
    def calculate(
        land_area_hectares: float,
        tree_density: str,
        tree_age_years: int,
        management_practice: str,
        use_api: bool = True
    ):
        """
        Returns carbon credits estimation
        """

        rule_based = calculate_carbon_credits(
            land_area_hectares,
            tree_density,
            tree_age_years,
            management_practice
        )

        api_based = None
        if use_api:
            api_based = ClimatiqClient.estimate_agroforestry_carbon(
                land_area_hectares,
                years=1
            )

        return {
            "rule_based_credits": rule_based,
            "api_based_credits": api_based,
            "final_credits": api_based or rule_based
        }
