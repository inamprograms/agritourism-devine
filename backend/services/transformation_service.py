# services/transformation_service.py

class TransformationService:
    """
    Rule-based farm -> tourism transformation engine (v1)
    """

    LEVEL_1_FREE = ["Farm visit", "Nature walk", "Educational tour"]
    LEVEL_1_PAID = ["Animal feeding", "Milking cow"]

    LEVEL_2_PAID = ["Entry ticket", "Tea / milk / fruit sales"]
    LEVEL_3_PAID = ["Weekend experience", "School visits", "Farm stay", "Packages"]

    def __init__(self):
        pass

    def generate_experiences(self, farm_data):
        """
        farm_data: dict with farm info + assets
        returns list of experience dicts
        """
        experiences = []

        # --- Level 1: Zero / Low cost ---
        for activity in self.LEVEL_1_FREE:
            experiences.append({
                "title": activity,
                "type": "activity" if "tour" in activity.lower() or "walk" in activity.lower() else "nature",
                "level": 1,
                "monetization": "free"
            })

        for activity in self.LEVEL_1_PAID:
            # Only add if farm has relevant assets
            if "cow" in farm_data.get("animals", []):
                experiences.append({
                    "title": activity,
                    "type": "activity",
                    "level": 1,
                    "monetization": "paid"
                })

        # --- Level 2: Small monetization ---
        for activity in self.LEVEL_2_PAID:
            experiences.append({
                "title": activity,
                "type": "activity",
                "level": 2,
                "monetization": "paid"
            })

        # --- Level 3: Growth ---
        for activity in self.LEVEL_3_PAID:
            experiences.append({
                "title": activity,
                "type": "activity",
                "level": 3,
                "monetization": "paid"
            })

        return experiences
