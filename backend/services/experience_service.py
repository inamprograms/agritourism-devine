# services/experience_service.py

from data.supabase_client import supabase
from data.schemas.experience import experience_schema
from postgrest import APIError

class ExperienceService:
    """
    Handles farm experiences: CRUD, listing, enabling/disabling using Supabase
    """

    def save_experiences(self, farm_id, experiences):
        """
        Save generated experiences for a farm to Supabase
        """
        try:
            # Delete existing experiences for farm first (optional, to avoid duplicates)
            supabase.table("experiences").delete().eq("farm_id", farm_id).execute()

            # Insert new experiences
            data_to_insert = [experience_schema(farm_id, exp) for exp in experiences]
            supabase.table("experiences").insert(data_to_insert).execute()
            return data_to_insert
        
        except APIError as e:
            return {"error": str(e)}, 500

    def list_experiences(self, farm_id, level=None, enabled_only=None):
        """
        List experiences for a farm, optionally filtered by level or enabled status.
        """
        try:
            query = supabase.table("experiences").select("*").eq("farm_id", farm_id)
            
            if level is not None:
                query = query.eq("level", level)

            if enabled_only is not None:
                query = query.eq("enabled", enabled_only)
                
            response = query.execute()
            return response.data or []
        
        except APIError as e:
            return {"error": str(e)}, 500

    def enable_experience(self, farm_id, experience_title):
        """
        Mark an experience as enabled (for farmer dashboard)
        """      
        try:
            update_res = (
                supabase
                .table("experiences")
                .update({"enabled": True})
                .eq("farm_id", farm_id)
                .eq("title", experience_title)
                .execute()
            )

            if not update_res.data:
                return None

            # fetch updated experience
            fetch_res = (
                supabase
                .table("experiences")
                .select("*")
                .eq("farm_id", farm_id)
                .eq("title", experience_title)
                .execute()
            )
            return fetch_res.data[0] if fetch_res.data else None

        except APIError as e:
            raise e
        
    def disable_experience(self, farm_id, experience_title):
        """
        Mark an experience as disabled
        """
        try:
            update_res = (
                supabase
                .table("experiences")
                .update({"enabled": False})
                .eq("farm_id", farm_id)
                .eq("title", experience_title)
                .execute()
            )

            if not update_res.data:
                return None

            fetch_res = (
                supabase
                .table("experiences")
                .select("*")
                .eq("farm_id", farm_id)
                .eq("title", experience_title)
                .execute()
            )

            return fetch_res.data[0] if fetch_res.data else None

        except APIError as e:
            raise e
        
    def get_experience_by_id(self, experience_id):
        """
        Fetch a single experience by its ID.
        Used by AI explanation layer.
        """
        try:
            res = (
                supabase
                .table("experiences")
                .select("*")
                .eq("id", experience_id)
                .single()
                .execute()
            )
            return res.data

        except APIError:
            return None

# Singleton instance
experience_service = ExperienceService()
