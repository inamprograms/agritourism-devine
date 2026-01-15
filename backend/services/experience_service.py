# services/experience_service.py

from data.supabase_client import supabase
from data.schemas.experience import experience_schema

class ExperienceService:
    """
    Handles farm experiences: CRUD, listing, enabling/disabling using Supabase
    """

    def save_experiences(self, farm_id, experiences):
        """
        Save generated experiences for a farm to Supabase
        """
        # Delete existing experiences for farm first (optional, to avoid duplicates)
        supabase.table("experiences").delete().eq("farm_id", farm_id).execute()

        # Insert new experiences
        data_to_insert = [experience_schema(farm_id, exp) for exp in experiences]
        supabase.table("experiences").insert(data_to_insert).execute()
        return experiences

    def list_experiences(self, farm_id, level=None):
        """
        List experiences for a farm, optionally filtered by level.
        """
        query = supabase.table("experiences").select("*").eq("farm_id", farm_id)
        if level:
            query = query.eq("level", level)
        response = query.execute()
        return response.data or []

    def enable_experience(self, farm_id, experience_title):
        """
        Mark an experience as enabled (for farmer dashboard)
        """
        supabase.table("experiences")\
            .update({"enabled": True})\
            .eq("farm_id", farm_id)\
            .eq("title", experience_title)\
            .execute()
        return self.list_experiences(farm_id, level=None)

    def disable_experience(self, farm_id, experience_title):
        """
        Mark an experience as disabled
        """
        supabase.table("experiences")\
            .update({"enabled": False})\
            .eq("farm_id", farm_id)\
            .eq("title", experience_title)\
            .execute()
        return self.list_experiences(farm_id, level=None)

# Singleton instance
experience_service = ExperienceService()
