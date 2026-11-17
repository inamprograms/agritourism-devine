# services/experience_service.py

from app.core.supabase import supabase
from app.schemas.experience import experience_schema
from postgrest import APIError

class ExperienceService:
    """
    Handles farm experiences: CRUD, listing, enabling/disabling using Supabase
    """

    def save_experiences(self, farm_id, experiences):
        """Update in place. Keep the farmer's enabled choice. Raises on error."""
        existing = (
            supabase.table("experiences").select("*").eq("farm_id", farm_id).execute().data or []
        )
        existing_by_title = {e["title"]: e for e in existing}
        new_titles = {e["title"] for e in experiences}

        to_insert, kept_enabled, updated = [], 0, 0
        for exp in experiences:
            row = experience_schema(farm_id, exp)
            old = existing_by_title.get(exp["title"])
            if old:
                row.pop("enabled", None)          # never overwrite the farmer's choice
                supabase.table("experiences").update(row).eq("id", old["id"]).execute()
                updated += 1
                if old.get("enabled"):
                    kept_enabled += 1
            else:
                to_insert.append(row)

        if to_insert:
            supabase.table("experiences").insert(to_insert).execute()

        removed = [e for t, e in existing_by_title.items() if t not in new_titles]
        if removed:
            supabase.table("experiences").delete().in_("id", [e["id"] for e in removed]).execute()

        return {
            "kept_enabled": kept_enabled,
            "updated": updated,
            "added": len(to_insert),
            "removed": len(removed),
            "removed_enabled": sum(1 for e in removed if e.get("enabled")),
        }

    def list_experiences(self, farm_id, level=None, enabled_only=None):
        """
        List experiences for a farm, optionally filtered by level or enabled status.
        """
        query = supabase.table("experiences").select("*").eq("farm_id", farm_id)

        if level is not None:
            query = query.eq("level", level)

        if enabled_only is not None:
            query = query.eq("enabled", enabled_only)

        response = query.execute()
        return response.data or []

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
        res = (
            supabase
            .table("experiences")
            .select("*")
            .eq("id", experience_id)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

# Singleton instance
experience_service = ExperienceService()
