import os
import requests

CLIMATIQ_API_URL = "https://api.climatiq.io/estimate"
CLIMATIQ_API_KEY = os.getenv("CLIMATIQ_API_KEY")


class ClimatiqClient:
    @staticmethod
    def estimate_agroforestry_carbon(
        land_area_hectares: float,
        years: int = 1
    ) -> float:
        """
        Returns carbon sequestration in tons CO2e
        """

        if not CLIMATIQ_API_KEY:
            raise ValueError("CLIMATIQ_API_KEY not set in environment")

        headers = {
            "Authorization": f"Bearer {CLIMATIQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "emission_factor": {
                # Agroforestry / forestry factor (industry standard)
                "activity_id": "forestry-forest-management",
                "data_version": "^1"
            },
            "parameters": {
                "area": land_area_hectares,
                "area_unit": "ha",
                "time": years,
                "time_unit": "year"
            }
        }

        response = requests.post(
            CLIMATIQ_API_URL,
            json=payload,
            headers=headers,
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        # 1 credit = 1 ton CO2e
        return round(data["co2e"], 2)
