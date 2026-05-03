from app.utils.supabase_client import get_admin_supabase_client

class FarmerService:

    def _get_or_create_farmer(self, admin, user_id: str) -> str:
        """
        Internal helper: get existing farmer for user or create one.
        Returns farmer_id. Uses actual user name from profiles table.
        """
        farmer_res = (
            admin.table("farmers")
            .select("id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )

        if farmer_res.data:
            return farmer_res.data[0]["id"]

        profile_res = (
            admin.table("profiles")
            .select("full_name")
            .eq("id", user_id)
            .single()
            .execute()
        )
        full_name = profile_res.data.get("full_name") if profile_res.data else None
        new_farmer = (
            admin.table("farmers")
            .insert({"user_id": user_id, "name": full_name or "Farmer"})
            .execute()
        )
        return new_farmer.data[0]["id"]
        
    def create_farm(self, user_id: str, name: str, farm_type: str, size_category: str = "medium", 
                location: str = None, description: str = None,
                crops: list = None, animals: dict = None, existing_trees: list = None,
                water_source: str = None, structures: list = None, road_access: str = None,
                distance_from_city_km: int = None, scenic_features: list = None) -> dict:
        """
        Explicitly create a new farm for this user.
        Called when user clicks 'Create Farm' button.
        A user can call this as many times as they want.
        """
        admin = get_admin_supabase_client()
        farmer_id = self._get_or_create_farmer(admin, user_id)

        new_farm = (
            admin.table("farms")
            .insert({
                "farmer_id": farmer_id,
                "name": name,
                "farm_type": farm_type,
                "size_category": size_category,
                "location": location,
                "description": description,
                "crops": crops or [],
                "animals": animals or {},
                "existing_trees": existing_trees or [],
                "water_source": water_source,
                "structures": structures or [],
                "road_access": road_access,
                "distance_from_city_km": distance_from_city_km,
                "scenic_features": scenic_features or [],
            })
            .execute()
        )
        return new_farm.data[0]

    def get_farms_for_user(self, user_id: str) -> list:
        """
        Returns all farms belonging to this user, ordered by creation date.
        """
        admin = get_admin_supabase_client()

        farmer_res = (
            admin.table("farmers")
            .select("id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not farmer_res.data:
            return []

        farmer_id = farmer_res.data[0]["id"]

        farms = (
            admin.table("farms")
            .select("*")
            .eq("farmer_id", farmer_id)
            .order("created_at", desc=False)
            .execute()
        )
        return farms.data or []

    def get_farm_by_id(self, farm_id: str) -> dict | None:
        """Returns a single farm by id."""
        admin = get_admin_supabase_client()
        res = (
            admin.table("farms")
            .select("*")
            .eq("id", farm_id)
            .single()
            .execute()
        )
        return res.data if res.data else None
    
    def update_farm(self, farm_id: str, data: dict) -> dict | None:
        """Updates farm details. Only updates fields that are provided."""
        admin = get_admin_supabase_client()
        res = (
            admin.table("farms")
            .update(data)
            .eq("id", farm_id)
            .execute()
        )
        return res.data[0] if res.data else None

    def get_farmer_for_user(self, user_id: str) -> dict | None:
        """Returns farmer record for this user."""
        admin = get_admin_supabase_client()
        res = (
            admin.table("farmers")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None
    
    def update_farmer_profile(self, user_id: str, data: dict) -> dict | None:
        """Updates farmer profile fields like budget, goals, timeline etc."""
        admin = get_admin_supabase_client()
        
        farmer_res = (
            admin.table("farmers")
            .select("id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not farmer_res.data:
            return None

        farmer_id = farmer_res.data[0]["id"]
        res = (
            admin.table("farmers")
            .update(data)
            .eq("id", farmer_id)
            .execute()
        )
        return res.data[0] if res.data else None

    def verify_farm_ownership(self, farm_id: str, user_id: str) -> bool:
        """
        Security check: confirms this farm belongs to this user.
        Call this before any write operation on a specific farm.
        """
        admin = get_admin_supabase_client()

        farmer_res = (
            admin.table("farmers")
            .select("id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not farmer_res.data:
            return False

        farmer_id = farmer_res.data[0]["id"]

        farm_res = (
            admin.table("farms")
            .select("id")
            .eq("id", farm_id)
            .eq("farmer_id", farmer_id)
            .limit(1)
            .execute()
        )
        return bool(farm_res.data)


farmer_service = FarmerService()