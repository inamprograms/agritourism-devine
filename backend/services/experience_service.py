# services/experience_service.py

class ExperienceService:
    """
    Handles farm experiences: CRUD, listing, enabling/disabling.
    """

    def __init__(self):
        # For now, store experiences in-memory (dict), replace later with DB
        self.experiences_db = {}  # {farm_id: [experience_dict, ...]}

    def save_experiences(self, farm_id, experiences):
        """
        Save generated experiences for a farm.
        """
        self.experiences_db[farm_id] = experiences
        return experiences

    def list_experiences(self, farm_id, level=None):
        """
        List experiences for a farm, optionally filtered by level.
        """
        all_exp = self.experiences_db.get(farm_id, [])
        if level:
            return [e for e in all_exp if e.get("level") == level]
        return all_exp

    def enable_experience(self, farm_id, experience_title):
        """
        Mark an experience as enabled (for farmer dashboard)
        """
        farm_exp = self.experiences_db.get(farm_id, [])
        for exp in farm_exp:
            if exp["title"] == experience_title:
                exp["enabled"] = True
                return exp
        return None

    def disable_experience(self, farm_id, experience_title):
        """
        Mark an experience as disabled
        """
        farm_exp = self.experiences_db.get(farm_id, [])
        for exp in farm_exp:
            if exp["title"] == experience_title:
                exp["enabled"] = False
                return exp
        return None
    
experience_service = ExperienceService()
